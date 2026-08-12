from dash import html, dcc, callback, Input, Output, State, callback_context, no_update, ALL
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from db.models import get_vaga, listar_historico, atualizar_vaga, excluir_vaga, get_tags_da_vaga
from components.pipeline import pipeline_view
from components.forms import form_editar_vaga
from styles import (
    COR_TEXTO, COR_DESTAQUE,
    COLUNA_ESTILO,
)

STATUS_OPCOES = [
    {"label": s, "value": s}
    for s in ["Interessado", "Currículo Enviado", "Entrevista Agendada",
              "Em Processo", "Oferta", "Aceito", "Rejeitado"]
]


def _info_campo(label, valor):
    if isinstance(valor, str) and (valor.startswith("http://") or valor.startswith("https://")):
        valor_elem = dmc.Anchor(
            valor, href=valor, target="_blank",
            underline="always", fz="sm",
        )
    else:
        valor_elem = dmc.Text(valor or "—", fz="sm", mt=2)
    return html.Div(
        children=[
            dmc.Text(
                label,
                fz="xs", fw=600, tt="uppercase", c="dimmed",
            ),
            valor_elem,
        ],
        style=COLUNA_ESTILO,
    )


def layout() -> html.Div:
    return html.Div([
        dcc.Store(id="vaga-id-store", data=None),
        dcc.Store(id="detalhe-trigger", data=0),
        html.Div(id="page-content-placeholder"),
    ])


@callback(
    Output("page-content-placeholder", "children"),
    Output("vaga-id-store", "data"),
    Input("detalhe-trigger", "data"),
    State("url", "pathname"),
)
def display_page(trigger, pathname):
    if not pathname.startswith("/vagas/"):
        raise PreventUpdate

    try:
        vaga_id = int(pathname.split("/")[-1])
    except (ValueError, IndexError):
        raise PreventUpdate

    vaga = get_vaga(vaga_id)
    if not vaga:
        return html.Div([
            dmc.Title("Vaga não encontrada", order=2, c="dimmed"),
            dcc.Link("Voltar para Listar Vagas", href="/vagas"),
        ]), None

    tags = get_tags_da_vaga(vaga_id)
    vaga["_tags"] = tags
    historico = listar_historico(vaga_id)
    vaga["_historico"] = historico

    return detalhes_vaga(vaga), vaga_id


def _textarea_leitura(valor: str) -> dmc.Textarea:
    return dmc.Textarea(
        value=valor or "",
        readOnly=True,
        minRows=6,
        style={"fontFamily": "var(--mantine-font-family-monospace)"},
    )


def detalhes_vaga(vaga: dict) -> html.Div:
    vaga_id = vaga["id"]

    return html.Div([
        dmc.Grid(
            gutter="lg",
            children=[
                dmc.GridCol(
                    span=12,
                    children=[
                        dmc.Title(
                            f"{vaga.get('nome', 'Sem nome')} - {vaga.get('empresa') or 'Confidencial'}",
                            order=3,
                        ),
                        dmc.Text(f"ID: {vaga_id}", c="dimmed", size="sm", mt="xs"),
                    ],
                ),
                dmc.GridCol(
                    span=6,
                    children=dmc.Paper(
                        p="lg", radius="md", shadow="sm", withBorder=True,
                        children=[
                            dmc.Title("Informações", order=5, mb="lg"),
                            dmc.Stack(gap="sm", children=[
                                _info_campo("Nome", vaga.get("nome")),
                                _info_campo("Empresa", vaga.get("empresa") or "Confidencial"),
                                _info_campo("Link", vaga.get("link") or "—"),
                                _info_campo("Modalidade", vaga.get("modalidade") or "—"),
                                _info_campo("Interesse", vaga.get("interesse") or "—"),
                                _info_campo("Aderência", vaga.get("aderencia") or "—"),
                                _info_campo("Status", vaga.get("status") or "—"),
                                _info_campo("Data Encontrada", vaga.get("data_encontrada") or "—"),
                                _info_campo("Data Envio", vaga.get("data_envio") or "⏳ Não enviado"),
                                _info_campo("Portal", vaga.get("portal_nome") or "Sem portal"),
                            ]),
                        ],
                    ),
                ),
                dmc.GridCol(
                    span=6,
                    children=dmc.Paper(
                        p="lg", radius="md", shadow="sm", withBorder=True,
                        children=[
                            html.Div(
                                dmc.Text("📄 Descrição", fw=600, fz="lg", c=COR_TEXTO),
                                id="btn-toggle-descricao",
                                n_clicks=0,
                                style={"cursor": "pointer", "marginBottom": "12px"},
                            ),
                            dmc.Collapse(
                                id="collapse-descricao",
                                opened=False,
                                children=_textarea_leitura(vaga.get("descricao")),
                            ),
                        ],
                    ),
                ),
                dmc.GridCol(
                    span=6,
                    children=dmc.Paper(
                        p="lg", radius="md", shadow="sm", withBorder=True,
                        children=[
                            html.Div(
                                dmc.Text("📝 Notas", fw=600, fz="lg", c=COR_TEXTO),
                                id="btn-toggle-notas",
                                n_clicks=0,
                                style={"cursor": "pointer", "marginBottom": "12px"},
                            ),
                            dmc.Collapse(
                                id="collapse-notas",
                                opened=False,
                                children=_textarea_leitura(vaga.get("notas")),
                            ),
                        ],
                    ),
                ),
                dmc.GridCol(
                    span=4,
                    children=dmc.Paper(
                        p="lg", radius="md", shadow="sm", withBorder=True,
                        children=[
                            dmc.Title("Tags", order=5, mb="md"),
                            dmc.Group(gap=6, children=[
                                *[
                                    dmc.Badge(
                                        tag["nome"] if isinstance(tag, dict) else tag,
                                        variant="light",
                                        color=COR_DESTAQUE,
                                        radius="xl",
                                        size="sm",
                                    )
                                    for tag in vaga.get("_tags", [])
                                ],
                            ]),
                        ],
                    ),
                ),
                dmc.GridCol(
                    span=8,
                    children=dmc.Paper(
                        p="lg", radius="md", shadow="sm", withBorder=True,
                        children=[
                            dmc.Title("Pipeline", order=5, mb="md"),
                            pipeline_view(vaga.get("status", "Interessado")),
                        ],
                    ),
                ),
                dmc.GridCol(
                    span=12,
                    children=dmc.Paper(
                        p="lg", radius="md", shadow="sm", withBorder=True,
                        children=[
                            html.Div(
                                dmc.Text("📜 Histórico de Status", fw=600, fz="lg", c=COR_TEXTO),
                                id="btn-toggle-historico",
                                n_clicks=0,
                                style={"cursor": "pointer", "marginBottom": "12px"},
                            ),
                            dmc.Collapse(
                                id="collapse-historico",
                                opened=False,
                                children=html.Div(
                                    children=[
                                        html.Div([
                                            dmc.Text(
                                                f"{h.get('data_mudanca', '—')}: ",
                                                span=True,
                                                c="dimmed",
                                                fw=700,
                                            ),
                                            dmc.Text(
                                                f"{h.get('status_anterior', '—')} → {h.get('status_novo', '—')}",
                                                span=True,
                                            ),
                                        ], style={"marginBottom": "8px"})
                                        for h in vaga.get("_historico", [])
                                    ],
                                    style={"padding": "16px"},
                                ),
                            ),
                        ],
                    ),
                ),
                dmc.GridCol(
                    span=12,
                    children=dmc.Paper(
                        p="lg", radius="md", shadow="sm", withBorder=True,
                        children=[
                            dmc.Title("Alterar Status", order=5, mb="md"),
                            dmc.Group(
                                align="flex-end",
                                children=[
                                    dmc.Select(
                                        id="status-dropdown",
                                        label="Status",
                                        data=STATUS_OPCOES,
                                        value=vaga.get("status", "Interessado"),
                                        style={"flex": 1},
                                    ),
                                    dmc.Button(
                                        "Atualizar Status",
                                        id="btn-atualizar-status",
                                        color="teal",
                                        variant="filled",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                dmc.GridCol(
                    span=12,
                    children=dmc.Group(
                        mt="lg",
                        children=[
                            dmc.Button(
                                "Editar",
                                id={"type": "btn-editar-vaga", "index": vaga_id},
                                color="teal",
                                variant="filled",
                            ),
                            dmc.Button(
                                "Excluir",
                                id={"type": "btn-excluir-vaga-detalhe", "index": vaga_id},
                                color="red",
                                variant="filled",
                            ),
                        ],
                    ),
                ),
            ],
        ),
        html.Div(id="edit-mode-placeholder", style={"marginTop": "32px"}),
    ])


@callback(
    Output({"type": "btn-editar-vaga", "index": ALL}, "n_clicks"),
    Output("edit-mode-placeholder", "children"),
    Input({"type": "btn-editar-vaga", "index": ALL}, "n_clicks"),
    State("vaga-id-store", "data"),
    prevent_initial_call=True,
)
def editar_vaga(n_clicks_list, vaga_id):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    clicked_n = ctx.triggered[0]["value"]
    if not clicked_n:
        raise PreventUpdate

    n_clicks_list = n_clicks_list or []
    new_clicks = [None] * len(n_clicks_list)

    vaga = get_vaga(vaga_id)
    if not vaga:
        return new_clicks, html.Div([
            dmc.Text("Vaga não encontrada", c="red"),
        ])

    return new_clicks, form_editar_vaga(vaga)


@callback(
    Output("edit-mode-placeholder", "children", allow_duplicate=True),
    Output("notification", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input({"type": "btn-excluir-vaga-detalhe", "index": ALL}, "n_clicks"),
    State("vaga-id-store", "data"),
    prevent_initial_call=True,
)
def excluir_vaga_detalhe(n_clicks_list, vaga_id):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    clicked_n = ctx.triggered[0]["value"]
    if not clicked_n:
        raise PreventUpdate

    if not vaga_id:
        raise PreventUpdate
    if ctx.triggered_id.get("index") != vaga_id:
        raise PreventUpdate

    try:
        excluir_vaga(vaga_id)
        return None, {"message": "Vaga excluída!", "type": "success"}, "/vagas"
    except Exception as e:
        return None, {"message": f"Erro ao excluir vaga: {str(e)}", "type": "danger"}, no_update


@callback(
    Output("status-dropdown", "value", allow_duplicate=True),
    Output("notification", "data", allow_duplicate=True),
    Input("btn-atualizar-status", "n_clicks"),
    State("status-dropdown", "value"),
    State("vaga-id-store", "data"),
    prevent_initial_call=True,
)
def atualizar_status(n_clicks, novo_status, vaga_id):
    if not n_clicks or not novo_status or not vaga_id:
        raise PreventUpdate

    vaga = get_vaga(vaga_id)
    if not vaga:
        return no_update, {"message": "Vaga não encontrada", "type": "danger"}

    if vaga.get("status") == novo_status:
        return no_update, {"message": "Status já está definido", "type": "info"}

    try:
        atualizar_vaga(vaga_id, **{
            "nome": vaga.get("nome") or "",
            "empresa": vaga.get("empresa") or "",
            "link": vaga.get("link") or "",
            "salario": vaga.get("salario") or None,
            "salario_max": vaga.get("salario_max") or None,
            "modalidade": vaga.get("modalidade") or "",
            "descricao": vaga.get("descricao") or "",
            "interesse": vaga.get("interesse") or 3,
            "aderencia": vaga.get("aderencia") or 3,
            "status": novo_status,
            "portal_id": vaga.get("portal_id") or None,
            "data_encontrada": vaga.get("data_encontrada") or "",
            "data_envio": vaga.get("data_envio") or "",
            "notas": vaga.get("notas") or "",
            "tag_ids": [t.get("id") if isinstance(t, dict) else t for t in vaga.get("_tags", [])],
        })
        return novo_status, {"message": "Status atualizado com sucesso!", "type": "success"}
    except Exception as e:
        return no_update, {"message": f"Erro ao atualizar status: {str(e)}", "type": "danger"}


@callback(
    Output("notification", "data", allow_duplicate=True),
    Input("btn-salvar-edicao", "n_clicks"),
    State("edit-vaga-nome", "value"),
    State("edit-vaga-empresa", "value"),
    State("edit-vaga-link", "value"),
    State("edit-vaga-salario", "value"),
    State("edit-vaga-salario-max", "value"),
    State("edit-vaga-modalidade", "value"),
    State("edit-vaga-portal", "value"),
    State("edit-vaga-data-encontrada", "value"),
    State("edit-vaga-data-envio", "value"),
    State("edit-vaga-interesse", "value"),
    State("edit-vaga-aderencia", "value"),
    State("edit-vaga-tags", "value"),
    State("edit-vaga-descricao", "value"),
    State("edit-vaga-notas", "value"),
    State("vaga-id-store", "data"),
    prevent_initial_call=True,
)
def salvar_edicao_vaga(
    n_clicks, nome, empresa, link, salario, salario_max, modalidade,
    portal, data_encontrada, data_envio, interesse, aderencia, tag_ids,
    descricao, notas, vaga_id
):
    if not n_clicks:
        raise PreventUpdate

    nome = (nome or "").strip()
    if not nome:
        return {"message": "Nome é obrigatório", "type": "warning"}

    tag_ids = tag_ids or []
    vaga_atual = get_vaga(vaga_id)
    if not vaga_atual:
        return {"message": "Vaga não encontrada", "type": "danger"}
    try:
        atualizar_vaga(
            vaga_id,
            nome=nome,
            empresa=empresa or "",
            link=link or "",
            salario=float(salario) if salario else None,
            salario_max=float(salario_max) if salario_max else None,
            modalidade=modalidade or "",
            descricao=descricao or "",
            interesse=int(interesse) if interesse else 3,
            aderencia=int(aderencia) if aderencia else 3,
            status=vaga_atual.get("status") or "Interessado",
            portal_id=int(portal) if portal and portal != "" else None,
            data_encontrada=data_encontrada or "",
            data_envio=data_envio or "",
            notas=notas or "",
            tag_ids=[int(t) for t in tag_ids] if tag_ids else None,
            data_publicacao=vaga_atual.get("data_publicacao") or "",
            fonte_id=vaga_atual.get("fonte_id") or "",
        )
        return {"message": "Vaga atualizada com sucesso!", "type": "success"}
    except Exception as e:
        return {"message": f"Erro ao atualizar vaga: {str(e)}", "type": "danger"}


@callback(
    Output("collapse-descricao", "opened"),
    Input("btn-toggle-descricao", "n_clicks"),
    State("collapse-descricao", "opened"),
    prevent_initial_call=True,
)
def toggle_descricao(n_clicks, is_open):
    if not n_clicks:
        raise PreventUpdate
    return not is_open


@callback(
    Output("collapse-notas", "opened"),
    Input("btn-toggle-notas", "n_clicks"),
    State("collapse-notas", "opened"),
    prevent_initial_call=True,
)
def toggle_notas(n_clicks, is_open):
    if not n_clicks:
        raise PreventUpdate
    return not is_open


@callback(
    Output("collapse-historico", "opened"),
    Input("btn-toggle-historico", "n_clicks"),
    State("collapse-historico", "opened"),
    prevent_initial_call=True,
)
def toggle_historico(n_clicks, is_open):
    if not n_clicks:
        raise PreventUpdate
    return not is_open