/**
 * URL codec — serialises/deserialises the LP model to/from the query string so
 * users can share or bookmark a specific problem.
 *
 * Format: ?os=max&ox=6&oy=7&c=2,3,le,12&c=1,1,le,5&…
 * Sense codes: le=≤  ge=≥  eq==
 *
 * All functions are pure (except readModelFromUrl / writeModelToUrl which access
 * `window`) and safe to call in non-browser environments (they return null / no-op).
 */

import { ConstraintSense, parseObjectiveSense } from './types';
import type { Constraint, Objective } from './types';

// ── Sense ↔ URL-code maps ──────────────────────────────────────────────────────

const SENSE_TO_CODE: Record<string, string> = {
  [ConstraintSense.LE]: 'le',
  [ConstraintSense.GE]: 'ge',
  [ConstraintSense.EQ]: 'eq',
};

const CODE_TO_SENSE: Record<string, ConstraintSense> = {
  le: ConstraintSense.LE,
  ge: ConstraintSense.GE,
  eq: ConstraintSense.EQ,
};

// ── Encode ────────────────────────────────────────────────────────────────────

/** Serialises an objective and constraint list into a URLSearchParams object. */
export function encodeModel(obj: Objective, constraints: Constraint[]): URLSearchParams {
  const p = new URLSearchParams();
  p.set('os', obj.sense);
  p.set('ox', String(obj.coeffX));
  p.set('oy', String(obj.coeffY));
  for (const c of constraints) {
    p.append('c', `${c.coeffX},${c.coeffY},${SENSE_TO_CODE[c.sense]},${c.rhs}`);
  }
  return p;
}

// ── Decode ────────────────────────────────────────────────────────────────────

/**
 * Parses a URLSearchParams object into a model. Returns null if any required
 * parameter is absent, malformed, or contains a non-finite number. Errors are
 * swallowed — the caller falls back to defaults silently.
 */
export function decodeModel(
  p: URLSearchParams,
): { objective: Objective; constraints: Constraint[] } | null {
  try {
    const os = p.get('os');
    const ox = p.get('ox');
    const oy = p.get('oy');
    if (!os || ox === null || oy === null) return null;

    const objective: Objective = {
      sense:  parseObjectiveSense(os),  // throws on unrecognised sense
      coeffX: Number(ox),
      coeffY: Number(oy),
    };
    if (!isFinite(objective.coeffX) || !isFinite(objective.coeffY)) return null;

    const cParams = p.getAll('c');
    if (cParams.length === 0) return null;

    const constraints: Constraint[] = cParams.map(cp => {
      const parts = cp.split(',');
      if (parts.length !== 4) throw new Error('bad constraint segment');
      const [cxStr, cyStr, sCode, rhsStr] = parts;
      const sense = CODE_TO_SENSE[sCode];
      if (!sense) throw new Error(`unknown sense code: ${sCode}`);
      const coeffX = Number(cxStr);
      const coeffY = Number(cyStr);
      const rhs    = Number(rhsStr);
      if (!isFinite(coeffX) || !isFinite(coeffY) || !isFinite(rhs)) {
        throw new Error('non-finite number');
      }
      return { id: crypto.randomUUID(), coeffX, coeffY, sense, rhs };
    });

    return { objective, constraints };
  } catch {
    return null;  // malformed URL — caller falls back to defaults
  }
}

// ── Browser-aware helpers ─────────────────────────────────────────────────────

/**
 * Reads the current URL search params and returns the decoded model.
 * Returns null if the URL contains no model, has malformed parameters,
 * or if called in a non-browser environment.
 */
export function readModelFromUrl(): ReturnType<typeof decodeModel> {
  if (typeof window === 'undefined') return null;
  return decodeModel(new URLSearchParams(window.location.search));
}

/**
 * Writes the model to the URL query string using `history.replaceState` so the
 * history stack stays clean. No-op in non-browser environments.
 */
export function writeModelToUrl(obj: Objective, constraints: Constraint[]): void {
  if (typeof window === 'undefined') return;
  const params = encodeModel(obj, constraints);
  window.history.replaceState(
    null,
    '',
    `${window.location.pathname}?${params.toString()}`,
  );
}
