import { EPSILON, ObjectiveSense } from './types';
import type { Objective } from './types';

/** A 2-D point or vector. */
export interface Vec2D { x: number; y: number }

// ── Floating-point helpers ────────────────────────────────────────────────────

function floatEq(a: number, b: number): boolean {
  return Math.abs(a - b) < EPSILON;
}

/** Returns true when a < b, allowing for floating-point tolerance. */
function floatLt(a: number, b: number): boolean {
  return a - EPSILON < b;
}

// ── Vector utilities ──────────────────────────────────────────────────────────

function vecLen(v: Vec2D): number {
  return Math.sqrt(v.x * v.x + v.y * v.y);
}

/** Returns the unit vector of v, or the zero vector if v has zero length. */
function vecUnit(v: Vec2D): Vec2D {
  const len = vecLen(v);
  if (floatEq(len, 0)) return { x: 0, y: 0 };
  return { x: v.x / len, y: v.y / len };
}

function vecEq(a: Vec2D, b: Vec2D): boolean {
  return floatEq(a.x, b.x) && floatEq(a.y, b.y);
}

/** Returns true when p is strictly inside the axis-aligned box [bl, tr]. */
function isInBox(p: Vec2D, bl: Vec2D, tr: Vec2D): boolean {
  return floatLt(bl.x, p.x) && floatLt(p.x, tr.x)
      && floatLt(bl.y, p.y) && floatLt(p.y, tr.y);
}

// ── Line geometry ─────────────────────────────────────────────────────────────

/** A line in the form x·X + y·Y = rhs (field names are the coefficients, not coordinates). */
export interface Line2D { x: number; y: number; rhs: number }

/** Returns the point on l where the X-coordinate equals x (requires l.y ≠ 0). */
function linePointWithX(l: Line2D, x: number): Vec2D {
  return { x, y: (l.rhs - l.x * x) / l.y };
}

/** Returns the point on l where the Y-coordinate equals y (requires l.x ≠ 0). */
function linePointWithY(l: Line2D, y: number): Vec2D {
  return { x: (l.rhs - l.y * y) / l.x, y };
}

/**
 * Returns the two points where `line` intersects the axis-aligned bounding box
 * defined by `bottomLeft` and `topRight`.
 *
 * Candidates are computed at each of the four box edges, then filtered to those
 * strictly inside the box to avoid counting corners twice. If the line misses or
 * only grazes the box, both elements of the returned pair are the same point.
 */
export function lineBoxedEndpoints(
  line: Line2D,
  bottomLeft: Vec2D,
  topRight: Vec2D,
): [Vec2D, Vec2D] {
  const candidates: Vec2D[] = [];

  if (!floatEq(line.x, 0)) {
    candidates.push(linePointWithY(line, bottomLeft.y));
    candidates.push(linePointWithY(line, topRight.y));
  }
  if (!floatEq(line.y, 0)) {
    candidates.push(linePointWithX(line, bottomLeft.x));
    candidates.push(linePointWithX(line, topRight.x));
  }

  const unique: Vec2D[] = [];
  for (const p of candidates) {
    if (isInBox(p, bottomLeft, topRight) && !unique.some(u => vecEq(u, p))) {
      unique.push(p);
    }
  }

  if (unique.length === 0) return [bottomLeft, bottomLeft];
  if (unique.length === 1) return [unique[0], unique[0]];
  return [unique[0], unique[1]];
}

/**
 * Returns a unit vector pointing in the direction of improvement for `obj`.
 * For MAX, this is the gradient (coeffX, coeffY); for MIN, it is negated.
 * Used to orient the objective arrow on the plot.
 */
export function objectiveUnitVector(obj: Objective): Vec2D {
  const raw: Vec2D = obj.sense === ObjectiveSense.MAX
    ? { x: obj.coeffX, y: obj.coeffY }
    : { x: -obj.coeffX, y: -obj.coeffY };
  return vecUnit(raw);
}
