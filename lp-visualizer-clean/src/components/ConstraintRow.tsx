import { ConstraintSense, CONSTRAINT_SENSES } from '../types';
import type { Constraint } from '../types';
import { NumberInput } from './NumberInput';

interface ConstraintRowProps {
  constraint: Constraint;
  index: number;
  onChange: (c: Constraint) => void;
  onRemove: () => void;
}

const SENSE_COLORS: Record<ConstraintSense, string> = {
  [ConstraintSense.LE]: '#60a5fa',
  [ConstraintSense.GE]: '#a78bfa',
  [ConstraintSense.EQ]: '#34d399',
};

const DOT_COLORS = ['#60a5fa','#a78bfa','#34d399','#fb923c','#f472b6','#38bdf8','#facc15'];

export function ConstraintRow({ constraint, index, onChange, onRemove }: ConstraintRowProps) {
  const dotColor = DOT_COLORS[index % DOT_COLORS.length];

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
        onChange={e => onChange({ ...constraint, sense: e.target.value as ConstraintSense })}
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
      <button className="btn btn--remove" title="Remove constraint" onClick={onRemove}>×</button>
    </div>
  );
}
