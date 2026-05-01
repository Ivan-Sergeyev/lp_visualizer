export const EPSILON = 1e-9;

// ── Constraint ────────────────────────────────────────────────────────────────

export const ConstraintSense = {
  LE: '≤',
  GE: '≥',
  EQ: '=',
} as const;
export type ConstraintSense = typeof ConstraintSense[keyof typeof ConstraintSense];

export const CONSTRAINT_SENSES = [
  ConstraintSense.LE,
  ConstraintSense.GE,
  ConstraintSense.EQ,
] as const;

export interface Constraint {
  id: string;
  coeffX: number;
  coeffY: number;
  sense: ConstraintSense;
  rhs: number;
}

export function defaultConstraint(id: string): Constraint {
  return { id, coeffX: 0, coeffY: 0, sense: ConstraintSense.LE, rhs: 0 };
}

/** Type-safe parser for <select> values. Throws on unrecognised input. */
export function parseConstraintSense(v: string): ConstraintSense {
  const match = CONSTRAINT_SENSES.find(s => s === v);
  if (!match) throw new Error(`Invalid ConstraintSense: "${v}"`);
  return match;
}

// ── Objective ─────────────────────────────────────────────────────────────────

export const ObjectiveSense = {
  MAX: 'max',
  MIN: 'min',
} as const;
export type ObjectiveSense = typeof ObjectiveSense[keyof typeof ObjectiveSense];

export const OBJECTIVE_SENSES = [ObjectiveSense.MAX, ObjectiveSense.MIN] as const;

/** Type-safe parser for <select> values. Throws on unrecognised input. */
export function parseObjectiveSense(v: string): ObjectiveSense {
  const match = OBJECTIVE_SENSES.find(s => s === v);
  if (!match) throw new Error(`Invalid ObjectiveSense: "${v}"`);
  return match;
}

export interface Objective {
  sense: ObjectiveSense;
  coeffX: number;
  coeffY: number;
}

// ── Result ────────────────────────────────────────────────────────────────────

export const OptimizerStatus = {
  OPTIMAL:    'optimal',
  UNBOUNDED:  'unbounded',
  INFEASIBLE: 'infeasible',
  FEASIBLE:   'feasible',
  NONE:       'none',
} as const;
export type OptimizerStatus = typeof OptimizerStatus[keyof typeof OptimizerStatus];

export interface Solution {
  point: [number, number];
  objectiveValue: number;
}

export interface LPResult {
  status: OptimizerStatus;
  solution: Solution | null;
}

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
