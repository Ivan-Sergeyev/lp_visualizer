# App Notes

## Feature Roadmap

1. **Improve GitHub documentation**
    - update spec to match the implementation of v0.2
    - update README to be friendlier to non-specialists
1. **Implement feasible region visualization**
    - Compute convex hull of constraints + bounding box
    - Render using `go.Scatter(x=vertices_x_list, y=vertices_y_list, fill="toself")`
1. **Implement constraint toggle functionality**
    - Add on/off buttons and visual feedback for constraints
    - Track toggle state in model
    - Apply `dash='dash'` style to disabled constraints
1. **Implement model persistence**
    - Save and load LP models
    - Reset to default model
1. **Improve visual design**
    - Add custom favicon
    - Fix issue with vertical alignment of "s.t." label (Requires flex container wrapping label + constraint rows)
    - Replace standard components with [Dash Mantine Components (DMC)](https://www.dash-mantine-components.com/)
    - Add objective vector display box (fixed position using `paper` ref)
    - Add color pickers for objective arrow, constraint lines, solution, and feasible region
1. **Add comprehensive test suite**

## Known Issues

1. **Model optimized twice at startup (debug=True)**
    - Requires investigation
1. **Store type 'session' is not supported**
    - Current behavior with 'memory' store type:
      the model, the store, and the graph cleared on reload
    - Current behavior after switching to 'session' store type:
      reloading the page resets the model and the graph, but does not clear the store,
      leading to a desync between the model, the model, and the graph,
      as well as store duplication
    - Requires investigation into potential fix

## Technical Notes & Design Decisions

- **Python-MIP Constraint Update Behavior**
  - Coefficient updates (x_coeff, y_coeff) and sense updates (<=, >=, =):
    Cannot be updated in-place -> must remove and re-add constraint
  - Right-hand side (rhs) updates: Can be updated in-place via `constraint.rhs = value`
  - According to a surface-level investigation, modifying the model in PuLP is even harder
  - Switched from python-mip to dcc.Store + manually implemented simplex solver
    to reduce latency, avoid using singleton object, and support online deployment and
    multiple concurrent users

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

### Unused

- [Python-MIP documentation](https://docs.python-mip.com/en/latest/name.dash.html)
- [PuLP](https://coin-or.github.io/pulp/)
