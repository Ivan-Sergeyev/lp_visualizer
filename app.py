import dash

from callbacks.model_state import model_state
from callbacks import user_actions
from components.components import app_layout



if __name__ == '__main__':
    print('DEBUG\n\n')
    print(model_state)
    model_state._debug()
    print('\n\n')

    app = dash.Dash(__name__)
    app.layout = app_layout(model_state)
    user_actions.register(app)

    app.run(debug=True)

# todos:
# - top prio: add optimization result callbacks and graph callbacks
# - nice to have: add functionality for toggling constraints on/off (buttons, callbacks, greying out)
# - define app_layout without relying on model_state (add containers for elements, populate from model state in app.py)
# - make it look pretty:
#   - fiddle with css
#   - add nicer components with Dash Mantine Components (DMC) https://www.dash-mantine-components.com/
# - fix bugs

# known issues:
# - reload browser page => UI refreshes, but not LP model => stale constraint IDs in UI => errors when changing constraints
#   - re-create initial model on reload?
# - with debug=True, model is optimized twice at startup
# - if the last constraint is deleted, add constraint button does nothing and throws callback error "cannot read properties of undefined (reading 'map')"
#   - separate callback for remove buttons?


# experimental findings, note for later: if we want to horizontally align bottom edge of 's.t.' label with bottom edge of first constraint row,
# we need to wrap 's.t.' label and first constraint row in a flex container together; this will require additional logic
# for dynamically adding/removing constraint rows while keeping 's.t.' label properly positioned.

# experimental findings: there's an alternative way to render math in dash by using mathjax.
# it's done by changing app initialization to:
# ```python
# app = dash.Dash(__name__, external_scripts=['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'] # unfortunately, external)
# ```
# then formulas are rendered by writing, for example, '\\(x\\)' or r'\(x\)' instead of dl.DashLatex(r'$x$')
# however, the mathjax approach is unfortunately unstable---math rendering breaks after a few page reloads


# docs: list of useful links about dash
# https://dash.plotly.com/pattern-matching-callbacks
# https://dash.plotly.com/advanced-callbacks
# https://dash.plotly.com/clientside-callbacks
# https://dash.plotly.com/flexible-callback-signatures
# https://dash.plotly.com/callback-gotchas
# https://dash.plotly.com/dash-core-components

# docs: python-mip documentation https://docs.python-mip.com/en/latest/name.dash.html
