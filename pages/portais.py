from dash import html, dcc, callback, Input, Output, State, ALL, callback_context, no_update
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from models import listar_portais, get_portal, criar_portal, atualizar_portal, excluir_portal
from components.forms import form_portal


def _portal_card(portal: dict):
    return dmc.Paper(
        p="lg",
        radius="md",
        shadow="sm",
        withBorder=True,
        mb="sm",
        children=[
            dmc.Title(portal["nome"], order=5),
            dmc.Text(portal.get("url_base") or "", size="sm", c="dimmed"),
            dmc.Text(f"Login: {portal.get('tipo_login') or '—'}",
                     size="xs", c="dimmed"),
            dmc.Text(f"Última atualização: {portal.get('ultima_atualizacao') or '—'}",
                     size="xs", c="dimmed"),
            dmc.Text(portal.get("notas") or "", size="sm", c="dimmed", mt="xs"),
            dmc.Group(
                mt="md",
                children=[
                    dmc.Button(
                        "Editar",
                        id={"type": "btn-editar-portal", "index": portal["id"]},
                        variant="outline",
                        color="teal",
                        size="xs",
                    ),
                    dmc.Button(
                        "Excluir",
                        id={"type": "btn-excluir-portal", "index": portal["id"]},
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
        dcc.Store(id="portais-trigger", data=0),
        dmc.Title("Portais", order=2, mb="lg"),
        dmc.Grid(
            gutter="lg",
            children=[
                dmc.GridCol(html.Div(id="portais-lista"), span=6),
                dmc.GridCol(html.Div(id="portais-form-wrapper"), span=6),
            ],
        ),
    ])


@callback(
    Output("portais-lista", "children"),
    Input("portais-trigger", "data"),
)
def render_lista(_trigger):
    portais = listar_portais()
    if not portais:
        return dmc.Text("Nenhum portal cadastrado.", c="dimmed")
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
    clicked_n = ctx.triggered[0]["value"]
    if not clicked_n:
        raise PreventUpdate
    return ctx.triggered_id["index"]


@callback(
    Output("editing_portal_id", "data", allow_duplicate=True),
    Input("btn-cancelar-edicao-portal", "n_clicks"),
    prevent_initial_call=True,
)
def cancelar_edicao_portal(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    return None


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
    State("form-portal-data", "value"),
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
        atualizar_portal(edit_id, nome, url or "", login or "", notas or "",
                         data or "")
        msg = "Portal atualizado com sucesso!"
    else:
        criar_portal(nome, url or "", login or "", notas or "", data or "")
        msg = "Portal criado com sucesso!"
    return trigger + 1, None, {"message": msg, "type": "success"}