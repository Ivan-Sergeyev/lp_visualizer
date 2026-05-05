// @vitest-environment jsdom
/**
 * URL codec tests — encodeModel / decodeModel / readModelFromUrl / writeModelToUrl
 *
 * Covers:
 *  - Round-trip fidelity (encode then decode reproduces the original model)
 *  - Malformed / missing parameters → null
 *  - Non-finite numbers → null
 *  - Unknown sense codes → null
 *  - Negative coefficients survive the round-trip
 *  - Browser-aware helpers (readModelFromUrl, writeModelToUrl)
 */

import { describe, it, expect } from 'vitest';
import { encodeModel, decodeModel, readModelFromUrl, writeModelToUrl } from './url';
import { ConstraintSense, ObjectiveSense } from './types';
import type { Constraint, Objective } from '../types';

// ── Fixtures ──────────────────────────────────────────────────────────────────

const obj: Objective = { sense: ObjectiveSense.MAX, coeffX: 6, coeffY: 7 };

const constraints: Constraint[] = [
  { id: crypto.randomUUID(), coeffX: 2,  coeffY: 3,  sense: ConstraintSense.LE, rhs: 12 },
  { id: crypto.randomUUID(), coeffX: 1,  coeffY: 1,  sense: ConstraintSense.LE, rhs: 5  },
  { id: crypto.randomUUID(), coeffX: -1, coeffY: 0,  sense: ConstraintSense.GE, rhs: -3 },
  { id: crypto.randomUUID(), coeffX: 0,  coeffY: -2, sense: ConstraintSense.EQ, rhs: 0  },
];

// ── Round-trip ────────────────────────────────────────────────────────────────

describe('URL codec — round-trip', () => {
  it('encodes then decodes the objective faithfully', () => {
    const decoded = decodeModel(encodeModel(obj, constraints));
    expect(decoded).not.toBeNull();
    expect(decoded!.objective.sense).toBe(obj.sense);
    expect(decoded!.objective.coeffX).toBeCloseTo(obj.coeffX);
    expect(decoded!.objective.coeffY).toBeCloseTo(obj.coeffY);
  });

  it('preserves constraint count', () => {
    const decoded = decodeModel(encodeModel(obj, constraints));
    expect(decoded!.constraints.length).toBe(constraints.length);
  });

  it('preserves all constraint fields (coeffX, coeffY, sense, rhs)', () => {
    const decoded = decodeModel(encodeModel(obj, constraints));
    for (let i = 0; i < constraints.length; i++) {
      const orig = constraints[i];
      const dec  = decoded!.constraints[i];
      expect(dec.coeffX).toBeCloseTo(orig.coeffX);
      expect(dec.coeffY).toBeCloseTo(orig.coeffY);
      expect(dec.sense).toBe(orig.sense);
      expect(dec.rhs).toBeCloseTo(orig.rhs);
    }
  });

  it('assigns fresh ids (not the originals) after decoding', () => {
    const decoded = decodeModel(encodeModel(obj, constraints));
    const decodedIds  = decoded!.constraints.map(c => c.id);
    const originalIds = constraints.map(c => c.id);
    // IDs should all be valid UUIDs but none should match the original ones
    for (const id of decodedIds) {
      expect(id).toMatch(/^[0-9a-f-]{36}$/);
      expect(originalIds).not.toContain(id);
    }
  });

  it('round-trips a MIN objective', () => {
    const minObj: Objective = { sense: ObjectiveSense.MIN, coeffX: 3, coeffY: -2 };
    const decoded = decodeModel(encodeModel(minObj, []));
    // Empty constraint list returns null — use a single constraint
    const cs: Constraint[] = [
      { id: crypto.randomUUID(), coeffX: 1, coeffY: 0, sense: ConstraintSense.GE, rhs: 0 },
    ];
    const result = decodeModel(encodeModel(minObj, cs));
    expect(result!.objective.sense).toBe(ObjectiveSense.MIN);
    expect(result!.objective.coeffX).toBeCloseTo(3);
    expect(result!.objective.coeffY).toBeCloseTo(-2);
  });

  it('round-trips negative coefficients without sign loss', () => {
    const decoded = decodeModel(encodeModel(obj, constraints));
    expect(decoded!.constraints[2].coeffX).toBeCloseTo(-1);
    expect(decoded!.constraints[3].coeffY).toBeCloseTo(-2);
  });

  it('round-trips all three constraint senses (LE, GE, EQ)', () => {
    const cs: Constraint[] = [
      { id: crypto.randomUUID(), coeffX: 1, coeffY: 0, sense: ConstraintSense.LE, rhs: 1 },
      { id: crypto.randomUUID(), coeffX: 0, coeffY: 1, sense: ConstraintSense.GE, rhs: 0 },
      { id: crypto.randomUUID(), coeffX: 1, coeffY: 1, sense: ConstraintSense.EQ, rhs: 3 },
    ];
    const decoded = decodeModel(encodeModel(obj, cs));
    expect(decoded!.constraints[0].sense).toBe(ConstraintSense.LE);
    expect(decoded!.constraints[1].sense).toBe(ConstraintSense.GE);
    expect(decoded!.constraints[2].sense).toBe(ConstraintSense.EQ);
  });
});

// ── Malformed input → null ────────────────────────────────────────────────────

describe('URL codec — malformed input returns null', () => {
  it('returns null for empty params', () => {
    expect(decodeModel(new URLSearchParams(''))).toBeNull();
  });

  it('returns null when objective sense param is missing', () => {
    const p = encodeModel(obj, constraints);
    p.delete('os');
    expect(decodeModel(p)).toBeNull();
  });

  it('returns null when ox param is missing', () => {
    const p = encodeModel(obj, constraints);
    p.delete('ox');
    expect(decodeModel(p)).toBeNull();
  });

  it('returns null when oy param is missing', () => {
    const p = encodeModel(obj, constraints);
    p.delete('oy');
    expect(decodeModel(p)).toBeNull();
  });

  it('returns null when no constraint params are present', () => {
    const p = new URLSearchParams('os=max&ox=1&oy=1');
    expect(decodeModel(p)).toBeNull();
  });

  it('returns null for an unrecognised objective sense code', () => {
    const p = encodeModel(obj, constraints);
    p.set('os', 'MAX');   // must be lowercase 'max'
    expect(decodeModel(p)).toBeNull();
  });

  it('returns null for an unrecognised constraint sense code', () => {
    // Craft a bad constraint segment manually
    const p = new URLSearchParams('os=max&ox=1&oy=1&c=1,1,lte,5');
    expect(decodeModel(p)).toBeNull();
  });

  it('returns null for a constraint segment with wrong field count', () => {
    const p = new URLSearchParams('os=max&ox=1&oy=1&c=1,1,le');  // missing rhs
    expect(decodeModel(p)).toBeNull();
  });

  it('returns null when a coefficient is NaN', () => {
    const p = new URLSearchParams('os=max&ox=abc&oy=1&c=1,1,le,5');
    expect(decodeModel(p)).toBeNull();
  });

  it('returns null when a coefficient is Infinity', () => {
    const p = new URLSearchParams('os=max&ox=Infinity&oy=1&c=1,1,le,5');
    expect(decodeModel(p)).toBeNull();
  });
});

// ── Browser-aware helpers ─────────────────────────────────────────────────────

describe('readModelFromUrl / writeModelToUrl', () => {
  it('readModelFromUrl reads from window.location.search', () => {
    const params = encodeModel(obj, constraints);
    Object.defineProperty(window, 'location', {
      value: { ...window.location, search: `?${params.toString()}` },
      writable: true,
    });
    const result = readModelFromUrl();
    expect(result).not.toBeNull();
    expect(result!.objective.sense).toBe(obj.sense);
  });

  it('writeModelToUrl updates the URL without a full page navigation', () => {
    const cs: Constraint[] = [
      { id: crypto.randomUUID(), coeffX: 1, coeffY: 0, sense: ConstraintSense.LE, rhs: 5 },
    ];
    writeModelToUrl(obj, cs);
    const p = new URLSearchParams(window.location.search);
    expect(p.get('os')).toBe(obj.sense);
    expect(p.get('ox')).toBe(String(obj.coeffX));
  });
});
