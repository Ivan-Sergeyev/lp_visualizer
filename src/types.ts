/** Tolerance used in all floating-point comparisons across geometry and solver. */
export const EPSILON = 1e-9;

// ── Constraint ────────────────────────────────────────────────────────────────

/** Inequality or equality sense for a constraint: ≤, ≥, or =. */
export const ConstraintSense = {
  LE: '≤',
  GE: '≥',
  EQ: '=',
} as const;
export type ConstraintSense = typeof ConstraintSense[keyof typeof ConstraintSense];

/** All valid ConstraintSense values, used to populate <select> option lists. */
export const CONSTRAINT_SENSES = [
  ConstraintSense.LE,
  ConstraintSense.GE,
  ConstraintSense.EQ,
] as const;

/** A single linear constraint: coeffX·x + coeffY·y {sense} rhs. */
export interface Constraint {
  id:     string;          // stable React key; generated with crypto.randomUUID()
  coeffX: number;
  coeffY: number;
  sense:  ConstraintSense;
  rhs:    number;
}

/** Returns a zeroed constraint: 0x + 0y ≤ 0. Used for new rows and the last-row reset. */
export function defaultConstraint(id: string): Constraint {
  return { id, coeffX: 0, coeffY: 0, sense: ConstraintSense.LE, rhs: 0 };
}

/** Parses a raw <select> value into ConstraintSense. Throws on unrecognised input. */
export function parseConstraintSense(v: string): ConstraintSense {
  const match = CONSTRAINT_SENSES.find(s => s === v);
  if (!match) throw new Error(`Invalid ConstraintSense: "${v}"`);
  return match;
}

/**
 * Formats a linear expression aX + bY as a human-readable string with proper
 * signs — e.g. "2x − 3y" instead of "2x + -3y". Coefficients of ±1 are shown
 * without the numeric part (e.g. "x", "−y"). Returns "0" when both are zero.
 */
export function formatLinearExpr(coeffX: number, coeffY: number): string {
  const terms: string[] = [];

  function addTerm(coeff: number, varName: string): void {
    if (Math.abs(coeff) < EPSILON) return;  // consistent with isNonzeroConstraint
    const abs    = Math.abs(coeff);
    const numStr = abs === 1 ? varName : `${abs}${varName}`;
    if (terms.length === 0) {
      terms.push(coeff < 0 ? `\u2212${numStr}` : numStr);  // − or plain first term
    } else {
      terms.push(coeff < 0 ? `\u2212 ${numStr}` : `+ ${numStr}`);
    }
  }

  addTerm(coeffX, 'x');
  addTerm(coeffY, 'y');
  return terms.length === 0 ? '0' : terms.join(' ');
}

/**
 * Returns true when at least one coefficient is non-zero, meaning this
 * constraint defines a visible line on the plot. Constraints where both
 * coefficients are zero are trivially satisfied (or infeasible) for any (x, y)
 * and produce no line — their legend entry is shown dimmed.
 */
export function isNonzeroConstraint(c: Constraint): boolean {
  return Math.abs(c.coeffX) > EPSILON || Math.abs(c.coeffY) > EPSILON;
}

// ── Objective ─────────────────────────────────────────────────────────────────

/** Whether the objective is minimised or maximised. */
export const ObjectiveSense = {
  MAX: 'max',
  MIN: 'min',
} as const;
export type ObjectiveSense = typeof ObjectiveSense[keyof typeof ObjectiveSense];

/** All valid ObjectiveSense values, used to populate <select> option lists. */
export const OBJECTIVE_SENSES = [ObjectiveSense.MAX, ObjectiveSense.MIN] as const;

/** Parses a raw <select> value into ObjectiveSense. Throws on unrecognised input. */
export function parseObjectiveSense(v: string): ObjectiveSense {
  const match = OBJECTIVE_SENSES.find(s => s === v);
  if (!match) throw new Error(`Invalid ObjectiveSense: "${v}"`);
  return match;
}

/** The objective function: optimise coeffX·x + coeffY·y in the given direction. */
export interface Objective {
  sense:  ObjectiveSense;
  coeffX: number;
  coeffY: number;
}

// ── Result ────────────────────────────────────────────────────────────────────

/**
 * Solver outcome returned by `solveLp`.
 *
 * `FEASIBLE` is an **internal** intermediate state used inside `SimplexSolver`
 * to signal "phase 1 succeeded; phase 2 not yet run." It is never returned by
 * `solveLp` — the public function always resolves to OPTIMAL, UNBOUNDED,
 * INFEASIBLE, or NONE.
 */
export const OptimizerStatus = {
  OPTIMAL:    'optimal',
  UNBOUNDED:  'unbounded',
  INFEASIBLE: 'infeasible',
  FEASIBLE:   'feasible',
  NONE:       'none',
} as const;
export type OptimizerStatus = typeof OptimizerStatus[keyof typeof OptimizerStatus];

/** An optimal solution: the point [x, y] and the objective value at that point. */
export interface Solution {
  point:          [number, number];
  objectiveValue: number;
}

/** The result returned by the solver. solution is non-null only when status is OPTIMAL. */
export interface LPResult {
  status:   OptimizerStatus;
  solution: Solution | null;
}

/** Formats an LPResult as a human-readable string for display in the Result panel. */
export function resultLabel(r: LPResult): string {
  switch (r.status) {
    case OptimizerStatus.OPTIMAL: {
      if (!r.solution) return 'Optimal solution found';
      const s = r.solution;
      return `Optimal value ${s.objectiveValue.toFixed(3)} at (${s.point[0].toFixed(3)}, ${s.point[1].toFixed(3)})`;
    }
    case OptimizerStatus.UNBOUNDED:  return 'Linear program is unbounded';
    case OptimizerStatus.INFEASIBLE: return 'Linear program is infeasible';
    case OptimizerStatus.FEASIBLE:
      // FEASIBLE is an internal intermediate state; solveLp never returns it.
      // Reaching this branch means a bug in the caller — throw rather than silently
      // returning a misleading label.
      throw new Error(
        'resultLabel: FEASIBLE is an internal solver status and should never reach the UI',
      );
    default:                         return 'Linear program has not been solved yet';
  }
}

// ── UI constants ──────────────────────────────────────────────────────────────

/** Cycling colour palette for constraint lines and legend swatches. */
export const CONSTRAINT_COLORS = [
  '#60a5fa', '#a78bfa', '#34d399', '#fb923c', '#f472b6', '#38bdf8', '#facc15',
] as const;
