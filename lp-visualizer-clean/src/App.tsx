import { useCallback, useMemo, useState } from 'react';

import { ObjectiveForm } from './components/ObjectiveForm';
import { ConstraintRow }  from './components/ConstraintRow';
import { Legend }         from './components/Legend';
import { buildData, buildLayout, PLOT_CONFIG } from './graph';
import { usePlot }        from './hooks/usePlot';
import { solveLp }        from './simplex';
import {
  ConstraintSense,
  defaultConstraint,
  ObjectiveSense,
  OptimizerStatus,
  resultLabel,
} from './types';
import type { Constraint, LPResult, Objective } from './types';

// ── Defaults (match the original Python app) ──────────────────────────────────

const DEFAULT_OBJECTIVE: Objective = {
  sense:  ObjectiveSense.MAX,
  coeffX: 6,
  coeffY: 9,
};

const DEFAULT_CONSTRAINTS: Constraint[] = [
  { id: crypto.randomUUID(), coeffX: 2, coeffY: 3, sense: ConstraintSense.LE, rhs: 12 },
  { id: crypto.randomUUID(), coeffX: 1, coeffY: 1, sense: ConstraintSense.LE, rhs: 5  },
  { id: crypto.randomUUID(), coeffX: 1, coeffY: 0, sense: ConstraintSense.GE, rhs: 0  },
  { id: crypto.randomUUID(), coeffX: 0, coeffY: 1, sense: ConstraintSense.GE, rhs: 0  },
];

// ── Status colour (references CSS custom properties) ─────────────────────────

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

  // ── Solve ─────────────────────────────────────────────────────────────────

  const result = useMemo<LPResult>(
    () => solveLp(objective, constraints),
    [objective, constraints],
  );

  // ── Build figure pieces — memoised independently ──────────────────────────

  const layout = useMemo(
    () => buildLayout(objective, constraints),
    [objective, constraints],
  );
  const data = useMemo(
    () => buildData(result),
    [result],
  );

  // ── Drive Plotly via hook ─────────────────────────────────────────────────

  const plotRef = usePlot(data, layout, PLOT_CONFIG);

  // ── Constraint callbacks — stable references via useCallback ─────────────

  const addConstraint = useCallback(() => {
    setConstraints(prev => [...prev, defaultConstraint(crypto.randomUUID())]);
  }, []);

  const updateConstraint = useCallback((id: string, updated: Constraint) => {
    setConstraints(prev => prev.map(c => c.id === id ? updated : c));
  }, []);

  const removeConstraint = useCallback((id: string) => {
    setConstraints(prev => {
      if (prev.length <= 1) return [defaultConstraint(crypto.randomUUID())];
      return prev.filter(c => c.id !== id);
    });
  }, []);

  // ── Render ────────────────────────────────────────────────────────────────

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
