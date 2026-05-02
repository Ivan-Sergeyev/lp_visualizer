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

/** Solver outcome. FEASIBLE is intermediate (feasible basis found, phase 2 not yet run). */
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
    case OptimizerStatus.FEASIBLE:   return 'Linear program is feasible';
    default:                         return 'Linear program has not been solved yet';
  }
}

// ── UI constants ──────────────────────────────────────────────────────────────

/** Cycling colour palette for constraint lines and legend swatches. */
export const CONSTRAINT_COLORS = [
  '#60a5fa', '#a78bfa', '#34d399', '#fb923c', '#f472b6', '#38bdf8', '#facc15',
] as const;
