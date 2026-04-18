# LP Visualizer

An interactive web application for visualizing and solving **2-variable linear programs** in real time. Built with Python, [Dash](https://dash.plotly.com/), and [Plotly](https://plotly.com/python/), it lets you define an LP by typing coefficients directly into the UI and instantly see the feasible region, constraint lines, objective vector, and optimal solution update on the plot.

---

## Features

- **Live LP editor**:
  - [v] enter objective function coefficients
  - [v] add/remove constraints through a structured form
  - [v] the plot updates on every change
- **Feasible region**:
  - [ ] shaded semi-transparent polygon
  - [ ] with bold boundary segments
  - [ ] and vertex markers
- **Constraint lines**:
  - [v] infinite lines
  - [ ] that rescale automatically as you zoom or pan
- **Objective vector**:
  - [v] fixed-size arrow
  - [ ] in a corner box showing the optimization direction
- **Optimal solution**:
  - [v] displays the optimal value below the plot
  - [ ] red marker placed at the optimal vertex
- **Unbounded / infeasible detection**:
  - [v] the app reports these statuses as text when no finite optimum exists
- **Per-constraint controls**:
  - [v] **Delete** (trash icon): permanently remove a constraint and update the plot
  - [ ] **Toggle** (eye icon): disable a constraint without deleting it; disabled constraints are dashed on the plot and excluded from solving
- **Adaptive sign display**:
  - [ ] automatically shows `−` instead of `+ −` when a coefficient is negative

---

## Tech Stack

| Library | Version | Purpose |
| --- | --- | --- |
| [Plotly](https://plotly.com/python/) | 6.7.0 | Interactive 2-D chart |
| [Dash](https://dash.plotly.com/) | 4.1.0 | Web app framework & reactive callbacks |
| [dash-iconify](https://github.com/snehilvj/dash-iconify) | 0.1.2 | Icon components (eye, trash, …) |
| [Python-MIP](https://www.python-mip.com/) | 1.17.6 | LP solver (CBC back-end) |

Python **3.14** is required (pinned in `.python-version`).

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Ivan-Sergeyev/lp_visualizer.git
cd lp_visualizer
```

### 2. Set up a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install .
```

To also install development tools (pytest + ruff):

```bash
pip install ".[dev]"
```

---

## Running the App

```bash
python app.py
```

The app starts in debug mode and is accessible at **[http://127.0.0.1:8050]** by default.

---

## Usage

The interface is split into two panels:

- **Left panel: LP model**
  - Set the **objective sense** (`min` or `max`) using the dropdown at the top.
  - Enter `x` and `y` coefficients for the objective function.
  - Click **Add Constraint** to append a new constraint row.
  - For each constraint, fill in the `x` coefficient, `y` coefficient, sense (`≤`, `≥`, or `=`), and right-hand side.
  - Use the **eye** button to temporarily disable a constraint, or the **trash** button to delete it.

- **Right panel: plot**
  - Constraint lines are drawn as thin black lines.
  - The feasible region is shaded in semi-transparent blue.
  - The objective vector is shown as a fixed arrow in a corner inset.
  - When an optimal solution exists, a red circle marks the optimal vertex and the optimal value is displayed below the chart.
  - Zoom and pan update the infinite lines automatically.

---

## Development

### Running tests

```bash
pytest
```

Tests live in the `tests/` directory and are auto-discovered by pytest (configured in `pyproject.toml`).

### Linting

```bash
ruff check .
```

Line length is set to 88 characters.

---

## Project Structure

```plaintext
lp_visualizer/
├── app.py                   # Entry point; creates the Dash app and registers callbacks
├── pyproject.toml           # Project metadata and dependencies
├── model/
│   ├── linear_program.py    # LP state: objective, constraints, solver call
│   └── domain_transfer_objects.py  # Dataclasses: Objective, Constraint, OptimizationResult
├── callbacks/
│   ├── user_actions.py      # Dash callbacks wired to every UI interaction
│   └── graph_updates.py     # Helper functions that mutate the Plotly figure
├── components/
│   └── components.py        # app_layout(); builds the full Dash component tree
├── assets/                  # Static files (CSS, favicon)
└── tests/                   # pytest suite
```

---

## Control Flow

```plaintext
User Action              →  Model Update                →  Plot Update
───────────────────────────────────────────────────────────────────────────────────────────────
Change objective sense   →  Flip sense                  →  Flip arrow, re-solve
Change obj. coefficient  →  Update coefficient          →  Rotate arrow, re-solve
Add constraint           →  Append constraint           →  Add line, update region, re-solve
Delete constraint        →  Remove constraint           →  Remove line, update region, re-solve
Disable constraint       →  Mark as inactive            →  Dash line, update region, re-solve
Enable constraint        →  Mark as active              →  Solid line, update region, re-solve
Change constraint coeff  →  Update coefficient          →  Move line, update region, re-solve
Change constraint sense  →  Update sense                →  Update region, re-solve
```

---

## License

This project is licensed under the [MIT License](LICENSE.txt).

---

## Author

[Ivan Sergeev](https://github.com/Ivan-Sergeyev)
