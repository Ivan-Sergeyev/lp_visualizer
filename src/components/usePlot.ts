import { useEffect, useRef } from 'react';
import type { RefObject } from 'react';
import type { Config, Data, Layout } from 'plotly.js';
import Plotly from 'plotly.js-dist-min';

/**
 * Manages the full Plotly lifecycle for a <div> ref:
 *  - `newPlot` on mount, `purge` on unmount (the purge cleanup makes React 18
 *    StrictMode's double-invoke safe — the second mount gets a clean element)
 *  - `Plotly.react` on every figure change (data / layout / config)
 *  - `Plotly.Plots.resize` on window resize (correct API; `relayout` would
 *    re-render all traces unnecessarily)
 */
export function usePlot(
  data:   Partial<Data>[],
  layout: Partial<Layout>,
  config: Partial<Config>,
): RefObject<HTMLDivElement | null> {
  const ref = useRef<HTMLDivElement>(null);

  // Mount-only effect: initialise Plotly on the first render and purge on unmount.
  // The purge in the cleanup makes React 18 StrictMode's double-invoke safe —
  // the second mount always gets a clean DOM element.
  //
  // data / layout / config are intentionally absent from the dep array.
  // Updates are handled entirely by the second effect (Plotly.react), which runs
  // after every figure change. Adding the figure deps here would cause a redundant
  // newPlot → purge → newPlot cycle on the very first render.
  useEffect(() => {
    if (!ref.current) return;
    Plotly.newPlot(ref.current, data, layout, config);
    const el = ref.current;
    return () => { Plotly.purge(el); };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- see block comment above
  }, []);

  // Runs whenever data, layout, or config changes. `Plotly.react` is a diff-aware
  // update that avoids a full re-render when only a subset of the figure changed.
  useEffect(() => {
    if (!ref.current) return;
    Plotly.react(ref.current, data, layout, config);
  }, [data, layout, config]);

  // Observe the plot container with a ResizeObserver so the chart reflowes
  // whenever the container changes size — not only when the browser window does.
  // This is more precise than `window.addEventListener('resize', ...)`, which
  // misses layout-driven resizes (e.g. a collapsible side panel).
  useEffect(() => {
    if (!ref.current) return;
    const el = ref.current;
    const ro = new ResizeObserver(() => {
      Plotly.Plots.resize(el);
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  return ref;
}
