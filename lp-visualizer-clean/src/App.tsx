import { useEffect, useMemo, useRef, useState } from 'react';
// @ts-ignore – types come from @types/plotly.js
import Plotly from 'plotly.js-dist-min';

import { ObjectiveForm } from './components/ObjectiveForm';
import { ConstraintRow }  from './components/ConstraintRow';
import { buildFigure }   from './graph';
import { solveLp }       from './simplex';
import {
  ConstraintSense,
  defaultConstraint,
  ObjectiveSense,
  OptimizerStatus,
  resultLabel,
} from './types';
import type { Constraint, LPResult, Objective } from './types';

const DEFAULT_OBJECTIVE: Objective = {
  sense:  ObjectiveSense.MAX,
  coeffX: 6,
  coeffY: 9,
};

const DEFAULT_CONSTRAINTS: Constraint[] = [
  { id: '0', coeffX: 2, coeffY: 3, sense: ConstraintSense.LE, rhs: 12 },
  { id: '1', coeffX: 1, coeffY: 1, sense: ConstraintSense.LE, rhs: 5  },
  { id: '2', coeffX: 1, coeffY: 0, sense: ConstraintSense.GE, rhs: 0  },
  { id: '3', coeffX: 0, coeffY: 1, sense: ConstraintSense.GE, rhs: 0  },
];

function statusColor(status: OptimizerStatus): string {
  switch (status) {
    case OptimizerStatus.OPTIMAL:    return 'var(--green)';
    case OptimizerStatus.INFEASIBLE: return 'var(--red)';
    case OptimizerStatus.UNBOUNDED:  return 'var(--amber)';
    default:                         return 'var(--muted)';
  }
}

const DOT_COLORS = ['#60a5fa','#a78bfa','#34d399','#fb923c','#f472b6','#38bdf8','#facc15'];

let idCounter = DEFAULT_CONSTRAINTS.length;
function nextId(): string { return String(idCounter++); }

export default function App() {
  const [objective,   setObjective]   = useState<Objective>(DEFAULT_OBJECTIVE);
  const [constraints, setConstraints] = useState<Constraint[]>(DEFAULT_CONSTRAINTS);

  const result = useMemo<LPResult>(
    () => solveLp(objective, constraints),
    [objective, constraints],
  );

  const figure = useMemo(
    () => buildFigure(objective, constraints, result),
    [objective, constraints, result],
  );

  const plotRef     = useRef<HTMLDivElement>(null);
  const initialised = useRef(false);

  useEffect(() => {
    if (!plotRef.current) return;
    const { data, layout, config } = figure;
    if (!initialised.current) {
      Plotly.newPlot(plotRef.current, data, layout, config);
      initialised.current = true;
    } else {
      Plotly.react(plotRef.current, data, layout, config);
    }
  }, [figure]);

  // Resize the plot when the window resizes
  useEffect(() => {
    function handleResize() {
      if (plotRef.current) Plotly.relayout(plotRef.current, {});
    }
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  function addConstraint() {
    setConstraints(prev => [...prev, defaultConstraint(nextId())]);
  }
  function updateConstraint(id: string, updated: Constraint) {
    setConstraints(prev => prev.map(c => c.id === id ? updated : c));
  }
  function removeConstraint(id: string) {
    setConstraints(prev => {
      if (prev.length <= 1) return [defaultConstraint(nextId())];
      return prev.filter(c => c.id !== id);
    });
  }

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

        <section className="section section--constraints">
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
        <div className="legend">
          {constraints.map((c, i) => (
            <span key={c.id} className="legend-item">
              <span className="legend-swatch" style={{ background: DOT_COLORS[i % DOT_COLORS.length] }} />
              <span style={{ color: 'var(--muted)' }}>
                {c.coeffX}x + {c.coeffY}y {c.sense} {c.rhs}
              </span>
            </span>
          ))}
          <span className="legend-item">
            <span className="legend-swatch" style={{ background: '#fbbf24', height: '2px', borderRadius: 0 }} />
            <span style={{ color: 'var(--muted)' }}>Objective direction</span>
          </span>
          {result.status === OptimizerStatus.OPTIMAL && (
            <span className="legend-item">
              <span className="legend-swatch legend-swatch--circle" style={{ background: '#4ade80' }} />
              <span style={{ color: '#4ade80' }}>Optimal point</span>
            </span>
          )}
        </div>
      </main>
    </div>
  );
}
