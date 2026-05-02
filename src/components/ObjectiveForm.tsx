import { memo, useCallback } from 'react';
import { OBJECTIVE_SENSES, parseObjectiveSense } from '../types';
import type { Objective } from '../types';
import { NumberInput } from './NumberInput';

interface ObjectiveFormProps {
  objective: Objective;
  onChange:  (o: Objective) => void;
}

/**
 * The objective function editor: [MIN|MAX] [cx] x + [cy] y
 *
 * The sense dropdown updates immediately; coefficient inputs use NumberInput
 * for deferred-commit behaviour (blur or Enter to propagate).
 *
 * Memoised: re-renders only when objective or onChange changes.
 */
export const ObjectiveForm = memo(function ObjectiveForm({
  objective,
  onChange,
}: ObjectiveFormProps) {
  const handleSenseChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      onChange({ ...objective, sense: parseObjectiveSense(e.target.value) });
    },
    [objective, onChange],
  );

  return (
    <div className="objective-row">
      <select
        className="sense-select"
        value={objective.sense}
        onChange={handleSenseChange}
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
});
