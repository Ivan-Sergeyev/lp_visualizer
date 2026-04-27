# LP Visualizer

Are you a visual learner? Want to understand linear programs but struggle to picture what's actually going on? LP Visualizer is for you.

Linear programs are the first thing you encounter when learning optimization — and for good reason.
They power real-world decisions like minimizing shipping costs, maximizing factory output, or balancing a diet.
But the textbook math can feel abstract.
This app makes it tangible: tweak a constraint, watch the line shift.
Move the objective, see the solution update instantly.
No prior knowledge required — just curiosity.

Built with [Python](https://python.org), [Dash](https://dash.plotly.com/), and [Plotly](https://plotly.com/python/), LP Visualizer runs in your browser and updates the plot in real time as you type.

---

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
  - [x] drawn as infinite lines clipped to the plot bounds
  - [ ] rescale automatically as you zoom or pan
- **Objective vector**:
  - [x] fixed-length arrow showing the optimization direction
  - [ ] corner inset box
- **Optimal solution**:
  - [x] reports the optimal value as text below the plot
  - [x] detects and reports unbounded and infeasible problems
  - [ ] red marker placed at the optimal vertex
- **Per-constraint controls**:
  - [x] **Delete** (trash icon): permanently removes a constraint and updates the plot
  - [ ] **Toggle** (eye icon): disable a constraint without deleting it; disabled constraints shown as dashed lines and excluded from solving
- **Adaptive sign display**:
  - [ ] automatically show `−` instead of `+ −` when a coefficient is negative

---

## Tech Stack

| Library | Version | Purpose |
| --- | --- | --- |
| [Plotly](https://plotly.com/python/) | 6.7.0 | Interactive 2-D chart |
| [Dash](https://dash.plotly.com/) | 4.1.0 | Web app framework and reactive callbacks |
| [dash-iconify](https://github.com/snehilvj/dash-iconify) | 0.1.2 | Icon components (trash, ...) |
| [dash-latex](https://pypi.org/project/dash-latex/) | 0.1.1 | LaTeX rendering for math labels |
| [NumPy](https://numpy.org/) | 2.4.4 | Tableau arithmetic in the simplex solver |

The LP solver is implemented from scratch using the two-phase simplex method (see `algorithms/simplex.py`). No external solver library is required.

Python **3.10+** is required. The project targets 3.14 in `pyproject.toml`; earlier versions work with the `from __future__ import annotations` compatibility shim.

---

## How to Install & Run

### Option A: uv (recommended)

[uv](https://docs.astral.sh/uv/) handles the Python version, virtual environment, and dependencies in one step.

```bash
git clone https://github.com/Ivan-Sergeyev/lp_visualizer.git
cd lp_visualizer
uv run app.py
```

`uv` reads `pyproject.toml` automatically. No separate install step is needed.

### Option B: pip

```bash
git clone https://github.com/Ivan-Sergeyev/lp_visualizer.git
cd lp_visualizer
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install .
python app.py
```

Either way, the app is accessible at [http://127.0.0.1:8050](http://127.0.0.1:8050) once running.

---

## Usage

The interface is split into two panels:

- **Left panel: LP model**
  - Set the **objective sense** (`min` or `max`) using the dropdown at the top.
  - Enter `x` and `y` coefficients for the objective function.
  - For each constraint, fill in the `x` coefficient, `y` coefficient, sense (`≤`, `≥`, or `=`), and right-hand side value.
  - Click **Add Constraint** to append a new constraint row.
  - Use the **trash** button to delete a constraint. If only one constraint remains, deleting it resets it to the default trivial constraint `0x + 0y ≤ 0` instead of removing it entirely.

- **Right panel: plot**
  - Constraint lines are drawn as thin blue lines clipped to the plot bounds.
  - The objective vector is shown as a red arrow anchored at the origin.
  - The optimizaition result (optimal value and point, or infeasible/unbounded status) is displayed below the chart. It updates automatically whenever the model changes.

---

## Development

### Running tests

```bash
python -m pytest
```

Tests live in `tests/` and are auto-discovered by pytest (configured in `pyproject.toml`). The suite covers geometry primitives, model dataclasses, and end-to-end solver correctness across optimal, unbounded, and infeasible cases.

### Linting

```bash
ruff check .
```

Line length is set to 88 characters.

---

## Project Structure

```plaintext
lp_visualizer/
├── app.py                    # Entry point: initial state, Dash app, server
├── pyproject.toml            # Dependencies and tool configuration
├── assets/
│   └── style.css             # App-wide CSS
├── algorithms/
│   ├── geometry.py           # 2D geometry: Vector2D, Point2D, Line2D
│   └── simplex.py            # Two-phase simplex solver: SimplexTableau, SimplexSolver
├── model/
│   ├── constraint.py         # Constraint dataclass and ConstraintSense enum
│   └── objective.py          # Objective dataclass and ObjectiveSense enum
├── components/
│   ├── common.py             # Shared constants (StorageType)
│   ├── app_layout.py         # Top-level layout assembly (panels + stores)
│   ├── objective.py          # Objective form row and dcc.Store component
│   └── constraint.py         # Constraint form rows and dcc.Store components
├── callbacks/
│   ├── graph.py              # Pure Plotly figure-building and patch functions
│   └── user.py               # Dash UI callback registration and ConstraintPatch helper
└── tests/
    ├── test_geometry.py      # Unit tests for geometry primitives
    ├── test_model.py         # Unit tests for Constraint and Objective model classes
    └── test_simplex.py       # Integration tests for the simplex solver
```

The layers are deliberately kept separate: `model` has no Dash or NumPy imports, `algorithms` has no Dash imports, `components` builds layout but registers no callbacks, and `callbacks` wires everything together.

---

## Control Flow

### Startup

1. `app.py` constructs an initial `Objective` and a `dict[str, Constraint]`.
2. A Plotly `Figure` is created and the objective arrow and constraint lines are drawn onto it via `callbacks/graph.py`.
3. `SimplexSolver.solve()` is called once to produce the initial result string.
4. `components/app_layout.py::app_wrapper()` assembles the full Dash layout:
   - **Left panel**: objective row + constraint rows + Add Constraint button.
   - **Right panel**: `dcc.Graph` + result `div`.
   - **Hidden stores**: one `dcc.Store` for the objective; one per constraint, each holding a serialized `ConstraintDict`.
5. `callbacks/user.py::register(app)` binds all reactive callbacks to the app.
6. The Dash development server starts.

### User interaction (constraint coefficient edit, as an example)

```plaintext
User types in a coefficient input
        │
        ▼
constraint_master_callback  (callbacks/user.py)
  • identifies the triggering input via dash.callback_context
  • calls ConstraintPatch().set_coeff_x(...)
      – looks up the constraint in the constraints store
      – calls graph.figure_update_constraint() to compute a figure Patch
      – patches the store entry in-place
  • returns (constraints_patch, figure_patch, store_patch)
        │
        ├─► dcc.Graph figure updated  (constraint line redrawn)
        ├─► constraints-store updated
        └─► constraints-list updated  (no-op patch; UI row unchanged)
                │
                ▼
        result_callback  (callbacks/user.py)
          • triggered by the store update
          • deserializes objective + all constraints from their stores
          • calls SimplexSolver.solve()
          • returns a Patch updating the result div text
```

### Solver pipeline

```plaintext
SimplexSolver.solve(objective, constraints)
        │
        ▼
SimplexTableau.canonical_from(objective, constraints)
  • MAX → MIN by negating objective costs
  • GE rows negated to LE; EQ rows split into one LE + one GE row
  • variables split: x = x⁺ − x⁻, y = y⁺ − y⁻  (both ≥ 0)
  • slack identity block appended
  • column layout: [RHS | x⁺ | x⁻ | y⁺ | y⁻ | slack₀ | slack₁ | …]
        │
        ├─ all RHS ≥ 0? ──YES──► Phase 2
        │
        └─ some RHS < 0 ──────► Phase 1 (find an initial BFS)
              • negate negative-RHS rows; add one artificial variable each
              • minimise sum of artificials via standard simplex
              • phase-1 objective value > 0  ──► INFEASIBLE  (stop)
              • phase-1 objective value = 0  ──► tear down artificials
                    │
                    ▼
              Phase 2 (standard simplex)
              • entering column: most negative reduced cost
              • leaving row: minimum ratio test
              • repeat until all reduced costs ≥ 0  ──► OPTIMAL
                    or no positive column entry found ──► UNBOUNDED
                    │
                    ▼
              _get_solution()
              • reads x⁺, x⁻, y⁺, y⁻ from the optimal basis
              • reconstructs x = x⁺ − x⁻, y = y⁺ − y⁻
              • corrects objective sign for the original MIN/MAX sense
              • returns Solution(point, objective_value)
```

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Author

[Ivan Sergeev](https://github.com/Ivan-Sergeyev)
