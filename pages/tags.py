import dash
from dash import html, dcc, callback, Input, Output, State, ALL, callback_context, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from models import listar_tags, criar_tag, excluir_tag
from components.forms import form_tag
from styles import (
    COR_TEXTO, COR_TEXTO_SEC, COR_BORDA, COR_PRIMARY,
    CARD_STYLE, tag_style,
)


def _tag_item(tag: dict) -> html.Div:
    return html.Div(
        children=[
            html.Span(f"🏷️ {tag['nome']}", style={
                "color": COR_TEXTO, "fontSize": "0.95rem",
            }),
            html.Button(
                "Excluir",
                id={"type": "btn-excluir-tag", "index": tag["id"]},
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
        ],
        style={
            **CARD_STYLE,
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "marginBottom": "8px",
            "padding": "12px 20px",
        },
    )


def layout() -> html.Div:
    return html.Div([
        dcc.Store(id="tags-trigger", data=0),
        html.H2("Tags", style={
            "color": COR_TEXTO, "fontWeight": 600, "marginBottom": "24px",
        }),
        dbc.Row([
            dbc.Col(html.Div(id="tags-lista"), width=6),
            dbc.Col(html.Div(id="tags-form-wrapper"), width=6),
        ], className="g-4"),
    ])


@callback(
    Output("tags-lista", "children"),
    Input("tags-trigger", "data"),
)
def render_lista(_trigger):
    tags = listar_tags()
    if not tags:
        return html.P(
            "Nenhuma tag cadastrada.",
            style={"color": COR_TEXTO_SEC},
        )
    return [_tag_item(t) for t in tags]


@callback(
    Output("tags-form-wrapper", "children"),
    Input("tags-trigger", "data"),
)
def render_form(_trigger):
    return form_tag()


@callback(
    Output("tags-trigger", "data", allow_duplicate=True),
    Output("notification", "data", allow_duplicate=True),
    Input({"type": "btn-excluir-tag", "index": ALL}, "n_clicks"),
    State("tags-trigger", "data"),
    prevent_initial_call=True,
)
def excluir_tag_callback(n_clicks_list, trigger):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    clicked_n = ctx.triggered[0]["value"]
    if not clicked_n:
        raise PreventUpdate
    tag_id = ctx.triggered_id["index"]
    excluir_tag(tag_id)
    return trigger + 1, {"message": "Tag excluída!", "type": "success"}


@callback(
    Output("tags-trigger", "data", allow_duplicate=True),
    Output("notification", "data", allow_duplicate=True),
    Input("btn-add-tag", "n_clicks"),
    State("form-tag-nome", "value"),
    State("tags-trigger", "data"),
    prevent_initial_call=True,
)
def adicionar_tag(n_clicks, nome, trigger):
    if not n_clicks:
        raise PreventUpdate
    nome = (nome or "").strip()
    if not nome:
        return no_update, {"message": "Nome é obrigatório", "type": "warning"}
    criar_tag(nome)
    return trigger + 1, {"message": f"Tag '{nome}' adicionada!", "type": "success"}
