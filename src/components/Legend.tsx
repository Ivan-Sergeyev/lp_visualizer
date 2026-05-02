import { memo } from 'react';
import { CONSTRAINT_COLORS } from '../types';
import { OptimizerStatus } from '../types';
import type { Constraint, LPResult } from '../types';

interface LegendProps {
  constraints: Constraint[];
  result:      LPResult;
}

/**
 * Plot legend rendered below the Plotly chart.
 *
 * Shows one swatch + formula per constraint (colours match the plot lines),
 * a fixed amber swatch for the objective direction arrow, and — when the result
 * is OPTIMAL — a green swatch for the optimal point marker.
 *
 * Memoised: re-renders only when constraints or result change.
 */
export const Legend = memo(function Legend({ constraints, result }: LegendProps) {
  return (
    <div className="legend">
      {constraints.map((c, i) => (
        <span key={c.id} className="legend-item">
          <span
            className="legend-swatch"
            style={{ background: CONSTRAINT_COLORS[i % CONSTRAINT_COLORS.length] }}
          />
          <span className="legend-text">
            {c.coeffX}x + {c.coeffY}y {c.sense} {c.rhs}
          </span>
        </span>
      ))}

      <span className="legend-item">
        <span className="legend-swatch legend-swatch--line" />
        <span className="legend-text">Objective direction</span>
      </span>

      {result.status === OptimizerStatus.OPTIMAL && (
        <span className="legend-item">
          <span className="legend-swatch legend-swatch--circle legend-swatch--optimal" />
          <span className="legend-text legend-text--optimal">Optimal point</span>
        </span>
      )}
    </div>
  );
});
