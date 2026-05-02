# LP Visualizer

Are you a visual learner? Want to understand linear programs but struggle to picture what's actually going on? LP Visualizer is for you.

Linear programs are the first thing you encounter when learning optimization — and for good reason.
They power real-world decisions like minimizing shipping costs, maximizing factory output, or balancing a diet.
But the textbook math can feel abstract.
This app makes it tangible: tweak a constraint, watch the line shift.
Move the objective, see the solution update instantly.
No prior knowledge required — just curiosity.

## Features

- **Live LP editor**:
  - [x] enter objective function coefficients and sense (`min` / `max`)
  - [x] add/remove constraints through a structured form
  - [x] the plot updates on every change
- **Feasible region**:
  - [ ] shaded semi-transparent polygon
  - [ ] with bold boundary segments
  - [ ] and vertex markers
- **Constraint lines**:
  - [x] drawn as infinite lines clipped to the plot bounds, each with a distinct colour
  - [ ] rescale automatically as you zoom or pan
- **Objective vector**:
  - [x] fixed-length amber arrow showing the optimization direction
  - [ ] corner inset box
- **Optimal solution**:
  - [x] reports the optimal value and point in the Result section of the left panel
  - [x] detects and reports unbounded and infeasible problems
  - [x] green marker placed at the optimal vertex
- **Per-constraint controls**:
  - [x] **Delete** (`×` button): permanently removes a constraint and updates the plot
  - [ ] **Toggle** (eye icon): disable a constraint without deleting it; disabled constraints shown as dashed lines and excluded from solving
- **Adaptive sign display**:
  - [ ] automatically show `−` instead of `+ −` when a coefficient is negative

## Usage

The interface is split into two panels:

- **Left panel: LP model**
  - Set the **objective sense** (`min` or `max`) using the dropdown at the top.
  - Enter `x` and `y` coefficients for the objective function.
  - For each constraint, fill in the `x` coefficient, `y` coefficient, sense (`≤`, `≥`, or `=`), and right-hand side value. Coefficient inputs commit on blur or Enter; clicking the spinner arrows steps by 0.5.
  - Click **Add Constraint** to append a new constraint row.
  - Use the **×** button to delete a constraint. If only one constraint remains, deleting it resets it to `0x + 0y ≤ 0` instead of removing it entirely.
  - The **Result** section at the bottom of the left panel shows the solver status (OPTIMAL / UNBOUNDED / INFEASIBLE) with a colour-coded border, and the optimal value and point when a solution exists. It updates automatically on every model change.

- **Right panel: plot**
  - Constraint lines are drawn clipped to the plot bounds; each constraint gets a distinct colour from a 7-entry cycling palette, matching the dot next to its form row.
  - The objective vector is shown as a fixed-length amber arrow anchored at the origin, pointing in the optimisation direction.
  - When the problem is optimal, a green circle marker is placed at the optimal vertex.
  - The legend below the plot lists each constraint formula, the objective direction, and (when optimal) the optimal point.

## Source overview

| File | Role |
|---|---|
| `src/types.ts` | Domain types (`Constraint`, `Objective`, `LPResult`), enums, sense parsers, `CONSTRAINT_COLORS`. No imports from other `src/` files. |
| `src/geometry.ts` | Pure math: `lineBoxedEndpoints` (clips a line to the viewport), `objectiveUnitVector` (gradient direction for the arrow). |
| `src/simplex.ts` | Two-phase simplex solver. Variables `x` and `y` are split into positive/negative parts (columns 1–4); slack and artificial variables follow. See the block comment above `FIXED_COLS` for the full tableau layout. |
| `src/graph.ts` | Plotly figure builders: `buildLayout` (axes + constraint lines + objective arrow) and `buildData` (optimal point marker). Also exports `X_RANGE`, `Y_RANGE`, and `PLOT_CONFIG`. |
| `src/components/usePlot.ts` | React hook that owns the Plotly `newPlot` / `react` / `purge` / `resize` lifecycle. |
| `src/components/NumberInput.tsx` | Number `<input>` with deferred-commit semantics: propagates to parent only on blur or Enter. |
| `src/components/ConstraintRow.tsx` | One constraint form row with a colour dot, three `NumberInput`s, a sense `<select>`, and a remove button. |
| `src/components/ObjectiveForm.tsx` | Objective sense `<select>` and two coefficient `NumberInput`s. |
| `src/components/Legend.tsx` | Swatches + labels below the plot: one per constraint, plus objective direction, plus optimal point when applicable. |
| `src/App.tsx` | State (`objective`, `constraints`), `useMemo` for solve + figure, `useCallback` for constraint mutations. No Plotly imports. |

## Development

```bash
npm run dev      # dev server with HMR
npm run build    # typecheck (tsc -b) then bundle (vite build)
npm run preview  # serve dist/ locally — run build first
npm run lint     # ESLint over all *.ts / *.tsx
npm test         # Vitest single-pass (87 tests in src/simplex.test.ts)
```

## Deployment

The app builds to pure static files and is deployed to GitHub Pages via GitHub Actions.

**Live URL:** `https://ivan-sergeyev.github.io/lp_visualizer/`

Every push to the `frontend-only` branch triggers `.github/workflows/deploy.yml`, which runs `npm ci && npm run build` and deploys `dist/` to Pages. You can also trigger a deploy manually from the Actions tab.

**One-time setup** (already done; recorded here for reference):
1. In the repo settings, go to Pages → Source → select **GitHub Actions**.
2. The `base: '/lp_visualizer/'` in `vite.config.ts` ensures asset paths match the Pages subdirectory.

## License

This project is licensed under the [MIT License](LICENSE).

## Author

[Ivan Sergeev](https://github.com/Ivan-Sergeyev)
