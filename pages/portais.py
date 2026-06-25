import dash
from dash import html, dcc, callback, Input, Output, State, ALL, callback_context, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from models import listar_portais, get_portal, criar_portal, atualizar_portal, excluir_portal
from components.forms import form_portal
from styles import (
    COR_TEXTO, COR_TEXTO_SEC, COR_BORDA, COR_PRIMARY,
    COR_SUPERFICIE, CARD_STYLE,
)


def _portal_card(portal: dict) -> html.Div:
    return html.Div(
        children=[
            html.Div([
                html.H5(portal["nome"], style={
                    "color": COR_TEXTO, "margin": 0, "fontWeight": 600,
                }),
                html.P(portal.get("url_base") or "", style={
                    "color": COR_TEXTO_SEC, "margin": "2px 0", "fontSize": "0.85rem",
                }),
                html.P(f"Login: {portal.get('tipo_login') or '—'}", style={
                    "color": COR_TEXTO_SEC, "margin": "2px 0", "fontSize": "0.85rem",
                }),
                html.P(f"Última atualização: {portal.get('ultima_atualizacao') or '—'}",
                        style={
                            "color": COR_TEXTO_SEC, "margin": "2px 0",
                            "fontSize": "0.85rem",
                        }),
                html.P(portal.get("notas") or "", style={
                    "color": COR_TEXTO_SEC, "margin": "4px 0", "fontSize": "0.8rem",
                }),
            ]),
            html.Div([
                html.Button(
                    "Editar",
                    id={"type": "btn-editar-portal", "index": portal["id"]},
                    className="btn btn-sm",
                    style={
                        "backgroundColor": "transparent",
                        "color": COR_PRIMARY,
                        "border": f"1px solid {COR_PRIMARY}",
                        "borderRadius": "6px",
                        "padding": "4px 14px",
                        "cursor": "pointer",
                        "marginRight": "8px",
                        "fontSize": "0.85rem",
                    },
                ),
                html.Button(
                    "Excluir",
                    id={"type": "btn-excluir-portal", "index": portal["id"]},
                    className="btn btn-sm",
                    style={
                        "backgroundColor": "transparent",
                        "color": "#DC3545",
                        "border": "1px solid #DC3545",
                        "borderRadius": "6px",
                        "padding": "4px 14px",
                        "cursor": "pointer",
                        "fontSize": "0.85rem",
                    },
                ),
            ], style={"display": "flex", "marginTop": "12px"}),
        ],
        style={**CARD_STYLE, "marginBottom": "12px"},
    )


def layout() -> html.Div:
    return html.Div([
        dcc.Store(id="portais-trigger", data=0),
        html.H2("Portais", style={
            "color": COR_TEXTO, "fontWeight": 600, "marginBottom": "24px",
        }),
        dbc.Row([
            dbc.Col(html.Div(id="portais-lista"), width=6),
            dbc.Col(html.Div(id="portais-form-wrapper"), width=6),
        ], className="g-4"),
    ])


@callback(
    Output("portais-lista", "children"),
    Input("portais-trigger", "data"),
)
def render_lista(_trigger):
    portais = listar_portais()
    if not portais:
        return html.P(
            "Nenhum portal cadastrado.",
            style={"color": COR_TEXTO_SEC},
        )
    return [_portal_card(p) for p in portais]


@callback(
    Output("portais-form-wrapper", "children"),
    Input("editing_portal_id", "data"),
)
def render_form(edit_id):
    if edit_id:
        portal = get_portal(edit_id)
        return form_portal(portal)
    return form_portal()


@callback(
    Output("editing_portal_id", "data", allow_duplicate=True),
    Input({"type": "btn-editar-portal", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def editar_portal(n_clicks_list):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    return ctx.triggered_id["index"]


@callback(
    Output("portais-trigger", "data", allow_duplicate=True),
    Output("notification", "data", allow_duplicate=True),
    Input({"type": "btn-excluir-portal", "index": ALL}, "n_clicks"),
    State("portais-trigger", "data"),
    prevent_initial_call=True,
)
def excluir_portal_callback(n_clicks_list, trigger):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    clicked_n = ctx.triggered[0]["value"]
    if not clicked_n:
        raise PreventUpdate
    portal_id = ctx.triggered_id["index"]
    excluir_portal(portal_id)
    return trigger + 1, {"message": "Portal excluído!", "type": "success"}


@callback(
    Output("portais-trigger", "data", allow_duplicate=True),
    Output("editing_portal_id", "data", allow_duplicate=True),
    Output("notification", "data", allow_duplicate=True),
    Input("btn-salvar-portal", "n_clicks"),
    State("form-portal-nome", "value"),
    State("form-portal-url", "value"),
    State("form-portal-login", "value"),
    State("form-portal-data", "date"),
    State("form-portal-notas", "value"),
    State("editing_portal_id", "data"),
    State("portais-trigger", "data"),
    prevent_initial_call=True,
)
def salvar_portal(n_clicks, nome, url, login, data, notas, edit_id, trigger):
    if not n_clicks:
        raise PreventUpdate
    nome = (nome or "").strip()
    if not nome:
        return no_update, no_update, {
            "message": "Nome é obrigatório", "type": "warning",
        }
    if edit_id:
        atualizar_portal(edit_id, nome, url or "", login or "", notas or "")
        msg = "Portal atualizado com sucesso!"
    else:
        criar_portal(nome, url or "", login or "", notas or "")
        msg = "Portal criado com sucesso!"
    return trigger + 1, None, {"message": msg, "type": "success"}
