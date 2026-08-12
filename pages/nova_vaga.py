from dash import html, dcc
import dash_mantine_components as dmc

from components.vaga_form import form_vaga


def layout() -> html.Div:
    return html.Div([
        dmc.Title("Nova Vaga", order=2, mb="lg"),
        dcc.Store(id="vaga-form-mode", data={"modo": "nova"}),
        dcc.Store(id="autofill-salary", data=None),
        dcc.Store(id="autofill-source", data=None),
        dcc.Store(id="form-saved-event", data=0),
        form_vaga(),
    ])