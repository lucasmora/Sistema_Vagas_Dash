from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

from models import listar_vagas, listar_tags
from components.cards import vaga_card
from styles import (
    COR_TEXTO, COR_TEXTO_SEC, COR_BORDA_CLARA,
    COR_PRIMARY, COR_SUPERFICIE, CARD_STYLE, INPUT_STYLE
)


def _vaga_item(vaga: dict) -> html.Div:
    return vaga_card(vaga, vaga.get("portal_nome") or "Sem portal")


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
                        "color": COR_TEXTO, "marginBottom": "20px", "fontWeight": 600,
                    }),
                    html.Div([
                        html.Label("Status", style={
                            "color": COR_TEXTO_SEC, "fontSize": "0.8125rem",
                            "marginBottom": "6px", "fontWeight": 500,
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
                                "border": f"1px solid {COR_BORDA_CLARA}",
                                "borderRadius": "8px",
                                "padding": "12px",
                                "color": COR_TEXTO,
                                "fontSize": "0.875rem",
                            },
                            inputStyle={"marginRight": "8px", "accentColor": COR_PRIMARY},
                            labelStyle={"marginBottom": "6px", "display": "block"},
                        ),
                        html.Hr(style={
                            "borderColor": COR_BORDA_CLARA, "margin": "20px 0",
                            "opacity": 0.5,
                        }),
                        html.Label("Portal", style={
                            "color": COR_TEXTO_SEC, "fontSize": "0.8125rem",
                            "marginBottom": "6px", "fontWeight": 500,
                        }),
                        dbc.Select(
                            id="filtro-portal",
                            options=[{"label": "Todos", "value": ""}],
                            value="",
                        ),
                        html.Hr(style={
                            "borderColor": COR_BORDA_CLARA, "margin": "20px 0",
                            "opacity": 0.5,
                        }),
                        html.Label("Tag", style={
                            "color": COR_TEXTO_SEC, "fontSize": "0.8125rem",
                            "marginBottom": "6px", "fontWeight": 500,
                        }),
                        dbc.Select(
                            id="filtro-tag",
                            options=[{"label": "Todas", "value": ""}],
                            value="",
                        ),
                        html.Hr(style={
                            "borderColor": COR_BORDA_CLARA, "margin": "20px 0",
                            "opacity": 0.5,
                        }),
                        html.Label("Busca", style={
                            "color": COR_TEXTO_SEC, "fontSize": "0.8125rem",
                            "marginBottom": "6px", "fontWeight": 500,
                        }),
                        dcc.Input(
                            id="filtro-busca",
                            placeholder="Busca por nome, empresa...",
                            type="text",
                            style={**INPUT_STYLE, "width": "100%"},
                        ),
                    ]),
                ], style={**CARD_STYLE}),
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
    return [html.Div(_vaga_item(v), style={"marginBottom": "20px"}) for v in vagas]