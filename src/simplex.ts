import { ConstraintSense, EPSILON, ObjectiveSense, OptimizerStatus } from './types';
import type {
  Constraint,
  LPResult,
  Objective,
  Solution,
} from './types';

// ── Matrix utilities ──────────────────────────────────────────────────────────

type Matrix = number[][];

function rowScale(m: Matrix, row: number, factor: number): void {
  for (let j = 0; j < m[row].length; j++) m[row][j] *= factor;
}

function rowAdd(m: Matrix, target: number, source: number, factor: number): void {
  for (let j = 0; j < m[target].length; j++) m[target][j] += factor * m[source][j];
}

// ── SimplexTableau ────────────────────────────────────────────────────────────

const FIXED_COLS = 5; // RHS + x+ x- + y+ y-

class SimplexTableau {
  tableau: Matrix;
  numConstraints: number;

  constructor(tableau: Matrix, numConstraints: number) {
    this.tableau = tableau;
    this.numConstraints = numConstraints;
  }

  private static canonicalObjectiveRow(obj: Objective): number[] {
    const { coeffX: cx, coeffY: cy, sense } = obj;
    return sense === ObjectiveSense.MAX
      ? [0, -cx,  cx, -cy,  cy]
      : [0,  cx, -cx,  cy, -cy];
  }

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

  getInitialBasis(): number[] {
    return Array.from({ length: this.numConstraints }, (_, i) => FIXED_COLS + i);
  }

  isRhsAllNonNegative(): boolean {
    for (let i = 0; i < this.numConstraints; i++) {
      if (this.tableau[i][0] < -EPSILON) return false;
    }
    return true;
  }

  getIndexSmallestCost(): number {
    const obj = this.tableau[this.tableau.length - 1];
    let minIdx = 1;
    for (let j = 2; j < obj.length; j++) {
      if (obj[j] < obj[minIdx]) minIdx = j;
    }
    return minIdx;
  }

  getObjectiveRow(): number[] { return this.tableau[this.tableau.length - 1]; }
  getObjectiveValue(): number { return this.tableau[this.tableau.length - 1][0]; }
  getRhs(row: number): number { return this.tableau[row][0]; }
  numRows(): number           { return this.tableau.length; }
  numCols(): number           { return this.tableau[0]?.length ?? 0; }

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

  pivotRowOp(currRow: number, pivotRow: number, pivotCol: number): void {
    rowAdd(this.tableau, currRow, pivotRow, -this.tableau[currRow][pivotCol]);
  }

  pivot(row: number, col: number): void {
    rowScale(this.tableau, row, 1 / this.tableau[row][col]);
    for (let i = 0; i < this.tableau.length; i++) {
      if (i !== row) this.pivotRowOp(i, row, col);
    }
  }

  phase1AddObjectiveRow(row: number[]): void {
    this.tableau.push([...row]);
  }

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

  private phase1(): void {
    this.phase1Setup();
    this.iterate();

    if (Math.abs(this.tableau.getObjectiveValue()) > EPSILON) {
      this.status = OptimizerStatus.INFEASIBLE;
      return;
    }

    this.basis  = this.tableau.phase1Teardown(this.artificialVars, this.basis);
    this.status = OptimizerStatus.FEASIBLE;
  }

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

export function solveLp(obj: Objective, constraints: Constraint[]): LPResult {
  return SimplexSolver.solve(obj, constraints);
}
