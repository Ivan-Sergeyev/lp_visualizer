import { memo } from 'react';
import { CONSTRAINT_COLORS, OptimizerStatus, formatLinearExpr, isNonzeroConstraint } from '../types';
import type { Constraint, LPResult } from '../types';

interface LegendProps {
  constraints: Constraint[];
  result:      LPResult;
}

/**
 * Plot legend rendered below the Plotly chart.
 *
 * Shows one swatch + formula per constraint (colours match the plot lines).
 * Constraints with both coefficients equal to zero produce no line on the plot
 * — they are shown as a dimmed entry with a tooltip explaining why they are
 * absent, using user-friendly language rather than the internal term "trivial".
 * Negative coefficients are rendered with a proper minus sign via formatLinearExpr.
 *
 * Also shows a fixed amber swatch for the objective direction arrow and —
 * when the result is OPTIMAL — a green swatch for the optimal point marker.
 *
 * Memoised: re-renders only when constraints or result change.
 */
export const Legend = memo(function Legend({ constraints, result }: LegendProps) {
  return (
    <div className="legend">
      {constraints.map((c, i) => {
        const hasLine = isNonzeroConstraint(c);
        const color   = CONSTRAINT_COLORS[i % CONSTRAINT_COLORS.length];
        return (
          <span
            key={c.id}
            className={`legend-item${hasLine ? '' : ' legend-item--no-line'}`}
            title={hasLine ? undefined : 'Both coefficients are zero — no line on the plot'}
          >
            <span
              className="legend-swatch"
              style={{ background: color, opacity: hasLine ? 1 : 0.25 }}
            />
            <span className="legend-text">
              {hasLine
                ? `${formatLinearExpr(c.coeffX, c.coeffY)} ${c.sense} ${c.rhs}`
                : `(no line) 0 ${c.sense} ${c.rhs}`}
            </span>
          </span>
        );
      })}

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
