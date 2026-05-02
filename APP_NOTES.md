# App Notes

## Feature Roadmap

1. **Implement feasible region visualisation**
   - Compute convex hull of constraints intersected with the bounding box.
   - Render as a filled `go.Scatter` trace with `fill: 'toself'` and a semi-transparent colour.
   - Bold boundary segments and vertex markers as separate traces or shapes.

2. **Implement constraint toggle functionality**
   - Add an eye-icon button to each `ConstraintRow`; track `enabled: boolean` on `Constraint`.
   - Excluded constraints: render as dashed lines in the plot and skip them in `solveLp`.

3. **Adaptive sign display**
   - When a coefficient is negative, show `− |coeff|` instead of `+ −|coeff|` in the constraint rows and legend.

4. **Implement model persistence**
   - Save/load LP models to `localStorage` or a shareable URL hash.
   - Add a reset-to-default button.

5. **Rescaling constraint lines on zoom/pan**
   - `lineBoxedEndpoints` in `geometry.ts` clips to the fixed viewport `X_RANGE / Y_RANGE`.
   - On zoom/pan, lines should recompute endpoints against the new visible range.
   - Hook into Plotly's `plotly_relayout` event to get the current axis ranges and rebuild shapes.

6. **Improve visual design**
   - Objective vector corner inset box (fixed position using `paper` reference in Plotly).
   - Colour pickers for objective arrow, constraint lines, solution, and feasible region.

## Design Decisions

### Last-constraint reset behaviour
When `removeConstraint` is called and only one constraint remains, it is replaced with a fresh
default (`0x + 0y ≤ 0`) rather than removed. See the comment in `App.tsx`'s `removeConstraint`
callback. The solver and plot do not handle an empty constraint list.

### NumberInput deferred commit
`NumberInput` holds a local string state while the user types and only propagates a parsed number
to the parent on blur or Enter. See the JSDoc in `components/NumberInput.tsx`. This avoids
triggering a re-solve on every keystroke and prevents the field from snapping to zero while a
partial value like `−` is being typed.

### Pure TypeScript simplex solver
The LP is solved in-browser by a two-phase simplex implementation in `simplex.ts`, with no
external math library. See the block comment above `FIXED_COLS` in that file for the full
tableau column layout and the rationale for splitting `x` and `y` into positive/negative parts.

### Plotly two-effect lifecycle
`usePlot` uses two separate `useEffect` calls — see the inline comments in
`components/usePlot.ts`. The split is necessary to separate mount/unmount (StrictMode-safe) from
figure updates (run on every dependency change).

## Known Limitations

- **Fixed viewport**: Constraint lines are clipped to `X_RANGE = [-1, 6]`, `Y_RANGE = [-1, 4]`
  in `graph.ts`. Zooming or panning in Plotly does not update the clip region — lines end at the
  initial boundary.
- **2-variable only**: The solver and UI are hard-coded for `x` and `y`. Generalising to `n`
  variables would require reworking the tableau encoding, the form, and the plot.
- **`tsx` devDependency installed but unused** in any npm script — can be removed if not needed
  for future scripting tasks.

## Resources

- [Plotly.js docs](https://plotly.com/javascript/)
- [Vite docs](https://vitejs.dev/)
- [Vitest docs](https://vitest.dev/)
