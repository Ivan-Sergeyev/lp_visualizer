import type { Data, Layout, Shape, Annotations } from 'plotly.js';
import { OptimizerStatus } from './types';
import type { Constraint, LPResult, Objective } from './types';
import { lineBoxedEndpoints, objectiveUnitVector } from './geometry';

export const X_RANGE: [number, number] = [-1, 6];
export const Y_RANGE: [number, number] = [-1, 4];

const BL = { x: X_RANGE[0], y: Y_RANGE[0] };
const TR = { x: X_RANGE[1], y: Y_RANGE[1] };

const CONSTRAINT_COLORS = [
  '#60a5fa','#a78bfa','#34d399','#fb923c','#f472b6','#38bdf8','#facc15',
];

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

function objectiveAnnotation(obj: Objective): Partial<Annotations> {
  const tip = objectiveUnitVector(obj);
  return {
    arrowcolor: '#fbbf24',
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

export interface PlotlyFigure {
  data:   Partial<Data>[];
  layout: Partial<Layout>;
  config: object;
}

export function buildFigure(
  objective: Objective,
  constraints: Constraint[],
  result: LPResult,
): PlotlyFigure {
  const data: Partial<Data>[] = [];
  if (result.status === OptimizerStatus.OPTIMAL && result.solution) {
    const [x, y] = result.solution.point;
    data.push({
      type: 'scatter',
      x: [x], y: [y],
      mode: 'markers',
      marker: { color: '#4ade80', size: 14, symbol: 'circle', line: { color: '#0f1117', width: 2 } },
      hovertemplate: `<b>Optimal</b><br>x = ${x.toFixed(3)}<br>y = ${y.toFixed(3)}<extra></extra>`,
      showlegend: false,
    } as Partial<Data>);
  }

  const layout: Partial<Layout> = {
    paper_bgcolor: '#161b22',
    plot_bgcolor:  '#0d1117',
    xaxis: {
      range: X_RANGE,
      gridcolor: '#1e2733', zerolinecolor: '#30363d',
      tickfont: { color: '#8b949e', family: "'IBM Plex Mono', monospace", size: 11 },
      linecolor: '#30363d',
      title: { text: 'x', font: { color: '#8b949e', family: "'EB Garamond', serif", size: 14 } },
    },
    yaxis: {
      range: Y_RANGE,
      gridcolor: '#1e2733', zerolinecolor: '#30363d',
      tickfont: { color: '#8b949e', family: "'IBM Plex Mono', monospace", size: 11 },
      linecolor: '#30363d',
      title: { text: 'y', font: { color: '#8b949e', family: "'EB Garamond', serif", size: 14 } },
    },
    shapes:      constraints.map((c, i) => constraintShape(c, i)),
    annotations: [objectiveAnnotation(objective)],
    margin: { l: 52, r: 24, t: 24, b: 52 },
    dragmode: 'pan',
    hoverlabel: { bgcolor: '#1c2333', bordercolor: '#30363d', font: { color: '#e6edf3' } },
  };

  const config = {
    displayModeBar: true,
    modeBarButtonsToRemove: ['toImage', 'sendDataToCloud'],
    displaylogo: false,
    scrollZoom: true,
  };

  return { data, layout, config };
}
