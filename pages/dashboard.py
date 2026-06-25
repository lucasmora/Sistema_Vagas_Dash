from dash import html, dcc
import dash_bootstrap_components as dbc

from components.layout import metric_card
from components.charts import fig_pizza_status, fig_barras_curriculos, fig_barras_portais
from models import obter_metricas
from styles import COR_TEXTO, COR_TEXTO_SEC


def layout() -> html.Div:
    m = obter_metricas()

    return html.Div(
        children=[
            html.Div(
                children=[
                    html.H2("Dashboard", style={
                        "color": COR_TEXTO, "fontWeight": 600, "margin": 0,
                    }),
                    html.P("Resumo das candidaturas",
                           style={"color": COR_TEXTO_SEC, "margin": "4px 0 0 0"}),
                ],
                style={"marginBottom": "24px"},
            ),
            dbc.Row(
                children=[
                    dbc.Col(metric_card("Total", m["total"], "#00BFA6"),
                            width=3),
                    dbc.Col(metric_card("Ativas", m["ativas"], "#6C63FF"),
                            width=3),
                    dbc.Col(metric_card("Em Entrevista", m["entrevista"],
                                        "#FFC107"), width=3),
                    dbc.Col(metric_card("Currículos", m["curriculos"],
                                        "#0DCAF0"), width=3),
                ],
                className="g-3",
                style={"marginBottom": "24px"},
            ),
            dbc.Row(
                children=[
                    dbc.Col(
                        dcc.Loading(
                            dcc.Graph(
                                id="graph-status",
                                figure=fig_pizza_status(),
                                config={"displayModeBar": False},
                            ),
                            type="circle",
                            color="#00BFA6",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dcc.Loading(
                            dcc.Graph(
                                id="graph-portais",
                                figure=fig_barras_portais(),
                                config={"displayModeBar": False},
                            ),
                            type="circle",
                            color="#6C63FF",
                        ),
                        width=6,
                    ),
                ],
                className="g-3",
                style={"marginBottom": "24px"},
            ),
            dbc.Row(
                children=[
                    dbc.Col(
                        dcc.Loading(
                            dcc.Graph(
                                id="graph-curriculos",
                                figure=fig_barras_curriculos(),
                                config={"displayModeBar": False},
                            ),
                            type="circle",
                            color="#00BFA6",
                        ),
                        width=12,
                    ),
                ],
                className="g-3",
            ),
        ],
    )
