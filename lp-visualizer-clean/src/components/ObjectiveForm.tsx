import { OBJECTIVE_SENSES, ObjectiveSense } from '../types';
import type { Objective } from '../types';
import { NumberInput } from './NumberInput';

interface ObjectiveFormProps {
  objective: Objective;
  onChange: (o: Objective) => void;
}

export function ObjectiveForm({ objective, onChange }: ObjectiveFormProps) {
  return (
    <div className="objective-row">
      <select
        className="sense-select"
        value={objective.sense}
        onChange={e => onChange({ ...objective, sense: e.target.value as ObjectiveSense })}
      >
        {OBJECTIVE_SENSES.map(s => (
          <option key={s} value={s}>{s.toUpperCase()}</option>
        ))}
      </select>
      <NumberInput
        className="coeff-input"
        value={objective.coeffX}
        onChange={v => onChange({ ...objective, coeffX: v })}
        placeholder="cx"
        step={0.5}
      />
      <span className="var-label">x</span>
      <span className="sign-label">+</span>
      <NumberInput
        className="coeff-input"
        value={objective.coeffY}
        onChange={v => onChange({ ...objective, coeffY: v })}
        placeholder="cy"
        step={0.5}
      />
      <span className="var-label">y</span>
    </div>
  );
}
