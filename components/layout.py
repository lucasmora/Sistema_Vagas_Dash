from dash import html
from styles import COR_TEXTO_SEC, COR_TEXTO_MUTED, COR_PRIMARY, CARD_STYLE


def metric_card(titulo: str, valor, cor: str = COR_PRIMARY) -> html.Div:
    return html.Div(
        children=[
            html.P(titulo, style={
                "color": COR_TEXTO_MUTED, "fontSize": "0.75rem",
                "margin": "0 0 6px 0", "textTransform": "uppercase",
                "letterSpacing": "0.5px", "fontWeight": 500,
            }),
            html.H2(
                str(valor),
                style={
                    "color": cor, "margin": 0, "fontSize": "2.25rem",
                    "fontWeight": 700,
                },
            ),
        ],
        style={
            **CARD_STYLE,
            "padding": "32px 32px",
        },
    )
