import { ConstraintSense, EPSILON, ObjectiveSense, OptimizerStatus } from './types';
import type {
  Constraint,
  LPResult,
  Objective,
  Solution,
} from './types';

// ── Matrix utilities ──────────────────────────────────────────────────────────

type Matrix = number[][];

/** Multiplies every element in a tableau row by a scalar (elementary row operation). */
function rowScale(m: Matrix, row: number, factor: number): void {
  for (let j = 0; j < m[row].length; j++) m[row][j] *= factor;
}

/** Adds `factor` times `source` to `target` (elementary row operation). */
function rowAdd(m: Matrix, target: number, source: number, factor: number): void {
  for (let j = 0; j < m[target].length; j++) m[target][j] += factor * m[source][j];
}

// ── SimplexTableau ────────────────────────────────────────────────────────────

/**
 * Column layout of the canonical tableau (FIXED_COLS = 5):
 *
 *   col 0      : RHS (right-hand side / constant term)
 *   col 1 / 2  : x⁺ / x⁻  (positive and negative parts of x)
 *   col 3 / 4  : y⁺ / y⁻  (positive and negative parts of y)
 *   col 5+     : slack variables (one per canonical constraint row)
 *
 * Splitting x and y into positive/negative parts ensures all decision variables
 * are non-negative, which is required by the standard simplex algorithm.
 * The objective row is always the last row of the tableau.
 */
const FIXED_COLS = 5; // RHS + x⁺ x⁻ + y⁺ y⁻

class SimplexTableau {
  tableau: Matrix;
  numConstraints: number;

  constructor(tableau: Matrix, numConstraints: number) {
    this.tableau = tableau;
    this.numConstraints = numConstraints;
  }

  /**
   * Builds the objective row in canonical (minimisation) form.
   * For MAX c·z: negate the objective so that min −c·z ≡ max c·z.
   * Layout: [0, −cx, cx, −cy, cy] for MAX; [0, cx, −cx, cy, −cy] for MIN.
   */
  private static canonicalObjectiveRow(obj: Objective): number[] {
    const { coeffX: cx, coeffY: cy, sense } = obj;
    return sense === ObjectiveSense.MAX
      ? [0, -cx,  cx, -cy,  cy]
      : [0,  cx, -cx,  cy, -cy];
  }

  /**
   * Converts a constraint into one or two canonical (≤-form) rows.
   * A ≥ constraint is multiplied by −1. An = constraint produces both a ≤ and
   * a ≥ row so that equality is enforced from both sides.
   */
  private static canonicalConstraintRows(c: Constraint): number[][] {
    const { coeffX: cx, coeffY: cy, rhs } = c;
    const le = [ rhs,  cx, -cx,  cy, -cy];
    const ge = [-rhs, -cx,  cx, -cy,  cy];
    switch (c.sense) {
      case ConstraintSense.LE: return [le];
      case ConstraintSense.GE: return [ge];
      case ConstraintSense.EQ: return [le, ge];
      default:                 return [le];
    }
  }

  /**
   * Builds the initial tableau from an objective and a list of constraints.
   * Appends one slack variable per canonical constraint row, giving each row
   * an identity column so the slack variables form the initial basis.
   */
  static canonicalFrom(obj: Objective, constraints: Constraint[]): SimplexTableau {
    const objRow = SimplexTableau.canonicalObjectiveRow(obj);

    if (constraints.length === 0) {
      return new SimplexTableau([[...objRow]], 0);
    }

    const cRows: number[][] = [];
    for (const c of constraints) cRows.push(...SimplexTableau.canonicalConstraintRows(c));

    const n = cRows.length;
    const block: Matrix = cRows.map((row, i) => {
      const slacks = new Array<number>(n).fill(0);
      slacks[i] = 1;
      return [...row, ...slacks];
    });

    const fullObjRow = [...objRow, ...new Array<number>(n).fill(0)];
    return new SimplexTableau([...block, fullObjRow], n);
  }

  /** Returns the initial basis: the slack variable column for each constraint row. */
  getInitialBasis(): number[] {
    return Array.from({ length: this.numConstraints }, (_, i) => FIXED_COLS + i);
  }

  /** Returns true if all RHS values are non-negative — if so, phase 1 is not needed. */
  isRhsAllNonNegative(): boolean {
    for (let i = 0; i < this.numConstraints; i++) {
      if (this.tableau[i][0] < -EPSILON) return false;
    }
    return true;
  }

  /** Returns the column index of the most negative reduced cost (pivot column selection). */
  getIndexSmallestCost(): number {
    const obj = this.tableau[this.tableau.length - 1];
    let minIdx = 1;
    for (let j = 2; j < obj.length; j++) {
      if (obj[j] < obj[minIdx]) minIdx = j;
    }
    return minIdx;
  }

  getObjectiveRow(): number[]  { return this.tableau[this.tableau.length - 1]; }
  getObjectiveValue(): number  { return this.tableau[this.tableau.length - 1][0]; }
  getRhs(row: number): number  { return this.tableau[row][0]; }
  numRows(): number            { return this.tableau.length; }
  numCols(): number            { return this.tableau[0]?.length ?? 0; }

  /**
   * Returns the row index that minimises RHS/entry for column `col` (minimum ratio test).
   * Only rows with a positive entry in `col` are considered. Returns null if none exist,
   * indicating the problem is unbounded in that direction.
   */
  minRatio(col: number): number | null {
    let minR = Infinity;
    let minRow: number | null = null;
    for (let row = 0; row < this.numConstraints; row++) {
      const entry = this.tableau[row][col];
      if (entry > EPSILON) {
        const ratio = this.getRhs(row) / entry;
        if (ratio < minR) { minR = ratio; minRow = row; }
      }
    }
    return minRow;
  }

  /** Eliminates the pivot column entry in `currRow` using the already-scaled `pivotRow`. */
  pivotRowOp(currRow: number, pivotRow: number, pivotCol: number): void {
    rowAdd(this.tableau, currRow, pivotRow, -this.tableau[currRow][pivotCol]);
  }

  /** Scales `row` so the pivot element is 1, then eliminates that column in all other rows. */
  pivot(row: number, col: number): void {
    rowScale(this.tableau, row, 1 / this.tableau[row][col]);
    for (let i = 0; i < this.tableau.length; i++) {
      if (i !== row) this.pivotRowOp(i, row, col);
    }
  }

  // ── Phase 1 helpers ─────────────────────────────────────────────────────────

  /** Appends a zeroed objective row for the phase 1 auxiliary problem. */
  phase1AddObjectiveRow(row: number[]): void {
    this.tableau.push([...row]);
  }

  /**
   * Adds an artificial variable for the given row (used when its RHS is negative).
   * Negates the row first (making the RHS positive), appends a column with a 1 in
   * that row and in the phase 1 objective row, and sets up the objective coefficient.
   */
  phase1AddArtificialVar(row: number): void {
    this.tableau[row] = this.tableau[row].map(v => -v);
    const lastRow = this.tableau.length - 1;
    for (let i = 0; i < this.tableau.length; i++) {
      this.tableau[i].push(i === row || i === lastRow ? 1 : 0);
    }
  }

  phase1DropObjectiveRow(): void { this.tableau.pop(); }

  phase1DropRow(row: number): void {
    this.tableau.splice(row, 1);
    this.numConstraints--;
  }

  /**
   * Cleans up after phase 1: removes the auxiliary objective row, removes any
   * degenerate rows still in the basis on artificial variables (or re-pivots them
   * onto a non-artificial column if possible), and strips all artificial variable
   * columns from the tableau. Returns the updated basis with remapped column indices.
   */
  phase1Teardown(artificialVars: number[], basis: number[]): number[] {
    this.phase1DropObjectiveRow();

    const artSet  = new Set(artificialVars);
    const firstArt = Math.min(...artificialVars);

    for (let row = this.numConstraints - 1; row >= 0; row--) {
      if (!artSet.has(basis[row])) continue;

      let swapped = false;
      for (let j = 0; j < firstArt; j++) {
        if (Math.abs(this.tableau[row][j]) > EPSILON) {
          this.pivot(row, j);
          basis[row] = j;
          swapped = true;
          break;
        }
      }

      if (!swapped) {
        this.phase1DropRow(row);
        basis.splice(row, 1);
      }
    }

    const totalCols = this.numCols();
    const keep = Array.from({ length: totalCols }, (_, j) => j).filter(j => !artSet.has(j));
    this.tableau = this.tableau.map(row => keep.map(j => row[j]));

    const colMap = new Map(keep.map((oldJ, newJ) => [oldJ, newJ]));
    return basis.map(bv => colMap.get(bv)!);
  }
}

// ── SimplexSolver ─────────────────────────────────────────────────────────────

/**
 * Two-phase simplex solver for 2-variable LPs.
 *
 * Phase 1: find a basic feasible solution (BFS) by solving an auxiliary problem
 *          that minimises the sum of artificial variables. If the minimum is not 0,
 *          the original problem is infeasible.
 * Phase 2: optimise the original objective starting from the BFS found in phase 1.
 *
 * Use the static `SimplexSolver.solve` entry point rather than constructing directly.
 */
class SimplexSolver {
  status: OptimizerStatus;
  private readonly sense: ObjectiveSense;
  private readonly tableau: SimplexTableau;
  private basis: number[];
  private artificialVars: number[] = [];

  constructor(
    status: OptimizerStatus,
    sense: ObjectiveSense,
    tableau: SimplexTableau,
    basis: number[],
  ) {
    this.status  = status;
    this.sense   = sense;
    this.tableau = tableau;
    this.basis   = basis;
  }

  /** Runs the simplex pivot loop until optimal or unbounded. */
  private iterate(): OptimizerStatus {
    while (true) {
      const enterCol = this.tableau.getIndexSmallestCost();
      if (this.tableau.getObjectiveRow()[enterCol] >= -EPSILON) {
        return OptimizerStatus.OPTIMAL;
      }
      const leaveRow = this.tableau.minRatio(enterCol);
      if (leaveRow === null) return OptimizerStatus.UNBOUNDED;
      this.tableau.pivot(leaveRow, enterCol);
      this.basis[leaveRow] = enterCol;
    }
  }

  /** Prepares the phase 1 auxiliary problem by adding artificial variables for
   *  any constraint row whose RHS is negative after slack variable introduction. */
  private phase1Setup(): void {
    let numCols = this.tableau.numCols();
    this.tableau.phase1AddObjectiveRow(new Array<number>(numCols).fill(0));

    for (let row = 0; row < this.tableau.numConstraints; row++) {
      if (this.tableau.getRhs(row) < -EPSILON) {
        this.tableau.phase1AddArtificialVar(row);
        this.tableau.pivotRowOp(this.tableau.numRows() - 1, row, numCols);
        this.artificialVars.push(numCols);
        this.basis[row] = numCols;
        numCols++;
      }
    }
  }

  /** Runs phase 1: finds a BFS or declares the problem infeasible. */
  private phase1(): void {
    this.phase1Setup();
    this.iterate();

    // A non-zero phase 1 objective value means some artificial variable stayed positive,
    // i.e. the original constraints have no feasible point.
    if (Math.abs(this.tableau.getObjectiveValue()) > EPSILON) {
      this.status = OptimizerStatus.INFEASIBLE;
      return;
    }

    this.basis  = this.tableau.phase1Teardown(this.artificialVars, this.basis);
    this.status = OptimizerStatus.FEASIBLE;
  }

  /**
   * Reconstructs the (x, y) solution from the current basis.
   * x = x⁺ (col 1) − x⁻ (col 2); y = y⁺ (col 3) − y⁻ (col 4).
   * The stored objective value is negated back for MIN problems (the tableau
   * always minimises, so a MIN objective was stored as-is while a MAX objective
   * was negated on entry).
   */
  private getSolution(): Solution | null {
    if (this.status !== OptimizerStatus.OPTIMAL) return null;

    const vals = new Map<number, number>();
    for (let row = 0; row < this.basis.length; row++) {
      vals.set(this.basis[row], this.tableau.getRhs(row));
    }

    const x = (vals.get(1) ?? 0) - (vals.get(2) ?? 0);
    const y = (vals.get(3) ?? 0) - (vals.get(4) ?? 0);

    let objValue = this.tableau.getObjectiveValue();
    if (this.sense === ObjectiveSense.MIN) objValue = -objValue;

    return { point: [x, y], objectiveValue: objValue };
  }

  getResult(): LPResult {
    return { status: this.status, solution: this.getSolution() };
  }

  /**
   * Builds the tableau, runs phase 1 if needed, then optimises.
   * Phase 1 is skipped when all initial RHS values are non-negative (the slack
   * variables already form a valid BFS).
   */
  static solve(obj: Objective, constraints: Constraint[]): LPResult {
    const tableau = SimplexTableau.canonicalFrom(obj, constraints);
    const solver  = new SimplexSolver(
      OptimizerStatus.NONE,
      obj.sense,
      tableau,
      tableau.getInitialBasis(),
    );

    if (solver.tableau.isRhsAllNonNegative()) {
      solver.status = OptimizerStatus.FEASIBLE;
    } else {
      solver.phase1();
    }

    if (solver.status === OptimizerStatus.FEASIBLE) {
      solver.status = solver.iterate();
    }

    return solver.getResult();
  }
}

// ── Public API ────────────────────────────────────────────────────────────────

/** Solves a 2-variable LP and returns the status and optimal solution (if one exists). */
export function solveLp(obj: Objective, constraints: Constraint[]): LPResult {
  return SimplexSolver.solve(obj, constraints);
}
