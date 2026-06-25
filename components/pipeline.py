from dash import html
from styles import (
    COR_BORDA, COR_TEXTO, COR_TEXTO_SEC, COR_DESTAQUE, COR_PRIMARY,
    PIPELINE_ORDEM, STATUS_CORES, pipeline_step_style, pipeline_connector_style,
    badge_style,
)


def pipeline_view(status_atual: str) -> html.Div:
    if status_atual == "Rejeitado":
        idx_atual = -1
    else:
        try:
            idx_atual = PIPELINE_ORDEM.index(status_atual)
        except ValueError:
            idx_atual = -1

    steps = []
    for i, nome_status in enumerate(PIPELINE_ORDEM):
        ativo = i <= idx_atual
        cor = STATUS_CORES.get(nome_status, COR_BORDA)

        steps.append(
            html.Div(
                children=[
                    html.Div(
                        str(i + 1),
                        style=pipeline_step_style(ativo, cor),
                    ),
                    html.Span(
                        nome_status,
                        style={
                            "color": COR_TEXTO if ativo else COR_TEXTO_SEC,
                            "fontSize": "0.7rem",
                            "textAlign": "center",
                            "marginTop": "6px",
                            "maxWidth": "80px",
                            "lineHeight": 1.2,
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "center",
                },
            )
        )

        if i < len(PIPELINE_ORDEM) - 1:
            prox_ativo = i + 1 <= idx_atual
            steps.append(
                html.Div(style=pipeline_connector_style(prox_ativo))
            )

    rejeitado_ativo = status_atual == "Rejeitado"

    return html.Div(
        children=[
            html.Div(
                children=[
                    *steps,
                    html.Div(style=pipeline_connector_style(rejeitado_ativo)),
                    html.Div(
                        children=[
                            html.Div(
                                "R",
                                style=pipeline_step_style(
                                    rejeitado_ativo, STATUS_CORES["Rejeitado"]
                                ),
                            ),
                            html.Span(
                                "Rejeitado",
                                style={
                                    "color": (
                                        COR_TEXTO if rejeitado_ativo
                                        else COR_TEXTO_SEC
                                    ),
                                    "fontSize": "0.7rem",
                                    "textAlign": "center",
                                    "marginTop": "6px",
                                    "maxWidth": "80px",
                                    "lineHeight": 1.2,
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "alignItems": "center",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "padding": "12px 0",
                },
            ),
            html.Div(
                children=[
                    html.Span("Status atual: ", style={
                        "color": COR_TEXTO_SEC, "fontSize": "0.85rem",
                    }),
                    html.Span(status_atual, style=badge_style(status_atual)),
                ],
                style={
                    "textAlign": "center",
                    "marginTop": "8px",
                },
            ),
        ],
        style={
            "backgroundColor": COR_BORDA,
            "borderRadius": "12px",
            "padding": "20px 24px",
        },
    )
