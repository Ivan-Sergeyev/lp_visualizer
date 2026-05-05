import { useCallback, useEffect, useMemo, useState } from 'react';

import { ObjectiveForm } from './components/ObjectiveForm';
import { ConstraintRow }  from './components/ConstraintRow';
import { Legend }         from './components/Legend';
import { buildData, buildLayout, isOutOfViewport, PLOT_CONFIG } from './graph';
import { usePlot }        from './components/usePlot';
import { solveLp }        from './simplex';
import { readModelFromUrl, writeModelToUrl } from './url';
import {
  ConstraintSense,
  defaultConstraint,
  ObjectiveSense,
  OptimizerStatus,
  resultLabel,
} from './types';
import type { Constraint, LPResult, Objective } from './types';

// ── Default model ─────────────────────────────────────────────────────────────

// A small bounded LP with a clean optimal solution at (3, 2) with value 32.
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

// readModelFromUrl() is safe in non-browser environments (returns null there).
const urlModel = readModelFromUrl();
const INITIAL_OBJECTIVE   = urlModel?.objective   ?? DEFAULT_OBJECTIVE;
const INITIAL_CONSTRAINTS = urlModel?.constraints ?? DEFAULT_CONSTRAINTS;

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
  const [objective,   setObjective]   = useState<Objective>(INITIAL_OBJECTIVE);
  const [constraints, setConstraints] = useState<Constraint[]>(INITIAL_CONSTRAINTS);

  // Sync model to URL query string on every change so the page can be bookmarked
  // or shared. replaceState keeps the history stack clean.
  useEffect(() => {
    writeModelToUrl(objective, constraints);
  }, [objective, constraints]);

  // Solve on every model change. solveLp is pure and fast for synchronous execution.
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
  const data = useMemo(() => buildData(result), [result]);

  const plotRef = usePlot(data, layout, PLOT_CONFIG);

  // ── Constraint callbacks ──────────────────────────────────────────────────────
  // Stable refs (empty deps + functional state updates). ConstraintRow derives its
  // own per-input handlers via useCallback keyed on these stable refs.

  const addConstraint = useCallback(() => {
    setConstraints(prev => [...prev, defaultConstraint(crypto.randomUUID())]);
  }, []);

  // Accepts the full updated Constraint; id is read from updated.id.
  // This removes the redundant (id, c) pair — the constraint already carries its id.
  const updateConstraint = useCallback((updated: Constraint) => {
    setConstraints(prev => prev.map(c => c.id === updated.id ? updated : c));
  }, []);

  // When the last constraint is removed, reset it to a default row rather than
  // producing an empty list, which the solver and plot do not handle.
  const removeConstraint = useCallback((id: string) => {
    setConstraints(prev => {
      if (prev.length <= 1) return [defaultConstraint(crypto.randomUUID())];
      return prev.filter(c => c.id !== id);
    });
  }, []);

  // ── Out-of-viewport warning ───────────────────────────────────────────────────
  const outOfViewport =
    result.status === OptimizerStatus.OPTIMAL &&
    result.solution !== null &&
    isOutOfViewport(result.solution.point);

  return (
    <div className="app-wrapper">

      {/* ── LEFT PANEL ── */}
      <aside className="left-panel">
        <div className="panel-header">
          <span className="panel-title">LP Visualiser</span>
          <span className="panel-subtitle">2-variable linear programs</span>
        </div>

        <section className="section" aria-labelledby="section-objective">
          <div id="section-objective" className="section-label">Objective</div>
          <ObjectiveForm objective={objective} onChange={setObjective} />
        </section>

        <section className="section" aria-labelledby="section-constraints">
          <div id="section-constraints" className="section-label">Subject to</div>
          <div className="constraints-list">
            {constraints.map((c, i) => (
              <ConstraintRow
                key={c.id}
                constraint={c}
                index={i}
                onChange={updateConstraint}
                onRemove={removeConstraint}
              />
            ))}
          </div>
          <button className="btn btn--add" onClick={addConstraint}>
            <span className="btn-icon">+</span> Add constraint
          </button>
        </section>

        <section className="section" aria-labelledby="section-result">
          <div id="section-result" className="section-label">Result</div>
          <div
            className="result-box"
            role="status"
            aria-live="polite"
            style={{ borderColor: statusColor(result.status), color: statusColor(result.status) }}
          >
            <span className="result-status">{result.status.toUpperCase()}</span>
            <span className="result-detail">{resultLabel(result)}</span>
          </div>
          {outOfViewport && (
            <div className="warning-box" role="alert">
              Optimal point is outside the visible plot area — try zooming out or panning.
            </div>
          )}
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
