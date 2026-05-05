import { memo, useCallback } from 'react';
import { CONSTRAINT_COLORS, CONSTRAINT_SENSES, ConstraintSense, parseConstraintSense } from '../types';
import type { Constraint } from '../types';
import { NumberInput } from './NumberInput';

export interface ConstraintRowProps {
  constraint: Constraint;
  index:      number;         // position in the constraints array; drives the colour dot
  onChange:   (c: Constraint) => void;  // stable ref from App — constraint carries its own id
  onRemove:   (id: string) => void;     // stable ref from App
}

/**
 * Maps each sense symbol to a fixed semantic colour for the sense <select> element.
 * These are intentionally independent of CONSTRAINT_COLORS (which cycles by row index)
 * because the sense colour is a fixed semantic cue rather than a positional one.
 * The first three entries happen to share the same hex values as CONSTRAINT_COLORS[0–2],
 * but they are declared separately to make the semantic distinction explicit.
 */
const SENSE_COLORS: Record<ConstraintSense, string> = {
  [ConstraintSense.LE]: '#60a5fa',
  [ConstraintSense.GE]: '#a78bfa',
  [ConstraintSense.EQ]: '#34d399',
};

/**
 * A single constraint row: [●] [cx] x + [cy] y [sense] [rhs] [×]
 *
 * The coloured dot matches the corresponding line on the plot. Coefficient and
 * RHS inputs use NumberInput for deferred-commit behaviour. The sense dropdown
 * updates immediately (no ambiguous partial state).
 *
 * `onChange` accepts the full updated constraint (which carries its own id), so
 * no redundant `(id, c)` pair is needed. All internal callbacks are derived via
 * `useCallback` so the memo actually prevents unnecessary NumberInput re-renders.
 */
export const ConstraintRow = memo(function ConstraintRow({
  constraint,
  index,
  onChange,
  onRemove,
}: ConstraintRowProps) {
  const { id, coeffX, coeffY, sense, rhs } = constraint;
  const dotColor = CONSTRAINT_COLORS[index % CONSTRAINT_COLORS.length];

  const handleCoeffX = useCallback(
    (v: number) => onChange({ ...constraint, coeffX: v }),
    [constraint, onChange],
  );
  const handleCoeffY = useCallback(
    (v: number) => onChange({ ...constraint, coeffY: v }),
    [constraint, onChange],
  );
  const handleRhs = useCallback(
    (v: number) => onChange({ ...constraint, rhs: v }),
    [constraint, onChange],
  );
  const handleSenseChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      onChange({ ...constraint, sense: parseConstraintSense(e.target.value) });
    },
    [constraint, onChange],
  );
  const handleRemove = useCallback(() => onRemove(id), [id, onRemove]);

  return (
    <div className="constraint-row">
      <span className="constraint-dot" style={{ background: dotColor }} aria-hidden="true" />
      <NumberInput
        className="coeff-input"
        value={coeffX}
        onChange={handleCoeffX}
        aria-label={`Constraint ${index + 1} x coefficient`}
        placeholder="cx"
        step={0.5}
      />
      <span className="var-label" aria-hidden="true">x</span>
      <span className="sign-label" aria-hidden="true">+</span>
      <NumberInput
        className="coeff-input"
        value={coeffY}
        onChange={handleCoeffY}
        aria-label={`Constraint ${index + 1} y coefficient`}
        placeholder="cy"
        step={0.5}
      />
      <span className="var-label" aria-hidden="true">y</span>
      <select
        className="sense-select sense-select--sm"
        value={sense}
        style={{ color: SENSE_COLORS[sense] }}
        onChange={handleSenseChange}
        aria-label={`Constraint ${index + 1} inequality sense`}
      >
        {CONSTRAINT_SENSES.map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>
      <NumberInput
        className="coeff-input"
        value={rhs}
        onChange={handleRhs}
        aria-label={`Constraint ${index + 1} right-hand side`}
        placeholder="rhs"
        step={0.5}
      />
      <button
        className="btn btn--remove"
        aria-label={`Remove constraint ${index + 1}`}
        onClick={handleRemove}
      >
        ×
      </button>
    </div>
  );
});
