# AGENTS.md

## Commands

```bash
npm run dev          # dev server (HMR)
npm run build        # tsc -b && vite build  — typecheck + bundle
npm run lint         # eslint on all *.ts / *.tsx
npm test             # vitest run  (single pass)
npm run test:watch   # vitest      (watch mode)
```

## Architecture

Pure frontend — no server, no API calls. All computation runs in the browser.

```
src/
  types.ts            # all domain types + EPSILON + sense parsers; no imports from other src files
  geometry.ts         # lineBoxedEndpoints, objectiveUnitVector — pure math, no React
  simplex.ts          # two-phase Simplex solver — pure math, no React
  graph.ts            # buildLayout(), buildData(), PLOT_CONFIG, CONSTRAINT_COLORS
  hooks/
    usePlot.ts        # Plotly lifecycle hook — newPlot/purge/react/resize
  components/
    ConstraintRow.tsx  # memo-ised; imports CONSTRAINT_COLORS from graph.ts
    ObjectiveForm.tsx  # memo-ised
    Legend.tsx         # memo-ised; renders constraint swatches + result badge
    NumberInput.tsx    # controlled input with local string state
  App.tsx             # domain state + useMemo + useCallback; no Plotly logic
  simplex.test.ts     # Vitest suite (excluded from app build)
  index.css           # global styles + CSS custom properties
```

## How the graph is driven

`usePlot(data, layout, config)` owns all Plotly concerns and returns a `RefObject<HTMLDivElement | null>`.  
`App.tsx` computes `data` and `layout` via separate `useMemo` calls and passes them to the hook — no Plotly imports in `App.tsx`.

`buildLayout(objective, constraints)` and `buildData(result)` are the two figure builders in `graph.ts`. They are memoised independently: layout only recomputes when the LP definition changes, data only when the result changes.

`PLOT_CONFIG` in `graph.ts` is a module-level constant — stable reference, no need to memo.

## Plotly lifecycle — why usePlot is structured as two effects

```ts
// Effect 1 — empty deps: newPlot on mount, purge on unmount.
// Purge in cleanup makes StrictMode's double-invoke safe.
useEffect(() => {
  Plotly.newPlot(ref.current, data, layout, config);
  return () => Plotly.purge(el);
}, []);

// Effect 2 — figure deps: react on every update.
useEffect(() => {
  Plotly.react(ref.current, data, layout, config);
}, [data, layout, config]);
```

Using `Plotly.Plots.resize()` for window resize — not `Plotly.relayout({})`, which re-renders all traces.

## TypeScript constraints — things that will cause build failures

**`erasableSyntaxOnly: true`** bans TypeScript `enum`. Use `const` objects with string literal union types:

```ts
// ✗ breaks the build
enum Foo { A = 'a' }

// ✓ pattern used throughout this repo
const Foo = { A: 'a' } as const;
type Foo = typeof Foo[keyof typeof Foo];
```

**`verbatimModuleSyntax: true`** requires `import type` for type-only imports:

```ts
import type { Constraint, LPResult } from './types';  // ✓
import { Constraint } from './types';                  // ✗ if Constraint is only a type
```

**`noUnusedLocals` and `noUnusedParameters`** are both true — unused variables are hard errors.

## Plotly import — no suppression comment needed

`plotly.js-dist-min` is resolved via `src/plotly-shim.d.ts`, which maps it to `@types/plotly.js`. Import it directly without `@ts-ignore` or `@ts-expect-error`:

```ts
import Plotly from 'plotly.js-dist-min';  // ✓ — shim handles types
```

## Validated sense parsers — use these in event handlers, not `as` casts

```ts
// ✗ unsafe — bypasses the type system
onChange({ ...c, sense: e.target.value as ConstraintSense })

// ✓ throws at runtime if a bad value ever appears
import { parseConstraintSense, parseObjectiveSense } from './types';
onChange({ ...c, sense: parseConstraintSense(e.target.value) })
```

## Colour palette — single source of truth

`CONSTRAINT_COLORS` is exported from `graph.ts`. Import from there in any component that needs it. Do not redeclare it.

## IDs — use crypto.randomUUID()

Constraint IDs are generated with `crypto.randomUUID()` (available in all target browsers and Node ≥19). Do not use module-level counters — they persist across HMR reloads and test runs.

## Test file is excluded from the app build

`tsconfig.app.json` excludes `src/**/*.test.ts`. If you add a new test file, apply the same exclusion pattern. Test files can use Node globals freely (`process`, etc.) because Vitest runs them in Node.

## Constraint satisfaction is the authoritative correctness check

When verifying the solver, check that the solution point satisfies every constraint — not just that the objective value matches. A subtle sign error in the tableau encoding can produce the right objective value at the wrong point. The test suite's `allSatisfied()` helper implements this check.

## Domain encoding in simplex.ts

Variables `x` and `y` are split into positive/negative parts at tableau columns 1–4:

| Column | Meaning |
|---|---|
| 0 | RHS |
| 1 | x⁺ |
| 2 | x⁻ |
| 3 | y⁺ |
| 4 | y⁻ |
| 5+ | slack variables (FIXED_COLS = 5) |

Artificial variables are appended during phase 1 and stripped before phase 2.

## Bounding box

The graph clips constraint lines to `X_RANGE = [-1, 6]`, `Y_RANGE = [-1, 4]` (exported from `graph.ts`, imported by the test suite). If you change the viewport, update the single source in `graph.ts` only.
