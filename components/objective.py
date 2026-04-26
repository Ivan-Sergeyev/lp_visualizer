from typing import TypedDict

import dash
import dash_latex as dl

from components.common import StorageType
from model.objective import OBJECTIVE_SENSES, Objective


class ObjectiveIDs(TypedDict):
    sense: str
    coeff_x: str
    sign_label: str
    coeff_y: str
    store: str


OBJECTIVE_IDS: ObjectiveIDs = {
    'sense': 'objective-sense',
    'coeff_x': 'objective-coeff-x',
    'sign_label': 'objective-sign-label',
    'coeff_y': 'objective-coeff-y',
    'store': 'objective-store',
}


def objective_layout(objective: Objective) -> dash.html.Div:
    return dash.html.Div(
        id='objective-row',
        children=[
            dash.dcc.Dropdown(
                id=OBJECTIVE_IDS['sense'],
                options=OBJECTIVE_SENSES,
                value=str(objective.sense),
                clearable=False,
                searchable=False,
                placeholder='Objective sense',
            ),
            dash.dcc.Input(
                id=OBJECTIVE_IDS['coeff_x'],
                className='coeff-input',
                type='number',
                inputMode='numeric',
                value=objective.coeff_x,
                debounce=True,
                placeholder='Coefficient for x',
            ),
            dash.html.Div(
                dl.DashLatex(r'$x$'),
                className='variable-label',
            ),
            dash.html.Div(
                dl.DashLatex(r'$+$'),
                id=OBJECTIVE_IDS['sign_label'],
                className='sign-label',
            ),
            dash.dcc.Input(
                id=OBJECTIVE_IDS['coeff_y'],
                className='coeff-input',
                type='number',
                inputMode='numeric',
                value=objective.coeff_y,
                debounce=True,
                placeholder='Coefficient for y',
            ),
            dash.html.Div(
                dl.DashLatex(r'$y$'),
                className='variable-label'
            ),
        ],
    )


def objective_store(objective: Objective, storage_type: StorageType) -> dash.dcc.Store:
    return dash.dcc.Store(
        id=OBJECTIVE_IDS['store'],
        storage_type=storage_type,
        data=objective.to_dict(),
    )
