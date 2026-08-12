from dash import html, dcc
import dash_mantine_components as dmc

from components.layout import metric_card
from components.charts import fig_pizza_status, fig_barras_curriculos, fig_barras_portais
from db.models import obter_metricas
from styles import COR_PRIMARY, COR_DESTAQUE, COR_ALERTA


def layout() -> html.Div:
    m = obter_metricas()

    return html.Div(
        children=[
            html.Div(
                children=[
                    dmc.Title("Dashboard", order=2, mb="xs"),
                    dmc.Text("Resumo das candidaturas", c="dimmed", size="sm"),
                ],
                style={"marginBottom": "24px"},
            ),
            dmc.Grid(
                gutter="md",
                children=[
                    dmc.GridCol(metric_card("Total", m["total"], COR_PRIMARY),
                                span=3),
                    dmc.GridCol(metric_card("Ativas", m["ativas"], COR_DESTAQUE),
                                span=3),
                    dmc.GridCol(metric_card("Em Entrevista", m["entrevista"],
                                            COR_ALERTA), span=3),
                    dmc.GridCol(metric_card("Currículos", m["curriculos"],
                                            COR_PRIMARY), span=3),
                ],
                mb="lg",
            ),
            dmc.Grid(
                gutter="md",
                children=[
                    dmc.GridCol(
                        dcc.Loading(
                            dcc.Graph(
                                id="graph-status",
                                figure=fig_pizza_status(),
                                config={"displayModeBar": False},
                            ),
                            type="circle",
                            color="var(--mantine-primary-color-filled)",
                        ),
                        span=6,
                    ),
                    dmc.GridCol(
                        dcc.Loading(
                            dcc.Graph(
                                id="graph-portais",
                                figure=fig_barras_portais(),
                                config={"displayModeBar": False},
                            ),
                            type="circle",
                            color="var(--mantine-color-violet-5)",
                        ),
                        span=6,
                    ),
                ],
                mb="lg",
            ),
            dmc.Grid(
                gutter="md",
                children=[
                    dmc.GridCol(
                        dcc.Loading(
                            dcc.Graph(
                                id="graph-curriculos",
                                figure=fig_barras_curriculos(),
                                config={"displayModeBar": False},
                            ),
                            type="circle",
                            color="var(--mantine-primary-color-filled)",
                        ),
                        span=12,
                    ),
                ],
            ),
        ],
    )