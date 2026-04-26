# LP Visualizer

Are you a visual learner? Want to understand linear programs but struggle to picture what's actually going on? LP Visualizer is for you.

Linear programs are the first thing you encounter when learning optimization --- and for good reason.
They power real-world decisions like minimizing shipping costs, maximizing factory output, or balancing a diet.
But the textbook math can feel abstract.
This app makes it tangible: tweak a constraint, watch the shaded region shift.
Move the objective, see the solution snap to a new corner.
No prior knowledge required --- just curiosity.

Built with [Python](https://python.org), [Dash](https://dash.plotly.com/), and [Plotly](https://plotly.com/python/), LP Visualizer runs in your browser and updates the plot instantly as you type.

---

## Features

- **Live LP editor**:
  - [x] enter objective function coefficients
  - [x] add/remove constraints through a structured form
  - [x] the plot updates on every change
- **Feasible region**:
  - [ ] shaded semi-transparent polygon
  - [ ] with bold boundary segments
  - [ ] and vertex markers
- **Constraint lines**:
  - [x] infinite lines
  - [ ] that rescale automatically as you zoom or pan
- **Objective vector**:
  - [x] fixed-size arrow
  - [ ] in a corner box showing the optimization direction
- **Optimal solution**:
  - [x] displays the optimal value below the plot
  - [ ] red marker placed at the optimal vertex
- **Unbounded / infeasible detection**:
  - [x] the app reports these statuses as text when no finite optimum exists
- **Per-constraint controls**:
  - [x] **Delete** (trash icon): permanently remove a constraint and update the plot
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

## How to Install & Run

### Option A: uv (recommended)

[uv](https://docs.astral.sh/uv/) handles the Python version, virtual environment, and dependencies in one step.

```bash
git clone https://github.com/Ivan-Sergeyev/lp_visualizer.git
cd lp_visualizer
uv run app.py
```

That's it. uv reads `.python-version` and `pyproject.toml` automatically.

### Option B — pip

For those seeking a pure Python experience without additional tools:

```bash
git clone https://github.com/Ivan-Sergeyev/lp_visualizer.git
cd lp_visualizer
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install .
python app.py
```

Either way, the app is accessible at [http://127.0.0.1:8050] once running.

---

## Usage

The interface is split into two panels:

- **Left panel: LP model**
  - Set the **objective sense** (`min` or `max`) using the dropdown at the top.
  - Enter `x` and `y` coefficients for the objective function.
  - Click **Add Constraint** to append a new constraint row.
  - For each constraint, fill in the `x` coefficient, `y` coefficient, sense (`≤`, `≥`, or `=`), and right-hand side.
  - Use the **trash** button to delete a constraint.
  - _Coming soon:_ Use the **eye** button to temporarily disable a constraint.

- **Right panel: plot**
  - Constraint lines are drawn as thin blue lines.
  - _Coming soon:_ The feasible region is shaded in semi-transparent blue.
  - The objective vector is shown as a fixed arrow (_Coming soon:_ in a corner inset).
  - _Coming soon:_ When an optimal solution exists, a red circle marks the optimal vertex and the optimal value is displayed below the chart.
  - _Coming soon:_ Zoom and pan update the infinite lines automatically.

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

_Todo: update_

---

## Control Flow

_Todo: update_

---

## License

This project is licensed under the [MIT License](LICENSE.txt).

---

## Author

[Ivan Sergeev](https://github.com/Ivan-Sergeyev)
