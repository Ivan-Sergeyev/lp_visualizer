import { useEffect, useRef } from 'react';
import type { RefObject } from 'react';
import type { Config, Data, Layout } from 'plotly.js';
import Plotly from 'plotly.js-dist-min';

/**
 * Manages the full Plotly lifecycle for a <div> ref:
 *  - newPlot on mount, purge on unmount  (survives StrictMode double-invoke)
 *  - Plotly.react on every figure change (data / layout / config)
 *  - Plotly.Plots.resize on window resize (correct resize API, not relayout)
 */
export function usePlot(
  data:   Partial<Data>[],
  layout: Partial<Layout>,
  config: Partial<Config>,
): RefObject<HTMLDivElement | null> {
  const ref = useRef<HTMLDivElement>(null);

  // Mount / unmount — intentionally empty deps so this only runs once per mount.
  // The purge cleanup makes StrictMode's double-invoke safe.
  useEffect(() => {
    if (!ref.current) return;
    Plotly.newPlot(ref.current, data, layout, config);
    const el = ref.current;
    return () => { Plotly.purge(el); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update figure whenever data or layout changes.
  useEffect(() => {
    if (!ref.current) return;
    Plotly.react(ref.current, data, layout, config);
  }, [data, layout, config]);

  // Resize with the correct Plotly API (not relayout which re-renders all traces).
  useEffect(() => {
    function handleResize() {
      if (ref.current) Plotly.Plots.resize(ref.current);
    }
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return ref;
}
