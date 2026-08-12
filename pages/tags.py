from dash import html, dcc, callback, Input, Output, State, ALL, callback_context, no_update
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from models import listar_tags, criar_tag, excluir_tag
from components.forms import form_tag


def _tag_item(tag: dict):
    return dmc.Paper(
        p="md",
        radius="md",
        shadow="sm",
        withBorder=True,
        mb="sm",
        style={"display": "flex", "justifyContent": "space-between",
               "alignItems": "center"},
        children=[
            dmc.Text(f"🏷️ {tag['nome']}", fw=500),
            dmc.Button(
                "Excluir",
                id={"type": "btn-excluir-tag", "index": tag["id"]},
                variant="outline",
                color="red",
                size="xs",
            ),
        ],
    )


def layout() -> html.Div:
    return html.Div([
        dcc.Store(id="tags-trigger", data=0),
        dmc.Title("Tags", order=2, mb="lg"),
        dmc.Grid(
            gutter="lg",
            children=[
                dmc.GridCol(html.Div(id="tags-lista"), span=6),
                dmc.GridCol(html.Div(id="tags-form-wrapper"), span=6),
            ],
        ),
    ])


@callback(
    Output("tags-lista", "children"),
    Input("tags-trigger", "data"),
)
def render_lista(_trigger):
    tags = listar_tags()
    if not tags:
        return dmc.Text("Nenhuma tag cadastrada.", c="dimmed")
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
    Input("form-tag-nome", "n_submit"),
    State("form-tag-nome", "value"),
    State("tags-trigger", "data"),
    prevent_initial_call=True,
)
def adicionar_tag(n_clicks, n_submit, nome, trigger):
    if not n_clicks and not n_submit:
        raise PreventUpdate
    nome = (nome or "").strip()
    if not nome:
        return no_update, {"message": "Nome é obrigatório", "type": "warning"}
    criar_tag(nome)
    return trigger + 1, {"message": f"Tag '{nome}' adicionada!", "type": "success"}