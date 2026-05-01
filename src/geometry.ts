import { EPSILON, ObjectiveSense } from './types';
import type { Objective } from './types';

export interface Vec2D { x: number; y: number }

function floatEq(a: number, b: number): boolean {
  return Math.abs(a - b) < EPSILON;
}

function floatLt(a: number, b: number): boolean {
  return a - EPSILON < b;
}

function vecLen(v: Vec2D): number {
  return Math.sqrt(v.x * v.x + v.y * v.y);
}

function vecUnit(v: Vec2D): Vec2D {
  const len = vecLen(v);
  if (floatEq(len, 0)) return { x: 0, y: 0 };
  return { x: v.x / len, y: v.y / len };
}

function vecEq(a: Vec2D, b: Vec2D): boolean {
  return floatEq(a.x, b.x) && floatEq(a.y, b.y);
}

function isInBox(p: Vec2D, bl: Vec2D, tr: Vec2D): boolean {
  return floatLt(bl.x, p.x) && floatLt(p.x, tr.x)
      && floatLt(bl.y, p.y) && floatLt(p.y, tr.y);
}

export interface Line2D { x: number; y: number; rhs: number }

function linePointWithX(l: Line2D, x: number): Vec2D {
  return { x, y: (l.rhs - l.x * x) / l.y };
}

function linePointWithY(l: Line2D, y: number): Vec2D {
  return { x: (l.rhs - l.y * y) / l.x, y };
}

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

export function objectiveUnitVector(obj: Objective): Vec2D {
  const raw: Vec2D = obj.sense === ObjectiveSense.MAX
    ? { x: obj.coeffX, y: obj.coeffY }
    : { x: -obj.coeffX, y: -obj.coeffY };
  return vecUnit(raw);
}
