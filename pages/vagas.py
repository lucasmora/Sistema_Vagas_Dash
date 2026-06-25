import dash
from dash import html, dcc, callback, Input, Output, State, ALL, callback_context, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from models import listar_vagas, atualizar_vaga, get_vaga, listar_tags
from components.cards import vaga_card
from styles import (
    COR_TEXTO, COR_TEXTO_SEC, COR_BORDA, COR_PRIMARY,
    COR_SUPERFICIE, CARD_STYLE, 
)


def _vaga_item(vaga: dict) -> html.Div:
    portal_nome = "Sem portal"
    if vaga.get("portal_id"):
        try:
            from models import get_portal
            portal = get_portal(vaga["portal_id"])
            if portal:
                portal_nome = portal["nome"]
        except:
            pass
    return vaga_card(vaga, portal_nome)


def layout() -> html.Div:
    return html.Div([
        dcc.Store(id="vagas-trigger", data=0),
        html.H2("Vagas", style={
            "color": COR_TEXTO, "fontWeight": 600, "marginBottom": "24px",
        }),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Filtros", style={
                        "color": COR_TEXTO, "marginBottom": "16px", "fontWeight": 600,
                    }),
                    html.Div([
                        html.Label("Status", style={
                            "color": COR_TEXTO_SEC, "fontSize": "0.85rem", "marginBottom": "4px",
                        }),
                        dcc.Checklist(
                            id="filtro-status",
                            options=[
                                {"label": s, "value": s}
                                for s in ["Interessado", "Currículo Enviado", "Entrevista Agendada",
                                         "Em Processo", "Oferta", "Aceito", "Rejeitado"]
                            ],
                            value=[],
                            style={
                                "backgroundColor": COR_SUPERFICIE,
                                "border": f"1px solid {COR_BORDA}",
                                "borderRadius": "8px",
                                "padding": "10px",
                            },
                        ),
                        html.Br(),
                        html.Br(),
                        html.Label("Portal", style={
                            "color": COR_TEXTO_SEC, "fontSize": "0.85rem", "marginBottom": "4px",
                        }),
                        dcc.Dropdown(
                            id="filtro-portal",
                            options=[{"label": "Todos", "value": ""}],
                            value="",
                            style={
                                "backgroundColor": COR_SUPERFICIE,
                                "border": f"1px solid {COR_BORDA}",
                                "borderRadius": "8px",
                            },
                        ),
                        html.Br(),
                        html.Br(),
                        html.Label("Tag", style={
                            "color": COR_TEXTO_SEC, "fontSize": "0.85rem", "marginBottom": "4px",
                        }),
                        dcc.Dropdown(
                            id="filtro-tag",
                            options=[{"label": "Todas", "value": ""}],
                            value="",
                            style={
                                "backgroundColor": COR_SUPERFICIE,
                                "border": f"1px solid {COR_BORDA}",
                                "borderRadius": "8px",
                            },
                        ),
                        html.Br(),
                        html.Br(),
                        html.Label("Busca", style={
                            "color": COR_TEXTO_SEC, "fontSize": "0.85rem", "marginBottom": "4px",
                        }),
                        dcc.Input(
                            id="filtro-busca",
                            placeholder="Busca por nome, empresa...",
                            type="text",
                            style={
                                "width": "100%",
                                "backgroundColor": COR_SUPERFICIE,
                                "border": f"1px solid {COR_BORDA}",
                                "borderRadius": "8px",
                                "padding": "8px 12px",
                                "color": COR_TEXTO,
                            },
                        ),
                    ]),
                ], style={**CARD_STYLE, "padding": "20px"}),
            ], width=3),
            dbc.Col(html.Div(id="vagas-lista"), width=9),
        ], className="g-4"),
    ])


@callback(
    Output("filtro-portal", "options"),
    Input("vagas-trigger", "data"),
)
def atualizar_opcoes_portais(trigger):
    from models import listar_portais
    portais = listar_portais()
    opcoes = [{"label": "Todos", "value": ""}]
    for p in portais:
        opcoes.append({"label": p["nome"], "value": str(p["id"])})
    return opcoes


@callback(
    Output("filtro-tag", "options"),
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
    State("filtro-status", "value"),
    State("filtro-portal", "value"),
    State("filtro-tag", "value"),
    State("filtro-busca", "value"),
)
def render_lista_vagas(_trigger, status_filtro, portal_filtro, tag_filtro, busca):
    vagas = listar_vagas(
        status_filtro=status_filtro if status_filtro else None,
        portal_id=int(portal_filtro) if portal_filtro and portal_filtro != "" else None,
        tag_id=int(tag_filtro) if tag_filtro and tag_filtro != "" else None,
        busca=busca or "",
    )
    if not vagas:
        return html.P(
            "Nenhuma vaga encontrada.",
            style={"color": COR_TEXTO_SEC},
        )
    return [_vaga_item(v) for v in vagas]


@callback(
    Output("vagas-trigger", "data", allow_duplicate=True),
    Output("notification", "data", allow_duplicate=True),
    Input({"type": "btn-excluir-vaga", "index": ALL}, "n_clicks"),
    State("vagas-trigger", "data"),
    prevent_initial_call=True,
)
def excluir_vaga_callback(n_clicks_list, trigger):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    vaga_id = ctx.triggered_id["index"]
    try:
        from models import excluir_vaga
        excluir_vaga(vaga_id)
        return trigger + 1, {"message": "Vaga excluída!", "type": "success"}
    except Exception as e:
        return trigger + 1, {"message": f"Erro ao excluir vaga: {str(e)}", "type": "danger"}