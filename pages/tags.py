from dash import html, dcc, callback, Input, Output, State, ALL, callback_context, no_update
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from models import listar_tags, get_tag, criar_tag, renomear_tag, excluir_tag
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
            dmc.Group(
                gap="xs",
                children=[
                    dmc.Button(
                        "Editar",
                        id={"type": "btn-editar-tag", "index": tag["id"]},
                        variant="outline",
                        color="teal",
                        size="xs",
                    ),
                    dmc.Button(
                        "Excluir",
                        id={"type": "btn-excluir-tag", "index": tag["id"]},
                        variant="outline",
                        color="red",
                        size="xs",
                    ),
                ],
            ),
        ],
    )


def layout() -> html.Div:
    return html.Div([
        dcc.Store(id="tags-trigger", data=0),
        dcc.Store(id="editing_tag_id", data=None),
        dcc.Store(id="excluir_tag_id", data=None),
        dmc.Title("Tags", order=2, mb="lg"),
        dmc.Grid(
            gutter="lg",
            children=[
                dmc.GridCol(html.Div(id="tags-lista"), span=6),
                dmc.GridCol(
                    html.Div(
                        id="tags-form-wrapper",
                    ),
                    span=6,
                ),
            ],
        ),
        dmc.Modal(
            id="modal-confirmar-exclusao-tag",
            opened=False,
            title="Excluir Tag",
            centered=True,
            children=[
                dmc.Text(
                    "Tem certeza que deseja excluir esta tag? "
                    "Essa ação não pode ser desfeita.",
                    mb="md",
                ),
                dmc.Group(
                    justify="flex-end",
                    children=[
                        dmc.Button(
                            "Cancelar",
                            id="btn-cancelar-exclusao-tag",
                            variant="default",
                        ),
                        dmc.Button(
                            "Excluir",
                            id="btn-confirmar-exclusao-tag",
                            color="red",
                            variant="filled",
                        ),
                    ],
                ),
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
    Input("editing_tag_id", "data"),
)
def render_form(_trigger, edit_id):
    if edit_id:
        tag = get_tag(edit_id)
        if tag:
            return form_tag(nome=tag["nome"], tag_id=tag["id"])
    return form_tag()


@callback(
    Output("editing_tag_id", "data", allow_duplicate=True),
    Input({"type": "btn-editar-tag", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def editar_tag(n_clicks_list):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    clicked_n = ctx.triggered[0]["value"]
    if not clicked_n:
        raise PreventUpdate
    return ctx.triggered_id["index"]


@callback(
    Output("editing_tag_id", "data", allow_duplicate=True),
    Input("btn-cancelar-edicao-tag", "n_clicks"),
    prevent_initial_call=True,
)
def cancelar_edicao_tag(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    return None


@callback(
    Output("excluir_tag_id", "data", allow_duplicate=True),
    Output("modal-confirmar-exclusao-tag", "opened", allow_duplicate=True),
    Input({"type": "btn-excluir-tag", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def abrir_exclusao(n_clicks_list):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    clicked_n = ctx.triggered[0]["value"]
    if not clicked_n:
        raise PreventUpdate
    return ctx.triggered_id["index"], True


@callback(
    Output("excluir_tag_id", "data", allow_duplicate=True),
    Output("modal-confirmar-exclusao-tag", "opened", allow_duplicate=True),
    Input("btn-cancelar-exclusao-tag", "n_clicks"),
    prevent_initial_call=True,
)
def cancelar_exclusao(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    return None, False


@callback(
    Output("tags-trigger", "data", allow_duplicate=True),
    Output("excluir_tag_id", "data", allow_duplicate=True),
    Output("modal-confirmar-exclusao-tag", "opened", allow_duplicate=True),
    Output("notification", "data", allow_duplicate=True),
    Input("btn-confirmar-exclusao-tag", "n_clicks"),
    State("excluir_tag_id", "data"),
    State("tags-trigger", "data"),
    prevent_initial_call=True,
)
def confirmar_exclusao(n_clicks, tag_id, trigger):
    if not n_clicks or not tag_id:
        raise PreventUpdate
    excluir_tag(tag_id)
    return trigger + 1, None, False, {
        "message": "Tag excluída!", "type": "success",
    }


@callback(
    Output("tags-trigger", "data", allow_duplicate=True),
    Output("editing_tag_id", "data", allow_duplicate=True),
    Output("notification", "data", allow_duplicate=True),
    Input("btn-add-tag", "n_clicks"),
    Input("form-tag-nome", "n_submit"),
    State("form-tag-nome", "value"),
    State("editing_tag_id", "data"),
    State("tags-trigger", "data"),
    prevent_initial_call=True,
)
def salvar_tag(n_clicks, n_submit, nome, edit_id, trigger):
    if not n_clicks and not n_submit:
        raise PreventUpdate
    nome = (nome or "").strip()
    if not nome:
        return no_update, no_update, {
            "message": "Nome é obrigatório", "type": "warning",
        }
    if edit_id:
        if not renomear_tag(edit_id, nome):
            return no_update, no_update, {
                "message": "Já existe uma tag com esse nome", "type": "danger",
            }
        msg = f"Tag '{nome.strip().lower()}' atualizada!"
    else:
        criar_tag(nome)
        msg = f"Tag '{nome.strip().lower()}' adicionada!"
    return trigger + 1, None, {"message": msg, "type": "success"}