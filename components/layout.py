from dash import html
from styles import COR_SUPERFICIE, COR_BORDA, COR_TEXTO, COR_TEXTO_SEC

def metric_card(titulo: str, valor, cor: str = "#00BFA6") -> html.Div:
    return html.Div(
        children=[
            html.P(titulo, style={
                "color": COR_TEXTO_SEC, "fontSize": "0.85rem",
                "margin": "0 0 4px 0", "textTransform": "uppercase",
                "letterSpacing": "0.5px",
            }),
            html.H2(
                str(valor),
                style={
                    "color": cor, "margin": 0, "fontSize": "2rem",
                    "fontWeight": 700,
                },
            ),
        ],
        style={
            "backgroundColor": COR_SUPERFICIE,
            "border": f"1px solid {COR_BORDA}",
            "borderRadius": "12px",
            "padding": "24px 32px",
        },
    )
