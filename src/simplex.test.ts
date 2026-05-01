/**
 * LP Visualiser — test suite (Vitest)
 *
 * Covers:
 *   1. Simplex solver  — status, objective value, exact optimal point
 *   2. Constraint satisfaction  — point verifies every constraint
 *   3. Solver properties  — duality, sensitivity, idempotency
 *   4. Geometry  — lineBoxedEndpoints, objectiveUnitVector
 *   5. Graph builder  — buildLayout, buildData, PLOT_CONFIG contract
 */

import { describe, it, expect } from 'vitest';
import { solveLp } from './simplex';
import { lineBoxedEndpoints, objectiveUnitVector } from './geometry';
import { buildLayout, buildData, PLOT_CONFIG, CONSTRAINT_COLORS, X_RANGE, Y_RANGE } from './graph';
import {
  ConstraintSense,
  ObjectiveSense,
  OptimizerStatus,
  resultLabel,
  EPSILON,
  parseConstraintSense,
  parseObjectiveSense,
} from './types';
import type { Constraint, LPResult, Objective } from './types';

// ── Helpers ────────────────────────────────────────────────────────────────────

const TOL = 1e-6;
const near = (a: number, b: number) => expect(a).toBeCloseTo(b, 6);
const unitLength = (x: number, y: number) => near(Math.sqrt(x * x + y * y), 1.0);

let _id = 0;
const uid = () => String(_id++);
const le = (cx: number, cy: number, rhs: number): Constraint =>
  ({ id: uid(), coeffX: cx, coeffY: cy, sense: ConstraintSense.LE, rhs });
const ge = (cx: number, cy: number, rhs: number): Constraint =>
  ({ id: uid(), coeffX: cx, coeffY: cy, sense: ConstraintSense.GE, rhs });
const eq = (cx: number, cy: number, rhs: number): Constraint =>
  ({ id: uid(), coeffX: cx, coeffY: cy, sense: ConstraintSense.EQ, rhs });

const max = (cx: number, cy: number, cs: Constraint[]): LPResult =>
  solveLp({ sense: ObjectiveSense.MAX, coeffX: cx, coeffY: cy }, cs);
const min = (cx: number, cy: number, cs: Constraint[]): LPResult =>
  solveLp({ sense: ObjectiveSense.MIN, coeffX: cx, coeffY: cy }, cs);

function satisfies(c: Constraint, x: number, y: number): boolean {
  const lhs = c.coeffX * x + c.coeffY * y;
  if (c.sense === ConstraintSense.LE) return lhs <= c.rhs + TOL;
  if (c.sense === ConstraintSense.GE) return lhs >= c.rhs - TOL;
  return Math.abs(lhs - c.rhs) < TOL;
}

function allSatisfied(r: LPResult, cs: Constraint[]): boolean {
  if (!r.solution) return false;
  const [x, y] = r.solution.point;
  return cs.every(c => satisfies(c, x, y));
}

// ═════════════════════════════════════════════════════════════════════════════
// 1. SOLVER — STATUS DETECTION
// ═════════════════════════════════════════════════════════════════════════════

describe('Solver — optimal', () => {
  it('box: status OPTIMAL, solution present', () => {
    const r = max(1, 1, [le(1,0,3), le(0,1,4)]);
    expect(r.status).toBe(OptimizerStatus.OPTIMAL);
    expect(r.solution).not.toBeNull();
  });

  it('min with lower bounds: status OPTIMAL', () => {
    const r = min(1, 1, [ge(1,0,0), ge(0,1,0), ge(1,1,1)]);
    expect(r.status).toBe(OptimizerStatus.OPTIMAL);
    expect(r.solution).not.toBeNull();
  });
});

describe('Solver — unbounded', () => {
  it('no constraints', () => {
    const r = max(1, 1, []);
    expect(r.status).toBe(OptimizerStatus.UNBOUNDED);
    expect(r.solution).toBeNull();
  });

  it('one-sided x', () => {
    expect(max(1, 0, [ge(1,0,0)]).status).toBe(OptimizerStatus.UNBOUNDED);
  });

  it('negative cost, no upper bound', () => {
    expect(max(-1,-1,[le(1,0,-1)]).status).toBe(OptimizerStatus.UNBOUNDED);
  });
});

describe('Solver — infeasible', () => {
  it('x≤1 and x≥2', () => {
    const r = max(1, 0, [le(1,0,1), ge(1,0,2)]);
    expect(r.status).toBe(OptimizerStatus.INFEASIBLE);
    expect(r.solution).toBeNull();
  });

  it('x+y≤0 and x+y≥1', () => {
    expect(max(1,1,[le(1,1,0), ge(1,1,1)]).status).toBe(OptimizerStatus.INFEASIBLE);
  });

  it('x+y=5 and x+y≤3', () => {
    expect(max(1,0,[eq(1,1,5), le(1,1,3)]).status).toBe(OptimizerStatus.INFEASIBLE);
  });

  it('x=2 and x=3', () => {
    expect(max(1,0,[eq(1,0,2), eq(1,0,3)]).status).toBe(OptimizerStatus.INFEASIBLE);
  });
});

// ═════════════════════════════════════════════════════════════════════════════
// 2. SOLVER — OBJECTIVE VALUES
// ═════════════════════════════════════════════════════════════════════════════

describe('Solver — objective values', () => {
  const cases: Array<[string, LPResult, number]> = [
    ['max x+y box (7)',          max(1,1,[le(1,0,3),le(0,1,4)]),                         7  ],
    ['max x+y diagonal (5)',     max(1,1,[le(1,1,5),le(1,0,4),le(0,1,4)]),               5  ],
    ['min x+y lower (1)',        min(1,1,[ge(1,0,0),ge(0,1,0),ge(1,1,1)]),               1  ],
    ['max x equality (3)',       max(1,0,[eq(1,1,3),ge(1,0,0),ge(0,1,0)]),               3  ],
    ['min x+y equalities (5)',   min(1,1,[eq(1,0,2),eq(0,1,3)]),                         5  ],
    ['max 0x+0y (0)',            max(0,0,[le(1,0,5)]),                                   0  ],
    ['max -x-y lower (−2)',      max(-1,-1,[ge(1,0,1),ge(0,1,1)]),                       -2 ],
    ['max 2x (6)',               max(2,0,[le(1,0,3),le(0,1,4)]),                         6  ],
    ['min 3x+2y (7)',            min(3,2,[ge(1,0,1),ge(0,1,2)]),                         7  ],
    ['max x+y symmetric (2)',    max(1,1,[le(2,1,3),le(1,2,3)]),                         2  ],
    ['max 6x+9y default (36)',   solveLp({sense:ObjectiveSense.MAX,coeffX:6,coeffY:9},
                                   [le(2,3,12),le(1,1,5),ge(1,0,0),ge(0,1,0)]),         36 ],
  ];

  it.each(cases)('%s', (_label, r, expected) => {
    expect(r.solution).not.toBeNull();
    near(r.solution!.objectiveValue, expected);
  });
});

// ═════════════════════════════════════════════════════════════════════════════
// 3. SOLVER — EXACT OPTIMAL COORDINATES
// ═════════════════════════════════════════════════════════════════════════════

describe('Solver — optimal coordinates', () => {
  it('max x+y box → (3,4)', () => {
    const r = max(1,1,[le(1,0,3),le(0,1,4)]);
    near(r.solution!.point[0], 3);
    near(r.solution!.point[1], 4);
  });

  it('max -x-y with lower bounds → (1,1)', () => {
    const r = max(-1,-1,[ge(1,0,1),ge(0,1,1)]);
    near(r.solution!.point[0], 1);
    near(r.solution!.point[1], 1);
  });

  it('min x+y equalities → (2,3)', () => {
    const r = min(1,1,[eq(1,0,2),eq(0,1,3)]);
    near(r.solution!.point[0], 2);
    near(r.solution!.point[1], 3);
  });

  it('max 6x+9y default → (0,4)', () => {
    const r = solveLp({sense:ObjectiveSense.MAX,coeffX:6,coeffY:9},
      [le(2,3,12),le(1,1,5),ge(1,0,0),ge(0,1,0)]);
    near(r.solution!.point[0], 0);
    near(r.solution!.point[1], 4);
  });

  it('max x+y symmetric constraints → (1,1)', () => {
    const r = max(1,1,[le(2,1,3),le(1,2,3)]);
    near(r.solution!.point[0], 1);
    near(r.solution!.point[1], 1);
  });

  it('max x with equality x+y=3 → (3,0)', () => {
    const r = max(1,0,[eq(1,1,3),ge(0,1,0)]);
    near(r.solution!.point[0], 3);
    near(r.solution!.point[1], 0);
  });

  it('min 3x+2y, x≥1, y≥2 → (1,2)', () => {
    const r = min(3,2,[ge(1,0,1),ge(0,1,2)]);
    near(r.solution!.point[0], 1);
    near(r.solution!.point[1], 2);
  });
});

// ═════════════════════════════════════════════════════════════════════════════
// 4. CONSTRAINT SATISFACTION
// ═════════════════════════════════════════════════════════════════════════════

describe('Solver — solution satisfies all constraints', () => {
  const problems: Array<[string, Objective, Constraint[]]> = [
    ['app default',         {sense:ObjectiveSense.MAX,coeffX:6,coeffY:9},  [le(2,3,12),le(1,1,5),ge(1,0,0),ge(0,1,0)]],
    ['max x+y box',         {sense:ObjectiveSense.MAX,coeffX:1,coeffY:1},  [le(1,0,3),le(0,1,4)]],
    ['min with lower',      {sense:ObjectiveSense.MIN,coeffX:1,coeffY:1},  [ge(1,0,0),ge(0,1,0),ge(1,1,1)]],
    ['equality constraint', {sense:ObjectiveSense.MAX,coeffX:1,coeffY:0},  [eq(1,1,3),ge(1,0,0),ge(0,1,0)]],
    ['two equalities',      {sense:ObjectiveSense.MIN,coeffX:1,coeffY:1},  [eq(1,0,2),eq(0,1,3)]],
    ['min 3x+2y bounded',   {sense:ObjectiveSense.MIN,coeffX:3,coeffY:2},  [ge(1,0,1),ge(0,1,2)]],
    ['complex polytope',    {sense:ObjectiveSense.MAX,coeffX:5,coeffY:4},  [le(6,4,24),le(1,2,6),ge(1,0,0),ge(0,1,0)]],
  ];

  it.each(problems)('%s', (_label, obj, cs) => {
    const r = solveLp(obj, cs);
    expect(r.status).toBe(OptimizerStatus.OPTIMAL);
    expect(allSatisfied(r, cs)).toBe(true);
  });
});

// ═════════════════════════════════════════════════════════════════════════════
// 5. SOLVER PROPERTIES
// ═════════════════════════════════════════════════════════════════════════════

describe('Solver — weak duality: max ≥ min over same region', () => {
  const regions: Array<[string, Constraint[]]> = [
    ['box with bounds',  [le(1,0,3),le(0,1,4),ge(1,0,0),ge(0,1,0)]],
    ['diamond',          [le(1,1,4),le(1,-1,4),ge(1,0,0),ge(0,1,0)]],
    ['app default',      [le(2,3,12),le(1,1,5),ge(1,0,0),ge(0,1,0)]],
  ];

  it.each(regions)('%s', (_label, cs) => {
    const rMax = max(1, 1, cs);
    const rMin = min(1, 1, cs);
    expect(rMax.status).toBe(OptimizerStatus.OPTIMAL);
    expect(rMin.status).toBe(OptimizerStatus.OPTIMAL);
    expect(rMax.solution!.objectiveValue).toBeGreaterThanOrEqual(
      rMin.solution!.objectiveValue - TOL,
    );
  });
});

describe('Solver — MAX/MIN negation symmetry', () => {
  it('max cᵀx = −min(−cᵀx), same point', () => {
    const cs = [le(1,0,3), le(0,1,4)];
    const rMax = max(1, 1, cs);
    const rMin = min(-1, -1, cs);
    near(rMax.solution!.objectiveValue, -rMin.solution!.objectiveValue);
    near(rMax.solution!.point[0], rMin.solution!.point[0]);
    near(rMax.solution!.point[1], rMin.solution!.point[1]);
  });
});

describe('Solver — idempotency', () => {
  it('solving twice gives identical result', () => {
    const cs  = [le(2,3,12),le(1,1,5),ge(1,0,0),ge(0,1,0)];
    const obj: Objective = { sense: ObjectiveSense.MAX, coeffX: 6, coeffY: 9 };
    const r1 = solveLp(obj, cs);
    const r2 = solveLp(obj, cs);
    expect(r1.status).toBe(r2.status);
    near(r1.solution!.objectiveValue, r2.solution!.objectiveValue);
    near(r1.solution!.point[0], r2.solution!.point[0]);
    near(r1.solution!.point[1], r2.solution!.point[1]);
  });
});

describe('Solver — redundant constraints', () => {
  it('adding redundant constraints does not change optimum', () => {
    const base  = [le(1,0,5), le(0,1,5)];
    const extra = [le(1,0,5), le(0,1,5), le(1,0,10), le(0,1,10), le(1,1,20)];
    near(max(1,1,base).solution!.objectiveValue, max(1,1,extra).solution!.objectiveValue);
  });
});

describe('Solver — sensitivity: tightening binding constraint lowers max monotonically', () => {
  it('B=5 → 9, B=3 → 7, B=2 → 6', () => {
    const r5 = max(1,1,[le(1,0,5),le(0,1,4)]).solution!.objectiveValue;
    const r3 = max(1,1,[le(1,0,3),le(0,1,4)]).solution!.objectiveValue;
    const r2 = max(1,1,[le(1,0,2),le(0,1,4)]).solution!.objectiveValue;
    near(r5, 9); near(r3, 7); near(r2, 6);
    expect(r5).toBeGreaterThanOrEqual(r3 - TOL);
    expect(r3).toBeGreaterThanOrEqual(r2 - TOL);
  });
});

// ═════════════════════════════════════════════════════════════════════════════
// 6. GEOMETRY — lineBoxedEndpoints
// ═════════════════════════════════════════════════════════════════════════════

const BL = { x: -1, y: -1 };
const TR = { x:  6, y:  4 };

function onLine(line: { x: number; y: number; rhs: number }, p: { x: number; y: number }): boolean {
  return Math.abs(line.x * p.x + line.y * p.y - line.rhs) < TOL;
}

describe('Geometry — lineBoxedEndpoints: endpoints lie on the line', () => {
  const lines = [
    ['horizontal y=1',          { x: 0, y: 1, rhs: 1  }],
    ['vertical x=2',            { x: 1, y: 0, rhs: 2  }],
    ['diagonal x+y=3',          { x: 1, y: 1, rhs: 3  }],
    ['steep 3x+y=5',            { x: 3, y: 1, rhs: 5  }],
    ['negative slope x−y=1',    { x: 1, y:-1, rhs: 1  }],
    ['app constraint 2x+3y=12', { x: 2, y: 3, rhs: 12 }],
  ] as const;

  it.each(lines)('%s', (_label, line) => {
    const [p1, p2] = lineBoxedEndpoints(line, BL, TR);
    expect(onLine(line, p1)).toBe(true);
    expect(onLine(line, p2)).toBe(true);
  });
});

describe('Geometry — lineBoxedEndpoints: crossing lines produce distinct endpoints', () => {
  it.each([
    ['diagonal x+y=3',  { x: 1, y: 1, rhs: 3 }],
    ['vertical x=2',    { x: 1, y: 0, rhs: 2 }],
    ['horizontal y=1',  { x: 0, y: 1, rhs: 1 }],
  ] as const)('%s', (_label, line) => {
    const [p1, p2] = lineBoxedEndpoints(line, BL, TR);
    expect(Math.abs(p1.x - p2.x) + Math.abs(p1.y - p2.y)).toBeGreaterThan(TOL);
  });
});

// ═════════════════════════════════════════════════════════════════════════════
// 7. GEOMETRY — objectiveUnitVector
// ═════════════════════════════════════════════════════════════════════════════

describe('Geometry — objectiveUnitVector: always unit length', () => {
  const cases: Array<[string, Objective]> = [
    ['max (1,1)',   { sense: ObjectiveSense.MAX, coeffX: 1, coeffY: 1  }],
    ['max (6,9)',   { sense: ObjectiveSense.MAX, coeffX: 6, coeffY: 9  }],
    ['min (1,1)',   { sense: ObjectiveSense.MIN, coeffX: 1, coeffY: 1  }],
    ['max (−1,2)', { sense: ObjectiveSense.MAX, coeffX:-1, coeffY: 2  }],
    ['max (3,0)',   { sense: ObjectiveSense.MAX, coeffX: 3, coeffY: 0  }],
    ['max (0,5)',   { sense: ObjectiveSense.MAX, coeffX: 0, coeffY: 5  }],
  ];

  it.each(cases)('%s', (_label, obj) => {
    const v = objectiveUnitVector(obj);
    unitLength(v.x, v.y);
  });
});

describe('Geometry — objectiveUnitVector: direction', () => {
  it('MAX and MIN are exactly opposite', () => {
    const vMax = objectiveUnitVector({ sense: ObjectiveSense.MAX, coeffX: 3, coeffY: 4 });
    const vMin = objectiveUnitVector({ sense: ObjectiveSense.MIN, coeffX: 3, coeffY: 4 });
    near(vMax.x, -vMin.x);
    near(vMax.y, -vMin.y);
  });

  it('max (+,+) → both components positive', () => {
    const v = objectiveUnitVector({ sense: ObjectiveSense.MAX, coeffX: 3, coeffY: 4 });
    expect(v.x).toBeGreaterThan(0);
    expect(v.y).toBeGreaterThan(0);
  });

  it('max (−,+) → x negative, y positive', () => {
    const v = objectiveUnitVector({ sense: ObjectiveSense.MAX, coeffX: -2, coeffY: 5 });
    expect(v.x).toBeLessThan(0);
    expect(v.y).toBeGreaterThan(0);
  });

  it('min (+,+) → both components negative', () => {
    const v = objectiveUnitVector({ sense: ObjectiveSense.MIN, coeffX: 3, coeffY: 4 });
    expect(v.x).toBeLessThan(0);
    expect(v.y).toBeLessThan(0);
  });
});

// ═════════════════════════════════════════════════════════════════════════════
// 8. GRAPH BUILDER
// ═════════════════════════════════════════════════════════════════════════════

describe('Graph — buildLayout: structure', () => {
  const obj: Objective = { sense: ObjectiveSense.MAX, coeffX: 6, coeffY: 9 };
  const cs = [le(2,3,12), le(1,1,5), ge(1,0,0), ge(0,1,0)];
  const layout = buildLayout(obj, cs);

  it('has xaxis with correct range', () => {
    expect(layout.xaxis).toBeDefined();
    expect(layout.xaxis!.range).toEqual(X_RANGE);
  });

  it('has yaxis with correct range', () => {
    expect(layout.yaxis).toBeDefined();
    expect(layout.yaxis!.range).toEqual(Y_RANGE);
  });

  it('shape count equals constraint count', () => {
    expect((layout.shapes ?? []).length).toBe(cs.length);
  });

  it('exactly one annotation', () => {
    expect((layout.annotations ?? []).length).toBe(1);
  });
});

describe('Graph — buildLayout: shapes are well-formed', () => {
  const obj: Objective = { sense: ObjectiveSense.MAX, coeffX: 1, coeffY: 1 };
  const cs = [le(1,0,3), le(0,1,4), ge(1,1,1)];
  const shapes = (buildLayout(obj, cs).shapes ?? []) as Array<Record<string, unknown>>;

  it('one shape per constraint', () => {
    expect(shapes.length).toBe(3);
  });

  it.each([0, 1, 2])('shape[%i] is a well-formed line', (i) => {
    const s = shapes[i];
    expect(s['type']).toBe('line');
    expect(s['x0']).toBeDefined();
    expect(s['y0']).toBeDefined();
    expect(s['x1']).toBeDefined();
    expect(s['y1']).toBeDefined();
    expect(typeof (s['line'] as Record<string,unknown>)['color']).toBe('string');
  });
});

describe('Graph — buildLayout: objective arrow', () => {
  it('arrow tip is a unit vector at the origin', () => {
    const obj: Objective = { sense: ObjectiveSense.MAX, coeffX: 3, coeffY: 4 };
    const ann = (buildLayout(obj, []).annotations ?? [])[0] as Record<string, unknown>;
    unitLength(ann['x'] as number, ann['y'] as number);
    expect(ann['ax']).toBeCloseTo(0);
    expect(ann['ay']).toBeCloseTo(0);
    expect(ann['x'] as number).toBeGreaterThan(0);
    expect(ann['y'] as number).toBeGreaterThan(0);
  });
});

describe('Graph — buildLayout: colour palette wraps at index 7', () => {
  it('9 constraints → shape[7] has same colour as shape[0]', () => {
    const obj: Objective = { sense: ObjectiveSense.MAX, coeffX: 1, coeffY: 1 };
    const cs = Array.from({ length: 9 }, (_, i) => le(1, 0, i + 1));
    const shapes = (buildLayout(obj, cs).shapes ?? []) as Array<Record<string,unknown>>;
    expect(shapes.length).toBe(9);
    const color0 = (shapes[0]['line'] as Record<string,unknown>)['color'];
    const color7 = (shapes[7]['line'] as Record<string,unknown>)['color'];
    expect(color0).toBe(color7);
  });
});

describe('Graph — buildData', () => {
  it('OPTIMAL: one scatter trace at the solution point', () => {
    const result = solveLp(
      { sense: ObjectiveSense.MAX, coeffX: 6, coeffY: 9 },
      [le(2,3,12),le(1,1,5),ge(1,0,0),ge(0,1,0)],
    );
    const data = buildData(result);
    expect(data.length).toBe(1);
    const trace = data[0] as Record<string, unknown>;
    expect(trace['type']).toBe('scatter');
    expect((trace['x'] as number[])[0]).toBeCloseTo(0);
    expect((trace['y'] as number[])[0]).toBeCloseTo(4);
  });

  it.each([OptimizerStatus.UNBOUNDED, OptimizerStatus.INFEASIBLE, OptimizerStatus.NONE])(
    '%s: no data traces',
    (status) => {
      expect(buildData({ status, solution: null }).length).toBe(0);
    },
  );
});

describe('Graph — PLOT_CONFIG is a stable object', () => {
  it('is defined and has key properties', () => {
    expect(PLOT_CONFIG).toBeDefined();
    expect(typeof PLOT_CONFIG.scrollZoom).toBe('boolean');
    expect(typeof PLOT_CONFIG.displaylogo).toBe('boolean');
  });
});

describe('Graph — CONSTRAINT_COLORS', () => {
  it('has 7 entries', () => {
    expect(CONSTRAINT_COLORS.length).toBe(7);
  });

  it('all entries are hex colour strings', () => {
    for (const c of CONSTRAINT_COLORS) {
      expect(c).toMatch(/^#[0-9a-f]{6}$/i);
    }
  });
});

// ═════════════════════════════════════════════════════════════════════════════
// 9. TYPES — parsers and constants
// ═════════════════════════════════════════════════════════════════════════════

describe('parseConstraintSense', () => {
  it('accepts all valid senses', () => {
    expect(parseConstraintSense('≤')).toBe(ConstraintSense.LE);
    expect(parseConstraintSense('≥')).toBe(ConstraintSense.GE);
    expect(parseConstraintSense('=')).toBe(ConstraintSense.EQ);
  });

  it('throws on invalid input', () => {
    expect(() => parseConstraintSense('<=')).toThrow();
    expect(() => parseConstraintSense('')).toThrow();
  });
});

describe('parseObjectiveSense', () => {
  it('accepts all valid senses', () => {
    expect(parseObjectiveSense('max')).toBe(ObjectiveSense.MAX);
    expect(parseObjectiveSense('min')).toBe(ObjectiveSense.MIN);
  });

  it('throws on invalid input', () => {
    expect(() => parseObjectiveSense('MAX')).toThrow();
    expect(() => parseObjectiveSense('')).toThrow();
  });
});

describe('EPSILON', () => {
  it('is small and positive', () => {
    expect(EPSILON).toBeGreaterThan(0);
    expect(EPSILON).toBeLessThan(1e-6);
  });
});

// ═════════════════════════════════════════════════════════════════════════════
// 10. resultLabel
// ═════════════════════════════════════════════════════════════════════════════

describe('resultLabel', () => {
  it('OPTIMAL: includes value and coordinates', () => {
    const label = resultLabel({
      status: OptimizerStatus.OPTIMAL,
      solution: { point: [1.5, 2.5], objectiveValue: 10.0 },
    });
    expect(label).toContain('10.000');
    expect(label).toContain('1.500');
    expect(label).toContain('2.500');
  });

  it.each([
    [OptimizerStatus.UNBOUNDED,  'unbounded'],
    [OptimizerStatus.INFEASIBLE, 'infeasible'],
    [OptimizerStatus.FEASIBLE,   'feasible'],
    [OptimizerStatus.NONE,       'not been solved'],
  ] as const)('%s contains "%s"', (status, keyword) => {
    expect(resultLabel({ status, solution: null }).toLowerCase()).toContain(keyword);
  });
});
