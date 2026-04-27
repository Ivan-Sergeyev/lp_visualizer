from collections.abc import Callable
from typing import Literal, TypedDict

import dash
import dash_iconify
import dash_latex as dl

from components.common import StorageType
from model.constraint import CONSTRAINT_SENSES, Constraint

type NameOrWildcard = (
    str
    | Literal[dash.dependencies.Wildcard.ALL]
    | Literal[dash.dependencies.Wildcard.MATCH]
    | Literal[dash.dependencies.Wildcard.ALLSMALLER]
)
type NameToType = Callable[[NameOrWildcard], dict[str, NameOrWildcard]]
ConstraintIDs = TypedDict('ConstraintIDs', {
    'row': NameToType,
    'coeff_x': NameToType,
    'sign_label': NameToType,
    'coeff_y': NameToType,
    'sense': NameToType,
    'rhs': NameToType,
    'remove_button': NameToType,
    'store': NameToType,
})


def type_name_id(type_str: NameOrWildcard) -> NameToType:
    return lambda name : {'type': type_str, 'name': name}


CONSTRAINT_IDS = {
    'row': type_name_id('constraint-row'),
    'coeff_x': type_name_id('constraint-coeff-x'),
    'sign_label': type_name_id('constraint-sign-label'),
    'coeff_y': type_name_id('constraint-coeff-y'),
    'sense': type_name_id('constraint-sense'),
    'rhs': type_name_id('constraint-rhs'),
    'remove_button': type_name_id('remove-constraint-button'),
    'store': type_name_id('constraint-store'),
}


def constraint_layout(name: str, constraint: Constraint) -> dash.html.Div:
    return dash.html.Div(
        id=CONSTRAINT_IDS['row'](name),
        className='constraint-row',
        children=[
            dash.dcc.Input(
                id=CONSTRAINT_IDS['coeff_x'](name),
                className='coeff-input',
                type='number',
                inputMode='numeric',
                value=constraint.coeff_x,
                debounce=True,
                placeholder='Coefficient for x',
            ),
            dash.html.Div(
                dl.DashLatex(r'$x$'),
                className='variable-label',
            ),
            dash.html.Div(
                dl.DashLatex(r'$+$'),
                id=CONSTRAINT_IDS['sign_label'](name),
                className='sign-label',
            ),
            dash.dcc.Input(
                id=CONSTRAINT_IDS['coeff_y'](name),
                className='coeff-input',
                type='number',
                inputMode='numeric',
                value=constraint.coeff_y,
                debounce=True,
                placeholder='Coefficient for y',
            ),
            dash.html.Div(
                dl.DashLatex(r'$y$'),
                className='variable-label',
            ),
            dash.dcc.Dropdown(
                id=CONSTRAINT_IDS['sense'](name),
                className='constraint-sense',
                options=CONSTRAINT_SENSES,
                value=str(constraint.sense),
                clearable=False,
                searchable=False,
                placeholder='Constraint sense',
            ),
            dash.dcc.Input(
                id=CONSTRAINT_IDS['rhs'](name),
                className='coeff-input',
                type='number',
                inputMode='numeric',
                value=constraint.rhs,
                debounce=True,
                placeholder='Right hand side',
            ),
            dash.dcc.Button(
                id=CONSTRAINT_IDS['remove_button'](name),
                name=name,
                className='button remove-constraint-button',
                title='Remove constraint',
                children=[
                    dash_iconify.DashIconify(icon='mdi:trash-can-outline')
                ],
                n_clicks=0,
            ),
        ],
    )


def constraint_store(name: str, constraint: Constraint, storage_type: StorageType) -> dash.dcc.Store:
    return dash.dcc.Store(
        id=CONSTRAINT_IDS['store'](name),
        storage_type=storage_type,
        data=constraint.to_dict(),
    )
