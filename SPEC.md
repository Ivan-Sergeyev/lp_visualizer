# LP Visualizer — Developer Specification

Specification for an LLM agent implementing this project with minor human oversight. Follow
this document precisely. Where a `TODO` is marked, stop and ask the human before proceeding.

---

## 1. Project Overview

An interactive web app that visualises two-variable linear programs (LPs). The user types an
objective function and a list of constraints; the app immediately redraws the plot and reports
the solution status.

Scope is deliberately narrow: **two variables (x and y) only**, real-valued (continuous), no
integer/MIP features even though the solver supports them.

---

## 2. Tech Stack

| Concern | Library | Notes |
| --- | --- | --- |
| Web framework | `dash` | Callbacks, layout |
| Plotting | `plotly` (via `dash`) | `dcc.Graph` |
| LP solver | `python-mip` | Continuous relaxation only |
| Language | Python 3.11+ | |
| Packaging | `pyproject.toml` (already exists) | |
| CI | GitHub Actions (`.github/workflows/ci.yml`) | |
| Testing | `pytest` | Files already exist under `tests/` |

Do not introduce additional runtime dependencies without asking.

---

## 3. File Architecture

```plaintext
lp_visualizer/
│   app.py                     # Dash app instance + layout; calls user_callbacks.register(app)
│   pyproject.toml
│   README.md
│
├───assets/                    # Static files served automatically by Dash (CSS, icons, etc.)
├───callbacks/
│       lp_state.py            # LPState dataclass and its mutation methods
│       user_callbacks.py      # register(app) — attaches all @app.callback decorators
│       plot_updates.py        # build_figure() and patch functions; no Dash decorators
└───tests/
        test_lp_state.py       # Unit tests for LPState mutation logic
        test_user_callbacks.py # Unit tests for plot logic
        test_plot_updates.py   # Unit tests for plot logic
```

### Responsibility boundaries

- **`app.py`**: creates the `Dash` app instance, defines the full page layout, and calls
  `user_callbacks.register(app)` to attach all callbacks. Also calls `build_figure(lp_state)`
  once to set the initial graph state directly on the `dcc.Graph` component in the layout.
  Contains no business logic and no `@app.callback` decorators.

- **`callbacks/lp_state.py`**: defines `LPState`, a dataclass holding the application's
  single shared state instance. Each method mutates LP state in response to a user action
  and returns the result of the corresponding plot update function from `plot_callbacks.py`,
  propagating the return value back to the caller. Contains no Dash decorators.

- **`callbacks/user_callbacks.py`**: defines a single `register(app)` function that attaches
  all `@app.callback`-decorated functions to the app. Each callback receives UI input(s),
  delegates to the corresponding `LPState` method, and returns the result directly to Dash.
  Contains no business logic beyond input coercion and delegation.

- **`callbacks/plot_callbacks.py`**: defines plot update functions that read from the shared
  `LPState` instance. `build_figure()` performs a full redraw and is called on initial load
  from `app.py`. Patch functions perform partial updates and are called by `LPState` methods
  after state mutation. Contains no Dash decorators.

---

## 4. Data Model

Application state lives in a single shared `LPState` instance created at module level in
`lp_state.py` and imported wherever needed. There are no `dcc.Store` components.

### 4.1 `LPState` (`callbacks/lp_state.py`)

`LPState` is a dataclass that internally owns a `python-mip` model. It does not store
coefficients or constraints as separate Python fields — all LP data lives inside the
`python-mip` model and is modified directly through the model's API.

It exposes mutation methods (e.g., `set_objective`, `set_constraint`, `add_constraint`) that
update the model, immediately re-solve the LP, cache the result, and return the result of the
corresponding `plot_callbacks` function to be passed back to Dash. Solving always happens
inside `LPState` as a direct consequence of any model update.

After solving, `LPState` exposes read-only result properties for `plot_callbacks` to consume:
`status`, `objective_value`, `x_opt`, and `y_opt`.

A module-level singleton `lp_state` is created in `lp_state.py` and imported by
`user_callbacks.py` and `app.py`.

---

## 5. Layout Specification

### 5.1 Top-level split

The page is divided into two equal vertical halves side by side:

- **Left half**: LP model panel
- **Right half**: Plot panel

Use a flexbox row in `app.py` or a two-column `dbc.Row` / `html.Div` with `display: flex`.

### 5.2 LP Model Panel (left)

Contains a vertical stack of rows. Each row is one equation line. All rows are laid out so
that their columns are vertically aligned across every row.

#### Column layout (left to right, all rows share the same column widths)

| Col | Content | Width | Alignment |
| --- | --- | --- | --- |
| A | Leading label (`min/max` dropdown or `s.t.` or blank) | fixed, wide enough for `s.t.` | left |
| B | x coefficient input | fixed, e.g. `80px` | right-aligned text |
| C | fixed label `x` | fixed | center |
| D | fixed label `+` | fixed | center |
| E | y coefficient input | fixed, same as B | right-aligned text |
| F | fixed label `y` | fixed | center |
| G | Sense (`<=`/`>=`/`=` dropdown, or for objective: empty spacer) | fixed | center |
| H | RHS input (or empty spacer for objective) | fixed, same as B | right-aligned text |

All rows must use the same column widths so content aligns vertically. Implement as a CSS
grid or a flex row with fixed widths; do not use a `<table>`.

#### Objective row (row 0)

- Col A: `dcc.Dropdown` with options `[{"label": "min", "value": "min"}, {"label": "max",
  "value": "max"}]`, default `"min"`, `id="obj-sense"`, no clearable.
- Col B: `dcc.Input`, type `"number"`, default `1`, `id="obj-cx"`.
- Col C: `"x"`.
- Col D: `"+"`.
- Col E: `dcc.Input`, type `"number"`, default `1`, `id="obj-cy"`.
- Col F: `"y"`.
- Cols G, H: empty spacers (same width as constraint counterparts to maintain alignment).

#### Constraint rows

Constraint rows are generated dynamically. Each row corresponds to one constraint tracked
by `lp_state`, identified by its stable integer id.

Component ids use the constraint's stable integer id as a suffix:

- `"cx-{id}"`, `"cy-{id}"`, `"sense-{id}"`, `"rhs-{id}"`

- Col A: `"s.t."` for the **first** rendered constraint row; blank for all others.
- Cols B–F: same structure as objective row but using per-constraint ids.
- Col G: `dcc.Dropdown` with options `<=`, `>=`, `=`; default `<=`; `id="sense-{id}"`.
- Col H: `dcc.Input`, type `"number"`, default `0`, `id="rhs-{id}"`.

#### "Add constraint" button

Placed below all constraint rows.

- `id="add-constraint-btn"`, label `"+ Add constraint"`.
- On click: calls `lp_state.add_constraint()`, then appends a new blank constraint row to the
  constraint container (handled in the corresponding `app.py` callback).

### 5.3 Plot Panel (right)

- `dcc.Graph(id="lp-graph")` taking most of the vertical space.
- Below the graph: a `html.Div(id="solution-text")` showing one of:
  - `"Optimal value: {v}"` where `{v}` is the objective value rounded to 4 significant figures.
  - `"Unbounded"`
  - `"Infeasible"`
  - `""` (empty) when there are no constraints.

---

## 6. LP Solving (`callbacks/lp_state.py`)

Solving is the responsibility of `LPState`, not `plot_callbacks`. Every mutation method
calls an internal solve immediately after updating the model. The solver is `python-mip`
with CBC, always run as a continuous LP (no integrality). Both variables are unbounded in
both directions. Trust `python-mip`'s results directly — no workarounds or verification
re-solves are needed.

If there are **zero constraints**, skip solving entirely and set `status` to a sentinel
value that `plot_callbacks` treats as "no solution".

### 6.1 Result interpretation

After calling `m.optimize()`, `LPState` updates its cached result properties according to
the returned status:

| `status` | `lp_state.status` | `solution_text` (for plot) | Red dot |
| --- | --- | --- | --- |
| `mip.OptimizationStatus.OPTIMAL` | `"optimal"` | `"Optimal value: {objective_value:.4g}"` | Yes, at `(x_opt, y_opt)` |
| `mip.OptimizationStatus.INFEASIBLE` | `"infeasible"` | `"Infeasible"` | No |
| `mip.OptimizationStatus.UNBOUNDED` | `"unbounded"` | `"Unbounded"` | No |
| zero constraints | `"none"` | `""` | No |

---

## 7. Plot Specification (`plot_callbacks.py`)

Build a single `go.Figure` in `build_figure(state: LPState)`. Patch functions receive the
same `state` argument and return a `dash.Patch` object targeting only the traces that
changed. `plot_callbacks` does not solve the LP — it reads the already-cached result
properties (`state.status`, `state.objective_value`, `state.x_opt`, `state.y_opt`) that
`LPState` populated after its last solve.

### 7.1 Axes and layout

- Equal aspect ratio is **not** required.
- Default axis range: `[-10, 10]` for both x and y on first render.
- `uirevision="lp"` on the figure layout so that user pan/zoom is preserved between updates.
- No legend.
- Minimal margins.

### 7.2 Constraint lines

For each constraint, draw one straight line across the full current plot range.

**Computing the line:**

Given constraint `a·x + b·y ≤/≥/= rhs`, the boundary line is `a·x + b·y = rhs`.

- If `b ≠ 0`: express as `y = (rhs - a·x) / b`. Evaluate at the two x-axis extremes of the
  current plot range to get two points. Use those as the line endpoints.
- If `b = 0` and `a ≠ 0`: vertical line at `x = rhs / a`. Draw as a vertical segment spanning
  the y-axis plot range.
- If both `a = 0` and `b = 0`: skip drawing this constraint line.

**Trace:**

```python
go.Scatter(
    x=[x0, x1], y=[y0, y1],
    mode="lines",
    line=dict(color="black", width=1),
    hoverinfo="skip"
)
```

**Making lines "infinite":** The current axis range is not available inside a callback
directly. Use a fixed wide range (e.g. `[-1000, 1000]`) to compute line endpoints; Plotly
will clip them to the visible area automatically. Set `cliponaxis=True` (default).

### 7.3 Objective vector box

A secondary subplot or `annotation`-based arrow in one corner of the plot showing the
direction of optimisation.

Implementation:

- Use a `go.Scatter` trace in **paper coordinates** (i.e. `xref="paper"`, `yref="paper"`)
  placed in the bottom-left corner (paper coords `[0.02, 0.15] × [0.02, 0.15]`).
- Draw a box outline as a rectangle annotation or a closed scatter path.
- Draw an arrow using a Plotly `annotation` with `arrowhead=2`, `ax`/`ay` set so the arrow
  originates from the centre of the box.

Arrow direction:

- Let `(cx, cy)` be the objective coefficients.
- If `sense == "min"`, the gradient points in direction `(cx, cy)` (we minimise, so the
  optimal moves opposite, but the convention is to draw the gradient arrow).
  - TODO: confirm with human which direction the arrow should point — gradient direction
    `(cx, cy)`, or the "improving" direction.
- Normalise `(cx, cy)` to length 1, scale to a fixed pixel length (e.g. 40 px) using `ax`/`ay`.
- If `cx == 0` and `cy == 0`, draw a dot (zero vector) in the centre of the box.

### 7.4 Optimal solution marker

If status is `OPTIMAL`:

```python
go.Scatter(
    x=[x_opt], y=[y_opt],
    mode="markers",
    marker=dict(color="red", size=10, symbol="circle"),
    hoverinfo="skip"
)
```

---

## 8. Callback Wiring (`callbacks/user_callbacks.py`)

All `@app.callback` decorators live in `user_callbacks.py` inside a `register(app)` function.
Each callback is a thin wrapper: coerce inputs, delegate to `lp_state`, return the result.

```python
# callbacks/user_callbacks.py
from callbacks.lp_state import lp_state
from dash import Input, Output, State, ALL

def register(app):

    @app.callback(...)
    def on_objective_change(...): ...

    @app.callback(...)
    def on_constraint_change(...): ...

    @app.callback(...)
    def on_add_constraint(...): ...
```

`app.py` calls this once after instantiating the app:

```python
# app.py
from callbacks.lp_state import lp_state
from callbacks.plot_callbacks import build_figure
import callbacks.user_callbacks as user_callbacks

app = Dash(__name__)
app.layout = build_layout(build_figure(lp_state))  # initial figure set in layout
user_callbacks.register(app)
```

### 8.1 Objective callback

```python
@app.callback(
    Output("lp-graph", "figure"),
    Input("obj-sense", "value"),
    Input("obj-cx",    "value"),
    Input("obj-cy",    "value"),
)
def on_objective_change(sense, cx, cy):
    return lp_state.set_objective(
        sense or "min",
        float(cx or 0),
        float(cy or 0),
    )
```

### 8.2 Constraint field callbacks

Because constraint component ids are dynamic, use **pattern-matching callbacks** (`ALL`
wildcard). Structure constraint component ids as dicts:

```python
{"type": "cx",    "index": constraint_id}
{"type": "cy",    "index": constraint_id}
{"type": "sense", "index": constraint_id}
{"type": "rhs",   "index": constraint_id}
```

```python
@app.callback(
    Output("lp-graph", "figure"),
    Input({"type": "cx",    "index": ALL}, "value"),
    Input({"type": "cy",    "index": ALL}, "value"),
    Input({"type": "sense", "index": ALL}, "value"),
    Input({"type": "rhs",   "index": ALL}, "value"),
    State({"type": "cx",    "index": ALL}, "id"),
)
def on_constraint_change(cxs, cys, senses, rhss, ids):
    result = None
    for id_dict, cx, cy, sense, rhs in zip(ids, cxs, cys, senses, rhss):
        result = lp_state.set_constraint(
            id_dict["index"],
            float(cx or 0), float(cy or 0),
            sense or "<=",  float(rhs or 0),
        )
    return result  # last patch / figure; all patches share the same state snapshot
```

### 8.3 Add-constraint callback

```python
@app.callback(
    Output("constraints-container", "children"),
    Input("add-constraint-btn", "n_clicks"),
    State("constraints-container", "children"),
    prevent_initial_call=True,
)
def on_add_constraint(_, existing_rows):
    c = lp_state.add_constraint()
    new_row = build_constraint_row(c)   # helper defined in app.py or a layout module
    return existing_rows + [new_row]
```

`build_constraint_row(c: ConstraintState)` returns the row `Div` structure described in
§5.2, using `c.id` for component id suffixes. Define this helper in `app.py` alongside
`build_layout`.

---

## 9. Edge Cases and Behaviour Contracts

| Situation | Expected behaviour |
| --- | --- |
| Input field is empty | Treat coefficient/RHS as `0.0` |
| Input field has non-numeric text | Treat as `0.0` (Dash `type="number"` prevents most cases) |
| Zero constraints | No solving; empty solution text; plot shows only objective vector box |
| `cx=0, cy=0` in a constraint | Constraint is degenerate; include it in solver (it will be trivially satisfied or infeasible depending on `rhs` and sense) |
| Objective `cx=0, cy=0` | Arrow in box is a dot; solver still runs |
| LP is unbounded | Use the re-solve workaround described in §6.5 |
| Plot zoom changes | `uirevision` preserves zoom; lines are pre-computed over wide range so they remain correct |

---

## 10. Acceptance Tests

Tests live in `tests/`. Use `pytest`. Do not use a browser/Selenium; test logic functions
directly.

### `test_lp_state.py`

Test `LPState` mutation methods and solve results directly — no Dash, no browser. Tests
interact only through the public interface; do not inspect internal model fields.

| Test | Action | Expected result |
| --- | --- | --- |
| Default status | instantiate `LPState` with no constraints | `status == "none"` |
| Solve updates status | call `set_objective` then `add_constraint` with a valid bounded LP | `status == "optimal"` |
| `add_constraint` returns distinct ids | call `add_constraint()` twice | returned ids are different integers |
| Infeasible LP | add two contradictory constraints | `status == "infeasible"` |
| Unbounded LP | set objective with no bounding constraints | `status == "unbounded"` |

### `test_plot_updates.py`

Test `build_figure` and the solve logic inside `plot_callbacks.py` directly.

| Test | `LPState` | Expected solution text | Expected dot coords |
| --- | --- | --- | --- |
| Simple bounded LP | min x+y, x+y>=2, x>=0, y>=0 | `"Optimal value: 2"` | any point on x+y=2, x,y≥0 |
| Infeasible | min x+y, x>=5, x<=3 | `"Infeasible"` | none |
| Unbounded | min x, no upper bound | `"Unbounded"` | none |
| No constraints | min x+y | `""` | none |
| Zero-coefficient objective | min 0x+0y, x+y>=1 | `"Optimal value: 1"` | any optimal point |

---

## 11. Open Questions / TODOs

- **TODO (arrow direction)**: Confirm which direction the objective vector arrow should point:
  the gradient `(cx, cy)` or the improving direction (negated for minimisation). See §7.3.
- **TODO (pyproject.toml)**: Confirm that `python-mip`, `dash`, and `plotly` are listed as
  dependencies in `pyproject.toml`. If not, add them.
- **TODO (CI)**: Confirm what `ci.yml` currently runs. It should at minimum run `pytest`.
- **TODO (assets/)**: Confirm whether any custom CSS is planned, or if Dash's default
  styling is acceptable for MVP.

---

## 12. Out of Scope for MVP

The following are explicitly deferred. Do not implement them unless the human asks:

- Adaptive sign between terms (showing `5x - 6y` instead of `5x + -6y`)
- Greying out zero-coefficient variables or signs
- Toggle constraint on/off (eye icon)
- Remove constraint (trash icon)
- Feasible region shading
- Infinitely many solutions highlight
- Integer/MIP solving
- More than two variables
