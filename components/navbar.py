from dash import html, dcc
from styles import (
    COR_FUNDO, COR_SUPERFICIE, COR_BORDA, COR_TEXTO,
    COR_TEXTO_SEC, COR_PRIMARY, SIDEBAR_WIDTH,
)

NAV_ITENS = [
    ("/", "Dashboard", "📊"),
    ("/nova-vaga", "Nova Vaga", "➕"),
    ("/vagas", "Listar Vagas", "📋"),
    ("/portais", "Portais", "🌐"),
    ("/tags", "Tags", "🏷️"),
]


def sidebar() -> html.Div:
    links = []
    for href, label, icon in NAV_ITENS:
        links.append(
            dcc.Link(
                html.Div(
                    [
                        html.Span(icon, style={"marginRight": "12px", "fontSize": "1.1rem"}),
                        html.Span(label),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "padding": "12px 24px",
                        "borderRadius": "8px",
                        "color": COR_TEXTO,
                        "fontSize": "0.95rem",
                        "transition": "background 0.15s",
                        "margin": "2px 12px",
                    },
                ),
                href=href,
                style={"textDecoration": "none"},
            )
        )

    return html.Div(
        children=[
            html.Div(
                children=[
                    html.H3(
                        "Sistema Vagas",
                        style={
                            "color": COR_PRIMARY,
                            "margin": 0,
                            "fontSize": "1.25rem",
                            "fontWeight": 700,
                        },
                    ),
                    html.Hr(style={
                        "borderColor": COR_BORDA,
                        "margin": "16px 0",
                    }),
                ],
                style={"padding": "24px 24px 0"},
            ),
            html.Nav(
                children=links,
                style={"flex": 1},
            ),
            html.Div(
                children=[
                    html.Hr(style={"borderColor": COR_BORDA, "margin": 0}),
                    html.P(
                        "v1.0.0",
                        style={
                            "color": COR_TEXTO_SEC,
                            "fontSize": "0.75rem",
                            "textAlign": "center",
                            "padding": "12px",
                            "margin": 0,
                        },
                    ),
                ],
            ),
        ],
        style={
            "backgroundColor": COR_SUPERFICIE,
            "borderRight": f"1px solid {COR_BORDA}",
            "height": "100vh",
            "display": "flex",
            "flexDirection": "column",
            "position": "fixed",
            "width": f"{100 * SIDEBAR_WIDTH / 12}%",
        },
    )
