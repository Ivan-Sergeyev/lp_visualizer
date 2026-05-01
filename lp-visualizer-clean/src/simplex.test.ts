/**
 * LP Visualiser — test suite
 *
 * Covers:
 *   1. Simplex solver  — status, objective value, and exact optimal point
 *   2. Constraint satisfaction  — solution point verifies every constraint
 *   3. Solver properties  — duality, sensitivity, idempotency
 *   4. Geometry  — lineBoxedEndpoints, objectiveUnitVector
 *   5. Graph builder  — buildFigure shape/annotation/data contract
 *
 * Run:  npx tsx src/simplex.test.ts
 */

import { solveLp } from './simplex';
import { lineBoxedEndpoints, objectiveUnitVector } from './geometry';
import { buildFigure, X_RANGE, Y_RANGE } from './graph';
import {
  ConstraintSense,
  ObjectiveSense,
  OptimizerStatus,
  resultLabel,
  EPSILON,
} from './types';
import type { Constraint, LPResult, Objective } from './types';

// ── Mini test runner ───────────────────────────────────────────────────────────

let passed = 0;
let failed = 0;
const failures: string[] = [];

function test(name: string, condition: boolean, detail?: string) {
  if (condition) {
    passed++;
    process.stdout.write(`  ✓  ${name}\n`);
  } else {
    failed++;
    const msg = detail ? `${name} — ${detail}` : name;
    failures.push(msg);
    process.stdout.write(`  ✗  ${msg}\n`);
  }
}

function section(name: string) {
  process.stdout.write(`\n── ${name}\n`);
}

// ── Numeric helpers ────────────────────────────────────────────────────────────

const TOL = 1e-6;

function near(a: number, b: number, tol = TOL): boolean {
  return Math.abs(a - b) < tol;
}

function unitLength(x: number, y: number): boolean {
  return near(Math.sqrt(x * x + y * y), 1.0);
}

// ── LP construction helpers ────────────────────────────────────────────────────

let _id = 0;
const id = () => String(_id++);

const le  = (cx: number, cy: number, rhs: number): Constraint =>
  ({ id: id(), coeffX: cx, coeffY: cy, sense: ConstraintSense.LE, rhs });
const ge  = (cx: number, cy: number, rhs: number): Constraint =>
  ({ id: id(), coeffX: cx, coeffY: cy, sense: ConstraintSense.GE, rhs });
const eq  = (cx: number, cy: number, rhs: number): Constraint =>
  ({ id: id(), coeffX: cx, coeffY: cy, sense: ConstraintSense.EQ, rhs });

function max(cx: number, cy: number, cs: Constraint[]): LPResult {
  return solveLp({ sense: ObjectiveSense.MAX, coeffX: cx, coeffY: cy }, cs);
}
function min(cx: number, cy: number, cs: Constraint[]): LPResult {
  return solveLp({ sense: ObjectiveSense.MIN, coeffX: cx, coeffY: cy }, cs);
}

/** Returns true if the point satisfies the constraint (within tolerance). */
function satisfies(c: Constraint, x: number, y: number): boolean {
  const lhs = c.coeffX * x + c.coeffY * y;
  if (c.sense === ConstraintSense.LE) return lhs <= c.rhs + TOL;
  if (c.sense === ConstraintSense.GE) return lhs >= c.rhs - TOL;
  return near(lhs, c.rhs);                 // EQ
}

/** Verifies that the solution point satisfies every constraint in the list. */
function pointSatisfiesAll(r: LPResult, cs: Constraint[]): boolean {
  if (!r.solution) return false;
  const [x, y] = r.solution.point;
  return cs.every(c => satisfies(c, x, y));
}

// ═════════════════════════════════════════════════════════════════════════════
// 1. SIMPLEX SOLVER — STATUS DETECTION
// ═════════════════════════════════════════════════════════════════════════════

section('Solver — optimal: status and solution presence');

{
  const cs = [le(1,0,3), le(0,1,4)];
  const r  = max(1, 1, cs);
  test('box — status is OPTIMAL',   r.status === OptimizerStatus.OPTIMAL);
  test('box — solution is not null', r.solution !== null);
}

{
  const cs = [ge(1,0,0), ge(0,1,0), ge(1,1,1)];
  const r  = min(1, 1, cs);
  test('min lower-bound — status is OPTIMAL', r.status === OptimizerStatus.OPTIMAL);
  test('min lower-bound — solution present',  r.solution !== null);
}

section('Solver — unbounded: status and null solution');

{
  test('no constraints — UNBOUNDED',       max(1, 1, []).status === OptimizerStatus.UNBOUNDED);
  test('no constraints — null solution',   max(1, 1, []).solution === null);
  test('one-sided x — UNBOUNDED',          max(1, 0, [ge(1,0,0)]).status === OptimizerStatus.UNBOUNDED);
  test('negative cost, no ub — UNBOUNDED', max(-1,-1,[le(1,0,-1)]).status === OptimizerStatus.UNBOUNDED);
}

section('Solver — infeasible: status and null solution');

{
  const cs1 = [le(1,0,1), ge(1,0,2)];
  const r1  = max(1, 0, cs1);
  test('x≤1 ∧ x≥2 — INFEASIBLE',       r1.status === OptimizerStatus.INFEASIBLE);
  test('x≤1 ∧ x≥2 — null solution',    r1.solution === null);

  test('x+y≤0 ∧ x+y≥1 — INFEASIBLE',  max(1,1,[le(1,1,0),ge(1,1,1)]).status === OptimizerStatus.INFEASIBLE);
  test('x+y=5 ∧ x+y≤3 — INFEASIBLE',  max(1,0,[eq(1,1,5),le(1,1,3)]).status === OptimizerStatus.INFEASIBLE);
  test('x=2 ∧ x=3 — INFEASIBLE',      max(1,0,[eq(1,0,2),eq(1,0,3)]).status === OptimizerStatus.INFEASIBLE);
}

// ═════════════════════════════════════════════════════════════════════════════
// 2. SIMPLEX SOLVER — EXACT OBJECTIVE VALUES
// ═════════════════════════════════════════════════════════════════════════════

section('Solver — objective value accuracy');

{
  const cases: Array<{ label: string; r: LPResult; expected: number }> = [
    { label: 'max x+y box (7)',          r: max(1,1,[le(1,0,3),le(0,1,4)]),                 expected: 7  },
    { label: 'max x+y diagonal (5)',     r: max(1,1,[le(1,1,5),le(1,0,4),le(0,1,4)]),      expected: 5  },
    { label: 'min x+y lower (1)',        r: min(1,1,[ge(1,0,0),ge(0,1,0),ge(1,1,1)]),      expected: 1  },
    { label: 'max x equality (3)',       r: max(1,0,[eq(1,1,3),ge(1,0,0),ge(0,1,0)]),      expected: 3  },
    { label: 'min x+y equalities (5)',   r: min(1,1,[eq(1,0,2),eq(0,1,3)]),                expected: 5  },
    { label: 'max 0x+0y (0)',            r: max(0,0,[le(1,0,5)]),                           expected: 0  },
    { label: 'max -x-y lower (−2)',      r: max(-1,-1,[ge(1,0,1),ge(0,1,1)]),              expected: -2 },
    { label: 'max 2x (6)',               r: max(2,0,[le(1,0,3),le(0,1,4)]),                expected: 6  },
    { label: 'min 3x+2y (7)',            r: min(3,2,[ge(1,0,1),ge(0,1,2)]),                expected: 7  },
    { label: 'max x+y sym (2)',          r: max(1,1,[le(2,1,3),le(1,2,3)]),                expected: 2  },
    { label: 'max 6x+9y default (36)',   r: solveLp({sense:ObjectiveSense.MAX,coeffX:6,coeffY:9},
        [le(2,3,12),le(1,1,5),ge(1,0,0),ge(0,1,0)]),                                       expected: 36 },
  ];

  for (const { label, r, expected } of cases) {
    test(label,
      r.solution !== null && near(r.solution.objectiveValue, expected),
      r.solution ? `got ${r.solution.objectiveValue.toFixed(6)}` : 'no solution');
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// 3. SIMPLEX SOLVER — EXACT OPTIMAL POINTS
// ═════════════════════════════════════════════════════════════════════════════

section('Solver — exact optimal coordinates');

function testPoint(label: string, r: LPResult, ex: number, ey: number) {
  const ok = r.solution !== null
    && near(r.solution.point[0], ex)
    && near(r.solution.point[1], ey);
  test(label, ok,
    r.solution
      ? `got (${r.solution.point[0].toFixed(4)}, ${r.solution.point[1].toFixed(4)}), expected (${ex}, ${ey})`
      : 'no solution');
}

{
  testPoint('max x+y box → (3,4)',
    max(1,1,[le(1,0,3),le(0,1,4)]), 3, 4);

  testPoint('max -x-y with lower bounds → (1,1)',
    max(-1,-1,[ge(1,0,1),ge(0,1,1)]), 1, 1);

  testPoint('min x+y equalities → (2,3)',
    min(1,1,[eq(1,0,2),eq(0,1,3)]), 2, 3);

  testPoint('max 6x+9y default → (0,4)',
    solveLp({sense:ObjectiveSense.MAX,coeffX:6,coeffY:9},
      [le(2,3,12),le(1,1,5),ge(1,0,0),ge(0,1,0)]),
    0, 4);

  testPoint('max x+y symmetric constraints → (1,1)',
    max(1,1,[le(2,1,3),le(1,2,3)]), 1, 1);

  testPoint('max x with equality x+y=3, y≥0 → (3,0)',
    max(1,0,[eq(1,1,3),ge(0,1,0)]), 3, 0);

  testPoint('min 3x+2y, x≥1, y≥2 → (1,2)',
    min(3,2,[ge(1,0,1),ge(0,1,2)]), 1, 2);
}

// ═════════════════════════════════════════════════════════════════════════════
// 4. CONSTRAINT SATISFACTION
// ═════════════════════════════════════════════════════════════════════════════

section('Solver — solution point satisfies all constraints');

{
  const problems: Array<{ label: string; obj: Objective; cs: Constraint[] }> = [
    {
      label: 'app default LP',
      obj: { sense: ObjectiveSense.MAX, coeffX: 6, coeffY: 9 },
      cs: [le(2,3,12), le(1,1,5), ge(1,0,0), ge(0,1,0)],
    },
    {
      label: 'max x+y in box',
      obj: { sense: ObjectiveSense.MAX, coeffX: 1, coeffY: 1 },
      cs: [le(1,0,3), le(0,1,4)],
    },
    {
      label: 'min x+y with lower bounds',
      obj: { sense: ObjectiveSense.MIN, coeffX: 1, coeffY: 1 },
      cs: [ge(1,0,0), ge(0,1,0), ge(1,1,1)],
    },
    {
      label: 'max with equality constraint',
      obj: { sense: ObjectiveSense.MAX, coeffX: 1, coeffY: 0 },
      cs: [eq(1,1,3), ge(1,0,0), ge(0,1,0)],
    },
    {
      label: 'multiple equality constraints',
      obj: { sense: ObjectiveSense.MIN, coeffX: 1, coeffY: 1 },
      cs: [eq(1,0,2), eq(0,1,3)],
    },
    {
      label: 'min 3x+2y, x≥1, y≥2',
      obj: { sense: ObjectiveSense.MIN, coeffX: 3, coeffY: 2 },
      cs: [ge(1,0,1), ge(0,1,2)],
    },
    {
      label: 'complex polytope',
      obj: { sense: ObjectiveSense.MAX, coeffX: 5, coeffY: 4 },
      cs: [le(6,4,24), le(1,2,6), ge(1,0,0), ge(0,1,0)],
    },
  ];

  for (const { label, obj, cs } of problems) {
    const r = solveLp(obj, cs);
    test(`${label} — point satisfies all constraints`,
      r.status === OptimizerStatus.OPTIMAL && pointSatisfiesAll(r, cs));
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// 5. SOLVER PROPERTIES
// ═════════════════════════════════════════════════════════════════════════════

section('Solver — weak duality: max f ≥ min f over same region');

{
  const pairs: Array<{ label: string; cs: Constraint[] }> = [
    { label: 'box',         cs: [le(1,0,3), le(0,1,4), ge(1,0,0), ge(0,1,0)] },
    { label: 'diamond',     cs: [le(1,1,4), le(1,-1,4), ge(1,0,0), ge(0,1,0)] },
    { label: 'app default', cs: [le(2,3,12), le(1,1,5), ge(1,0,0), ge(0,1,0)] },
  ];

  for (const { label, cs } of pairs) {
    const rMax = max(1, 1, cs);
    const rMin = min(1, 1, cs);
    test(`${label}: max ≥ min`,
      rMax.status === OptimizerStatus.OPTIMAL &&
      rMin.status === OptimizerStatus.OPTIMAL &&
      rMax.solution!.objectiveValue >= rMin.solution!.objectiveValue - TOL);
  }
}

section('Solver — MAX/MIN negation symmetry: max cᵀx = −(min −cᵀx)');

{
  const cs = [le(1,0,3), le(0,1,4)];
  const rMax = max(1, 1, cs);
  const rMin = min(-1, -1, cs);
  test('objective values are negations',
    rMax.solution !== null && rMin.solution !== null &&
    near(rMax.solution.objectiveValue, -rMin.solution.objectiveValue));
  test('optimal points are identical',
    rMax.solution !== null && rMin.solution !== null &&
    near(rMax.solution.point[0], rMin.solution.point[0]) &&
    near(rMax.solution.point[1], rMin.solution.point[1]));
}

section('Solver — idempotency: solving twice gives the same result');

{
  const cs  = [le(2,3,12), le(1,1,5), ge(1,0,0), ge(0,1,0)];
  const obj: Objective = { sense: ObjectiveSense.MAX, coeffX: 6, coeffY: 9 };
  const r1 = solveLp(obj, cs);
  const r2 = solveLp(obj, cs);
  test('same status',    r1.status === r2.status);
  test('same objective', r1.solution !== null && r2.solution !== null &&
    near(r1.solution.objectiveValue, r2.solution.objectiveValue));
  test('same point',     r1.solution !== null && r2.solution !== null &&
    near(r1.solution.point[0], r2.solution.point[0]) &&
    near(r1.solution.point[1], r2.solution.point[1]));
}

section('Solver — redundant constraints do not change the optimum');

{
  const base  = [le(1,0,5), le(0,1,5)];
  const extra = [le(1,0,5), le(0,1,5), le(1,0,10), le(0,1,10), le(1,1,20)];
  const r1 = max(1, 1, base);
  const r2 = max(1, 1, extra);
  test('same objective',
    r1.solution !== null && r2.solution !== null &&
    near(r1.solution.objectiveValue, r2.solution.objectiveValue));
}

section('Solver — tightening a binding constraint lowers the maximum monotonically');

{
  const r5 = max(1,1,[le(1,0,5),le(0,1,4)]);
  const r3 = max(1,1,[le(1,0,3),le(0,1,4)]);
  const r2 = max(1,1,[le(1,0,2),le(0,1,4)]);
  test('B=5 → obj=9', r5.solution !== null && near(r5.solution.objectiveValue, 9));
  test('B=3 → obj=7', r3.solution !== null && near(r3.solution.objectiveValue, 7));
  test('B=2 → obj=6', r2.solution !== null && near(r2.solution.objectiveValue, 6));
  test('obj(B=5) ≥ obj(B=3) ≥ obj(B=2)',
    r5.solution !== null && r3.solution !== null && r2.solution !== null &&
    r5.solution.objectiveValue >= r3.solution.objectiveValue - TOL &&
    r3.solution.objectiveValue >= r2.solution.objectiveValue - TOL);
}

// ═════════════════════════════════════════════════════════════════════════════
// 6. GEOMETRY — lineBoxedEndpoints
// ═════════════════════════════════════════════════════════════════════════════

section('Geometry — lineBoxedEndpoints: endpoints lie exactly on the line');

const BL = { x: -1, y: -1 };
const TR = { x:  6, y:  4 };

function onLine(line: { x: number; y: number; rhs: number }, p: { x: number; y: number }): boolean {
  return near(line.x * p.x + line.y * p.y, line.rhs);
}

{
  const cases = [
    { label: 'horizontal y=1',       line: { x: 0, y: 1, rhs: 1  } },
    { label: 'vertical x=2',         line: { x: 1, y: 0, rhs: 2  } },
    { label: 'diagonal x+y=3',       line: { x: 1, y: 1, rhs: 3  } },
    { label: 'steep 3x+y=5',         line: { x: 3, y: 1, rhs: 5  } },
    { label: 'negative slope x−y=1', line: { x: 1, y:-1, rhs: 1  } },
    { label: 'app constraint 2x+3y=12', line: { x: 2, y: 3, rhs: 12 } },
  ];

  for (const { label, line } of cases) {
    const [p1, p2] = lineBoxedEndpoints(line, BL, TR);
    test(`${label}: p1 on line`, onLine(line, p1));
    test(`${label}: p2 on line`, onLine(line, p2));
  }
}

section('Geometry — lineBoxedEndpoints: endpoints are distinct for lines crossing the box');

{
  const crossing = [
    { label: 'diagonal x+y=3',   line: { x: 1, y: 1, rhs: 3  } },
    { label: 'vertical x=2',     line: { x: 1, y: 0, rhs: 2  } },
    { label: 'horizontal y=1',   line: { x: 0, y: 1, rhs: 1  } },
  ];
  for (const { label, line } of crossing) {
    const [p1, p2] = lineBoxedEndpoints(line, BL, TR);
    test(`${label}: endpoints are distinct`, !near(p1.x, p2.x) || !near(p1.y, p2.y));
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// 7. GEOMETRY — objectiveUnitVector
// ═════════════════════════════════════════════════════════════════════════════

section('Geometry — objectiveUnitVector: always a unit vector');

{
  const objectives: Array<{ label: string; obj: Objective }> = [
    { label: 'max (1,1)',  obj: { sense: ObjectiveSense.MAX, coeffX: 1, coeffY: 1  } },
    { label: 'max (6,9)',  obj: { sense: ObjectiveSense.MAX, coeffX: 6, coeffY: 9  } },
    { label: 'min (1,1)',  obj: { sense: ObjectiveSense.MIN, coeffX: 1, coeffY: 1  } },
    { label: 'max (−1,2)', obj: { sense: ObjectiveSense.MAX, coeffX:-1, coeffY: 2  } },
    { label: 'max (3,0)',  obj: { sense: ObjectiveSense.MAX, coeffX: 3, coeffY: 0  } },
    { label: 'max (0,5)',  obj: { sense: ObjectiveSense.MAX, coeffX: 0, coeffY: 5  } },
  ];

  for (const { label, obj } of objectives) {
    const v = objectiveUnitVector(obj);
    test(`${label}: unit length`, unitLength(v.x, v.y));
  }
}

section('Geometry — objectiveUnitVector: MAX and MIN are exactly opposite');

{
  const cx = 3, cy = 4;
  const vMax = objectiveUnitVector({ sense: ObjectiveSense.MAX, coeffX: cx, coeffY: cy });
  const vMin = objectiveUnitVector({ sense: ObjectiveSense.MIN, coeffX: cx, coeffY: cy });
  test('x-components are negated', near(vMax.x, -vMin.x));
  test('y-components are negated', near(vMax.y, -vMin.y));
}

section('Geometry — objectiveUnitVector: points in the correct half-plane');

{
  const v1 = objectiveUnitVector({ sense: ObjectiveSense.MAX, coeffX: 3, coeffY: 4 });
  test('max (+,+) → v.x > 0', v1.x > 0);
  test('max (+,+) → v.y > 0', v1.y > 0);

  const v2 = objectiveUnitVector({ sense: ObjectiveSense.MAX, coeffX: -2, coeffY: 5 });
  test('max (−,+) → v.x < 0', v2.x < 0);
  test('max (−,+) → v.y > 0', v2.y > 0);

  const v3 = objectiveUnitVector({ sense: ObjectiveSense.MIN, coeffX: 3, coeffY: 4 });
  test('min (+,+) → v.x < 0', v3.x < 0);
  test('min (+,+) → v.y < 0', v3.y < 0);
}

// ═════════════════════════════════════════════════════════════════════════════
// 8. GRAPH BUILDER
// ═════════════════════════════════════════════════════════════════════════════

section('Graph — buildFigure: layout structure');

{
  const obj: Objective = { sense: ObjectiveSense.MAX, coeffX: 6, coeffY: 9 };
  const cs = [le(2,3,12), le(1,1,5), ge(1,0,0), ge(0,1,0)];
  const fig = buildFigure(obj, cs, solveLp(obj, cs));

  test('layout has xaxis',             !!fig.layout.xaxis);
  test('layout has yaxis',             !!fig.layout.yaxis);
  test('xaxis range matches X_RANGE',  JSON.stringify(fig.layout.xaxis!.range) === JSON.stringify(X_RANGE));
  test('yaxis range matches Y_RANGE',  JSON.stringify(fig.layout.yaxis!.range) === JSON.stringify(Y_RANGE));
  test('shapes count = constraints',   (fig.layout.shapes  ?? []).length === cs.length);
  test('exactly one annotation',       (fig.layout.annotations ?? []).length === 1);
  test('config object is present',     !!fig.config);
}

section('Graph — buildFigure: constraint shapes are well-formed line objects');

{
  const obj: Objective = { sense: ObjectiveSense.MAX, coeffX: 1, coeffY: 1 };
  const cs = [le(1,0,3), le(0,1,4), ge(1,1,1)];
  const fig = buildFigure(obj, cs, { status: OptimizerStatus.NONE, solution: null });
  const shapes = (fig.layout.shapes ?? []) as Array<Record<string,unknown>>;

  test('one shape per constraint', shapes.length === 3);

  for (let i = 0; i < shapes.length; i++) {
    const s = shapes[i];
    test(`shape[${i}] type="line"`,  s['type'] === 'line');
    test(`shape[${i}] has x0/y0`,    s['x0'] !== undefined && s['y0'] !== undefined);
    test(`shape[${i}] has x1/y1`,    s['x1'] !== undefined && s['y1'] !== undefined);
    const lineObj = s['line'] as Record<string,unknown>;
    test(`shape[${i}] has line.color`, typeof lineObj['color'] === 'string');
  }
}

section('Graph — buildFigure: optimal scatter point');

{
  const obj: Objective = { sense: ObjectiveSense.MAX, coeffX: 6, coeffY: 9 };
  const cs = [le(2,3,12), le(1,1,5), ge(1,0,0), ge(0,1,0)];
  const result = solveLp(obj, cs);   // optimal at (0,4)
  const fig = buildFigure(obj, cs, result);

  test('OPTIMAL: exactly one trace',      fig.data.length === 1);
  const trace = fig.data[0] as Record<string,unknown>;
  test('OPTIMAL: trace type=scatter',     trace['type'] === 'scatter');
  test('OPTIMAL: x matches solution',
    Array.isArray(trace['x']) && near((trace['x'] as number[])[0], 0));
  test('OPTIMAL: y matches solution',
    Array.isArray(trace['y']) && near((trace['y'] as number[])[0], 4));
}

section('Graph — buildFigure: no data trace for non-optimal results');

{
  const obj: Objective = { sense: ObjectiveSense.MAX, coeffX: 1, coeffY: 0 };
  test('UNBOUNDED: no traces',  buildFigure(obj, [], { status: OptimizerStatus.UNBOUNDED,  solution: null }).data.length === 0);
  test('INFEASIBLE: no traces', buildFigure(obj, [], { status: OptimizerStatus.INFEASIBLE, solution: null }).data.length === 0);
  test('NONE: no traces',       buildFigure(obj, [], { status: OptimizerStatus.NONE,       solution: null }).data.length === 0);
}

section('Graph — buildFigure: objective arrow is a unit vector at the origin');

{
  const obj: Objective = { sense: ObjectiveSense.MAX, coeffX: 3, coeffY: 4 };
  const fig = buildFigure(obj, [], { status: OptimizerStatus.NONE, solution: null });
  const ann = (fig.layout.annotations ?? [])[0] as Record<string,unknown>;
  const ax = ann['x'] as number;
  const ay = ann['y'] as number;
  test('arrow tip is a unit vector',       unitLength(ax, ay));
  test('arrow tail ax=0',                  near(ann['ax'] as number, 0));
  test('arrow tail ay=0',                  near(ann['ay'] as number, 0));
  test('tip x > 0 for max(+,+)',           ax > 0);
  test('tip y > 0 for max(+,+)',           ay > 0);
}

section('Graph — buildFigure: colour palette wraps after 7 constraints');

{
  const obj: Objective = { sense: ObjectiveSense.MAX, coeffX: 1, coeffY: 1 };
  const cs = Array.from({ length: 9 }, (_, i) => le(1, 0, i + 1));
  const fig = buildFigure(obj, cs, { status: OptimizerStatus.NONE, solution: null });
  const shapes = (fig.layout.shapes ?? []) as Array<Record<string,unknown>>;
  test('9 shapes produced', shapes.length === 9);
  const color0 = (shapes[0]['line'] as Record<string,unknown>)['color'] as string;
  const color7 = (shapes[7]['line'] as Record<string,unknown>)['color'] as string;
  test('colour at index 7 equals colour at index 0', color0 === color7);
}

// ═════════════════════════════════════════════════════════════════════════════
// 9. EPSILON CONTRACT
// ═════════════════════════════════════════════════════════════════════════════

section('EPSILON constant');

{
  test('EPSILON > 0',    EPSILON > 0);
  test('EPSILON < 1e-6', EPSILON < 1e-6);
}

// ═════════════════════════════════════════════════════════════════════════════
// 10. resultLabel formatting
// ═════════════════════════════════════════════════════════════════════════════

section('resultLabel — output strings');

{
  const label = resultLabel({ status: OptimizerStatus.OPTIMAL, solution: { point: [1.5, 2.5], objectiveValue: 10.0 } });
  test('OPTIMAL: contains value 10.000', label.includes('10.000'));
  test('OPTIMAL: contains x 1.500',      label.includes('1.500'));
  test('OPTIMAL: contains y 2.500',      label.includes('2.500'));

  const byStatus: Array<[OptimizerStatus, string]> = [
    [OptimizerStatus.UNBOUNDED,  'unbounded'],
    [OptimizerStatus.INFEASIBLE, 'infeasible'],
    [OptimizerStatus.FEASIBLE,   'feasible'],
    [OptimizerStatus.NONE,       'not been solved'],
  ];
  for (const [status, keyword] of byStatus) {
    test(`${status}: label contains "${keyword}"`,
      resultLabel({ status, solution: null }).toLowerCase().includes(keyword));
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// SUMMARY
// ═════════════════════════════════════════════════════════════════════════════

process.stdout.write(`\n${'─'.repeat(64)}\n`);
process.stdout.write(`${passed + failed} tests — ${passed} passed, ${failed} failed\n`);

if (failures.length > 0) {
  process.stdout.write('\nFailed:\n');
  failures.forEach(f => process.stdout.write(`  ✗  ${f}\n`));
  process.exit(1);
} else {
  process.stdout.write('All tests passed ✓\n');
}
