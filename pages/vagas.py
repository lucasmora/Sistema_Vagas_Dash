from dash import html, dcc, callback, Input, Output
import dash_mantine_components as dmc

from db.models import listar_vagas, listar_tags, listar_portais
from components.cards import vaga_card
from styles import STATUS_ORDEM


def _vaga_item(vaga: dict) -> html.Div:
    return vaga_card(vaga, vaga.get("portal_nome") or "Sem portal")


def layout() -> html.Div:
    statuses = STATUS_ORDEM

    return html.Div([
        dcc.Store(id="vagas-trigger", data=0),
        dmc.Title("Vagas", order=2, mb="lg"),
        dmc.Grid(
            gutter="lg",
            children=[
                dmc.GridCol(
                    span=3,
                    children=dmc.Paper(
                        p="lg",
                        radius="md",
                        shadow="sm",
                        withBorder=True,
                        children=[
                            dmc.Title("Filtros", order=5, mb="md"),
                            dmc.CheckboxGroup(
                                id="filtro-status",
                                label="Status",
                                labelProps={"style": {"marginBottom": "12px"}},
                                value=[],
                                children=[
                                    html.Div(
                                        dmc.Checkbox(label=s, value=s),
                                        style={"marginBottom": "12px"},
                                    )
                                    for s in statuses
                                ],
                            ),
                            dmc.Divider(my="lg"),
                            dmc.Select(
                                id="filtro-portal",
                                label="Portal",
                                labelProps={"style": {"marginBottom": "12px"}},
                                data=[{"label": "Todos", "value": ""}],
                                allowDeselect=False,
                                value="",
                            ),
                            dmc.Divider(my="lg"),
                            dmc.Select(
                                id="filtro-tag",
                                label="Tag",
                                labelProps={"style": {"marginBottom": "12px"}},
                                data=[{"label": "Todas", "value": ""}],
                                allowDeselect=False,
                                value="",
                            ),
                            dmc.Divider(my="lg"),
                            dmc.TextInput(
                                id="filtro-busca",
                                label="Busca",
                                labelProps={"style": {"marginBottom": "12px"}},
                                placeholder="Busca por nome, empresa...",
                            ),
                        ],
                    ),
                ),
                dmc.GridCol(html.Div(id="vagas-lista"), span=9),
            ],
        ),
    ])


@callback(
    Output("filtro-portal", "data"),
    Input("vagas-trigger", "data"),
)
def atualizar_opcoes_portais(trigger):
    portais = listar_portais()
    opcoes = [{"label": "Todos", "value": ""}]
    for p in portais:
        opcoes.append({"label": p["nome"], "value": str(p["id"])})
    return opcoes


@callback(
    Output("filtro-tag", "data"),
    Input("vagas-trigger", "data"),
)
def atualizar_opcoes_tags(trigger):
    tags = listar_tags()
    opcoes = [{"label": "Todas", "value": ""}]
    for t in tags:
        opcoes.append({"label": t["nome"], "value": str(t["id"])})
    return opcoes


@callback(
    Output("vagas-lista", "children"),
    Input("vagas-trigger", "data"),
    Input("filtro-status", "value"),
    Input("filtro-portal", "value"),
    Input("filtro-tag", "value"),
    Input("filtro-busca", "value"),
)
def render_lista_vagas(_trigger, status_filtro, portal_filtro, tag_filtro, busca):
    vagas = listar_vagas(
        status_filtro=status_filtro if status_filtro else None,
        portal_id=int(portal_filtro) if portal_filtro and portal_filtro != "" else None,
        tag_id=int(tag_filtro) if tag_filtro and tag_filtro != "" else None,
        busca=busca or "",
    )
    if not vagas:
        return dmc.Text("Nenhuma vaga encontrada.", c="dimmed")
    return [html.Div(_vaga_item(v)) for v in vagas]