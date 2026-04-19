# App Notes

## Feature Roadmap

- Create GitHub documentation (README/spec)

- **Implement constraint toggle functionality**
  - Add on/off buttons and visual feedback for constraints
  - Track toggle state in model
  - Apply `dash='dash'` style to disabled constraints
- **Implement feasible region visualization**
  - Compute convex hull of constraints + bounding box
  - Render using `go.Scatter(x=vertices_x_list, y=vertices_y_list, fill="toself")`
- **Implement model persistence**
  - Save and load LP models
  - Reset to default model
- **Improve visual design**
  - Fix issue with vertical alignment of "s.t." label (Requires flex container wrapping label + constraint rows)
  - Add custom favicon
  - Replace standard components with [Dash Mantine Components (DMC)](https://www.dash-mantine-components.com/)
  - Add objective vector display box (fixed position using `paper` ref)
  - Add color pickers for objective arrow, constraint lines, solution, and feasible region
- **Implement model persistence**
  - Add alternative model implementation that does not rely on python-mip
  - Store custom Objective and Constraint classes, implement simplex method to solve LP
  - Use this to adderss browser reload and multi-user session issues (see [Known Issues])
- Add comprehensive test suite

## Known Issues

- **Browser page reload causes stale constraint IDs**
  - Problem: UI refreshes but LP model doesn't → errors when modifying constraints
  - Possible solutions:
    - On reload, reset model or re-create initial model
    - Move to manual LP storage (no shared state optimization)
  - Related to: Multi-user session state management

- **Model optimized twice at startup (debug=True)**
  - Intermittent issue; appears related to model initialization location
  - Last occurred when moving initialization between `linear_program.py` ↔ `app.py`
  - Needs investigation and stable fix

## Technical Notes & Design Decisions

- **Python-MIP Constraint Update Behavior**
  - Coefficient updates (x_coeff, y_coeff) and sense updates (<=, >=, =): Cannot be updated in-place → must remove and re-add constraint
  - Right-hand side (rhs) updates: Can be updated in-place via `constraint.rhs = value`
  - This pattern is reflected in `LinearProgram._set_mip_constraint_*` methods

- **Last Constraint Reset Behavior**
  - When deleting the last constraint, the system resets it to default instead of removing it
  - Reason: `master_constraint_callback()` depends on at least one constraint existing
  - Without this, the callback breaks when the constraint list becomes empty
  - This behavior is implemented in `remove_constraint()` inside `user_actions.register()`

- **Math Rendering**
  - Current approach: DashLatex (stable, recommended)
  - Alternative: MathJax via CDN
    - Setup:

      ```python
      app = dash.Dash(
          __name__,
          external_scripts=[
              'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'
          ]
      )
      ```

    - Syntax: Use `\\(x\\)` or `r'\(x\)'` instead of `dl.DashLatex(r'$x$')`
    - Status: Not recommended — rendering breaks after multiple page reloads

- **CSS/Input Styling Quirks**
  - Issue: Dash wraps inputs in divs; stepper buttons generate automatically even with `min`/`max`/`step=None`
  - Impact: Default styling overrides and element width mismatch
  - Solution: Use `input[id*="-coeff"]` selector with `text-align: right; width: 100%`

## Resources

- [Plotly docs](https://docs.plotly.com/)
- [Dash documentation](https://dash.plotly.com/)
- [Python-MIP documentation](https://docs.python-mip.com/en/latest/name.dash.html)
