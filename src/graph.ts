import type { Config, Data, Layout, Shape, Annotations } from 'plotly.js';
import { OptimizerStatus, CONSTRAINT_COLORS, EPSILON, isNonzeroConstraint } from './types';
import type { Constraint, LPResult, Objective } from './types';
import { lineBoxedEndpoints, objectiveUnitVector } from './geometry';

// ── Viewport ──────────────────────────────────────────────────────────────────

/**
 * Fixed plot bounds. Constraint lines are clipped to this region.
 * Also imported by simplex.test.ts to check that solutions lie within the viewport.
 */
export const X_RANGE: [number, number] = [-1, 6];
export const Y_RANGE: [number, number] = [-1, 4];

const BL = { x: X_RANGE[0], y: Y_RANGE[0] };
const TR = { x: X_RANGE[1], y: Y_RANGE[1] };

/**
 * Returns true when the point lies outside the visible plot viewport.
 * Used to display a warning when the optimal solution is off-screen.
 */
export function isOutOfViewport(point: [number, number]): boolean {
  const [x, y] = point;
  return x < X_RANGE[0] || x > X_RANGE[1] || y < Y_RANGE[0] || y > Y_RANGE[1];
}

// ── Static Plotly config ──────────────────────────────────────────────────────

/**
 * Plotly theme tokens — kept in sync with the CSS custom properties in index.css.
 * Centralised here so a palette change requires editing a single object, not
 * hunting down scattered hex literals throughout buildLayout.
 */
const THEME = {
  bgPaper:  '#161b22',               // --surface
  bgPlot:   '#0d1117',               // --bg
  grid:     '#1e2733',
  zeroline: '#30363d',               // --border2
  tick:     '#8b949e',               // --muted
  fontMono: "'IBM Plex Mono', monospace",  // --font-mono
  fontSer:  "'EB Garamond', serif",        // --font-ser
  hover:    { bg: '#1c2333', border: '#30363d', text: '#e6edf3' },
  amber:    '#fbbf24',
} as const;

/**
 * Plotly UI config shared across all renders.
 * 'toImage' and 'sendDataToCloud' are removed from the modebar as they are not
 * useful here; scroll-to-zoom is enabled for interactive exploration.
 */
export const PLOT_CONFIG: Partial<Config> = {
  displayModeBar: true,
  modeBarButtonsToRemove: ['toImage', 'sendDataToCloud'],
  displaylogo: false,
  scrollZoom: true,
};

// ── Shape / annotation builders ───────────────────────────────────────────────

/** Builds a Plotly line shape for one constraint, clipped to the viewport. */
function constraintShape(c: Constraint, index: number): Partial<Shape> {
  const line = { x: c.coeffX, y: c.coeffY, rhs: c.rhs };
  const [p1, p2] = lineBoxedEndpoints(line, BL, TR);
  const color = CONSTRAINT_COLORS[index % CONSTRAINT_COLORS.length];
  return {
    type: 'line',
    xref: 'x', yref: 'y',
    x0: p1.x, y0: p1.y,
    x1: p2.x, y1: p2.y,
    line: { color, width: 2.5 },
  } as Partial<Shape>;
}

/** Builds the amber arrow annotation that shows the objective direction. */
function objectiveAnnotation(obj: Objective): Partial<Annotations> {
  const tip = objectiveUnitVector(obj);
  return {
    arrowcolor: THEME.amber,
    arrowhead: 3,
    arrowwidth: 2.5,
    showarrow: true,
    text: '',
    axref: 'x', ayref: 'y',
    xref:  'x',  yref: 'y',
    ax: 0, ay: 0,
    x: tip.x, y: tip.y,
  };
}

// ── Public figure builders ────────────────────────────────────────────────────

/**
 * Builds the Plotly layout (axes, constraint lines, objective arrow) from the
 * current LP definition. Memoised independently of the solver result so it only
 * recomputes when the objective or constraints change.
 *
 * Trivial constraints (both coefficients zero) are excluded from `shapes` —
 * they produce no line on the plot. The objective arrow annotation is suppressed
 * when the objective vector is zero (no meaningful direction to show).
 */
export function buildLayout(
  objective: Objective,
  constraints: Constraint[],
): Partial<Layout> {
  // Pre-compute the objective direction to decide whether to show the arrow.
  // The zero check mirrors isNonzeroConstraint: both use EPSILON for consistency.
  const tip          = objectiveUnitVector(objective);
  const showArrow    = Math.abs(tip.x) > EPSILON || Math.abs(tip.y) > EPSILON;

  // Filter trivial constraints but preserve original indices so shape colours
  // stay in sync with the legend (which colours by position in the full array).
  const nonTrivial = constraints
    .map((c, i) => ({ c, i }))
    .filter(({ c }) => isNonzeroConstraint(c));

  return {
    paper_bgcolor: THEME.bgPaper,
    plot_bgcolor:  THEME.bgPlot,
    xaxis: {
      range: X_RANGE,
      gridcolor:    THEME.grid,
      zerolinecolor: THEME.zeroline,
      linecolor:     THEME.zeroline,
      tickfont: { color: THEME.tick, family: THEME.fontMono, size: 11 },
      title: { text: 'x', font: { color: THEME.tick, family: THEME.fontSer, size: 14 } },
    },
    yaxis: {
      range: Y_RANGE,
      gridcolor:    THEME.grid,
      zerolinecolor: THEME.zeroline,
      linecolor:     THEME.zeroline,
      tickfont: { color: THEME.tick, family: THEME.fontMono, size: 11 },
      title: { text: 'y', font: { color: THEME.tick, family: THEME.fontSer, size: 14 } },
    },
    shapes:      nonTrivial.map(({ c, i }) => constraintShape(c, i)),
    annotations: showArrow ? [objectiveAnnotation(objective)] : [],
    margin:   { l: 52, r: 24, t: 24, b: 52 },
    dragmode: 'pan',
    hoverlabel: {
      bgcolor:     THEME.hover.bg,
      bordercolor: THEME.hover.border,
      font: { color: THEME.hover.text },
    },
  };
}

/**
 * Builds the Plotly data traces from the solver result. Returns an empty array
 * unless the result is OPTIMAL, in which case it returns a single green circle
 * marker at the optimal point. Memoised independently of the layout so it only
 * recomputes when the result changes.
 */
export function buildData(result: LPResult): Partial<Data>[] {
  if (result.status !== OptimizerStatus.OPTIMAL || !result.solution) return [];
  const [x, y] = result.solution.point;
  return [{
    type: 'scatter',
    x: [x], y: [y],
    mode: 'markers',
    marker: { color: '#4ade80', size: 14, symbol: 'circle', line: { color: '#0f1117', width: 2 } },
    // Plotly format directives keep the template a stable string constant — values
    // are injected by Plotly at hover time rather than baked in at render time.
    hovertemplate: '<b>Optimal</b><br>x = %{x:.3f}<br>y = %{y:.3f}<extra></extra>',
    showlegend: false,
  } as Partial<Data>];
}
