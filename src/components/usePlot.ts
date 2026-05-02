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

  // Empty deps: runs once per mount. Captures the element in `el` so the cleanup
  // closure holds the reference even after the component unmounts and ref.current
  // is cleared.
  useEffect(() => {
    if (!ref.current) return;
    Plotly.newPlot(ref.current, data, layout, config);
    const el = ref.current;
    return () => { Plotly.purge(el); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Runs whenever data, layout, or config changes. `Plotly.react` is a diff-aware
  // update that avoids a full re-render when only a subset of the figure changed.
  useEffect(() => {
    if (!ref.current) return;
    Plotly.react(ref.current, data, layout, config);
  }, [data, layout, config]);

  // Separate effect so the resize listener is registered once and never torn down
  // and re-added on figure changes.
  useEffect(() => {
    function handleResize() {
      if (ref.current) Plotly.Plots.resize(ref.current);
    }
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return ref;
}
