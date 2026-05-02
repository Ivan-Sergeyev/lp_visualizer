import { memo, useCallback } from 'react';
import { CONSTRAINT_COLORS } from '../types';
import { CONSTRAINT_SENSES, ConstraintSense, parseConstraintSense } from '../types';
import type { Constraint } from '../types';
import { NumberInput } from './NumberInput';

interface ConstraintRowProps {
  constraint: Constraint;
  index:      number;       // position in the constraints array; drives the colour dot
  onChange:   (c: Constraint) => void;
  onRemove:   () => void;
}

/**
 * Maps each sense symbol to a distinct colour for the sense <select> element.
 * Kept separate from CONSTRAINT_COLORS (which cycles by index) because the
 * sense colour is a fixed semantic cue, not a positional one.
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
 * Memoised: re-renders only when its own constraint, index, or callbacks change.
 */
export const ConstraintRow = memo(function ConstraintRow({
  constraint,
  index,
  onChange,
  onRemove,
}: ConstraintRowProps) {
  const dotColor = CONSTRAINT_COLORS[index % CONSTRAINT_COLORS.length];

  const handleSenseChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      onChange({ ...constraint, sense: parseConstraintSense(e.target.value) });
    },
    [constraint, onChange],
  );

  return (
    <div className="constraint-row">
      <span className="constraint-dot" style={{ background: dotColor }} />
      <NumberInput
        className="coeff-input"
        value={constraint.coeffX}
        onChange={v => onChange({ ...constraint, coeffX: v })}
        placeholder="cx"
        step={0.5}
      />
      <span className="var-label">x</span>
      <span className="sign-label">+</span>
      <NumberInput
        className="coeff-input"
        value={constraint.coeffY}
        onChange={v => onChange({ ...constraint, coeffY: v })}
        placeholder="cy"
        step={0.5}
      />
      <span className="var-label">y</span>
      <select
        className="sense-select sense-select--sm"
        value={constraint.sense}
        style={{ color: SENSE_COLORS[constraint.sense] }}
        onChange={handleSenseChange}
      >
        {CONSTRAINT_SENSES.map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>
      <NumberInput
        className="coeff-input"
        value={constraint.rhs}
        onChange={v => onChange({ ...constraint, rhs: v })}
        placeholder="rhs"
        step={0.5}
      />
      <button className="btn btn--remove" title="Remove constraint" onClick={onRemove}>
        ×
      </button>
    </div>
  );
});
