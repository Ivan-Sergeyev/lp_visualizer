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
 * All internal callbacks are stabilised with useCallback so the memo actually
 * prevents NumberInput re-renders when only unrelated state changes.
 */
export const ObjectiveForm = memo(function ObjectiveForm({
  objective,
  onChange,
}: ObjectiveFormProps) {
  const { coeffX, coeffY, sense } = objective;

  const handleSenseChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      onChange({ ...objective, sense: parseObjectiveSense(e.target.value) });
    },
    [objective, onChange],
  );

  const handleCoeffX = useCallback(
    (v: number) => onChange({ ...objective, coeffX: v }),
    [objective, onChange],
  );

  const handleCoeffY = useCallback(
    (v: number) => onChange({ ...objective, coeffY: v }),
    [objective, onChange],
  );

  return (
    <div className="objective-row">
      <select
        className="sense-select"
        value={sense}
        onChange={handleSenseChange}
        aria-label="Objective sense"
      >
        {OBJECTIVE_SENSES.map(s => (
          <option key={s} value={s}>{s.toUpperCase()}</option>
        ))}
      </select>
      <NumberInput
        className="coeff-input"
        value={coeffX}
        onChange={handleCoeffX}
        aria-label="Objective x coefficient"
        placeholder="cx"
        step={0.5}
      />
      <span className="var-label" aria-hidden="true">x</span>
      <span className="sign-label" aria-hidden="true">+</span>
      <NumberInput
        className="coeff-input"
        value={coeffY}
        onChange={handleCoeffY}
        aria-label="Objective y coefficient"
        placeholder="cy"
        step={0.5}
      />
      <span className="var-label" aria-hidden="true">y</span>
    </div>
  );
});
