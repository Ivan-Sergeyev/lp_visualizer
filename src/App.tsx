import { useCallback, useMemo, useState } from 'react';

import { ObjectiveForm } from './components/ObjectiveForm';
import { ConstraintRow }  from './components/ConstraintRow';
import { Legend }         from './components/Legend';
import { buildData, buildLayout, PLOT_CONFIG } from './graph';
import { usePlot }        from './components/usePlot';
import { solveLp }        from './simplex';
import {
  ConstraintSense,
  defaultConstraint,
  ObjectiveSense,
  OptimizerStatus,
  resultLabel,
} from './types';
import type { Constraint, LPResult, Objective } from './types';

// ── Default model ─────────────────────────────────────────────────────────────

// A small bounded LP that has a clean optimal solution at (3, 2) with value 32.
const DEFAULT_OBJECTIVE: Objective = {
  sense:  ObjectiveSense.MAX,
  coeffX: 6,
  coeffY: 7,
};

const DEFAULT_CONSTRAINTS: Constraint[] = [
  { id: crypto.randomUUID(), coeffX: 2, coeffY: 3, sense: ConstraintSense.LE, rhs: 12 },
  { id: crypto.randomUUID(), coeffX: 1, coeffY: 1, sense: ConstraintSense.LE, rhs: 5  },
  { id: crypto.randomUUID(), coeffX: 1, coeffY: 0, sense: ConstraintSense.GE, rhs: 0  },
  { id: crypto.randomUUID(), coeffX: 0, coeffY: 1, sense: ConstraintSense.GE, rhs: 0  },
];

// ── Helpers ───────────────────────────────────────────────────────────────────

/**
 * Maps solver status to a CSS custom property for the Result panel border/text.
 * References variables defined in index.css.
 */
function statusColor(status: OptimizerStatus): string {
  switch (status) {
    case OptimizerStatus.OPTIMAL:    return 'var(--green)';
    case OptimizerStatus.INFEASIBLE: return 'var(--red)';
    case OptimizerStatus.UNBOUNDED:  return 'var(--amber)';
    default:                         return 'var(--muted)';
  }
}

// ── App ───────────────────────────────────────────────────────────────────────

export default function App() {
  const [objective,   setObjective]   = useState<Objective>(DEFAULT_OBJECTIVE);
  const [constraints, setConstraints] = useState<Constraint[]>(DEFAULT_CONSTRAINTS);

  // Solve on every model change. solveLp is pure and fast enough for synchronous
  // execution; no debounce is needed at this scale.
  const result = useMemo<LPResult>(
    () => solveLp(objective, constraints),
    [objective, constraints],
  );

  // Build layout and data separately so each only recomputes when its inputs change.
  // Layout depends on the LP definition; data depends only on the solver result.
  const layout = useMemo(
    () => buildLayout(objective, constraints),
    [objective, constraints],
  );
  const data = useMemo(
    () => buildData(result),
    [result],
  );

  const plotRef = usePlot(data, layout, PLOT_CONFIG);

  // Stable callback references prevent unnecessary re-renders of memoised children.
  const addConstraint = useCallback(() => {
    setConstraints(prev => [...prev, defaultConstraint(crypto.randomUUID())]);
  }, []);

  const updateConstraint = useCallback((id: string, updated: Constraint) => {
    setConstraints(prev => prev.map(c => c.id === id ? updated : c));
  }, []);

  // When the last constraint is removed, reset it to a default row rather than
  // producing an empty list, which the solver and plot do not handle.
  const removeConstraint = useCallback((id: string) => {
    setConstraints(prev => {
      if (prev.length <= 1) return [defaultConstraint(crypto.randomUUID())];
      return prev.filter(c => c.id !== id);
    });
  }, []);

  return (
    <div className="app-wrapper">

      {/* ── LEFT PANEL ── */}
      <aside className="left-panel">
        <div className="panel-header">
          <span className="panel-title">LP Visualiser</span>
          <span className="panel-subtitle">2-variable linear programs</span>
        </div>

        <section className="section">
          <div className="section-label">Objective</div>
          <ObjectiveForm objective={objective} onChange={setObjective} />
        </section>

        <section className="section">
          <div className="section-label">Subject to</div>
          <div className="constraints-list">
            {constraints.map((c, i) => (
              <ConstraintRow
                key={c.id}
                constraint={c}
                index={i}
                onChange={updated => updateConstraint(c.id, updated)}
                onRemove={() => removeConstraint(c.id)}
              />
            ))}
          </div>
          <button className="btn btn--add" onClick={addConstraint}>
            <span className="btn-icon">+</span> Add constraint
          </button>
        </section>

        <section className="section">
          <div className="section-label">Result</div>
          <div
            className="result-box"
            style={{ borderColor: statusColor(result.status), color: statusColor(result.status) }}
          >
            <span className="result-status">{result.status.toUpperCase()}</span>
            <span className="result-detail">{resultLabel(result)}</span>
          </div>
        </section>
      </aside>

      {/* ── RIGHT PANEL ── */}
      <main className="right-panel">
        <div className="plot-container" ref={plotRef} />
        <Legend constraints={constraints} result={result} />
      </main>

    </div>
  );
}
