from dash import html, dcc
from styles import (
    COR_TEXTO, COR_TEXTO_SEC, COR_TEXTO_MUTED,
    COR_PRIMARY, CARD_STYLE, badge_style, tag_style,
)


def _formatar_salario(vaga: dict) -> str:
    s = vaga.get("salario")
    sm = vaga.get("salario_max")
    if s is None and sm is None:
        return "Salário não informado"
    if sm is None:
        return f"R$ {s:,.0f}".replace(",", ".")
    return f"R$ {s:,.0f} - R$ {sm:,.0f}".replace(",", ".")


def _estrelas(valor: int) -> str:
    return "★" * valor + "☆" * (5 - valor)


def vaga_card(vaga: dict, portal_nome: str = "") -> html.Div:
    nome = vaga.get("nome", "Sem nome")
    empresa = vaga.get("empresa") or "Confidencial"
    status = vaga.get("status", "Interessado")
    salario = _formatar_salario(vaga)
    modalidade = vaga.get("modalidade") or ""
    data_envio = vaga.get("data_envio")
    interesse = vaga.get("interesse") or 0
    aderencia = vaga.get("aderencia") or 0
    tags = vaga.get("_tags", [])
    vaga_id = vaga.get("id")

    info_parts = [salario]
    if modalidade:
        info_parts.append(modalidade)
    info_linha = " · ".join(info_parts)

    data_envio_texto = (
        f"📅 {data_envio}" if data_envio
        else "⏳ Currículo não enviado"
    )

    tag_pills = []
    for tag in tags:
        tag_pills.append(
            html.Span(tag if isinstance(tag, str) else tag.get("nome", ""),
                      style=tag_style())
        )

    return html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.H4(nome, style={
                                "color": COR_TEXTO, "margin": 0,
                                "fontSize": "1.125rem", "fontWeight": 600,
                            }),
                            html.P(empresa, style={
                                "color": COR_TEXTO_SEC, "margin": "4px 0 0 0",
                                "fontSize": "0.875rem",
                            }),
                        ],
                        style={"flex": 1},
                    ),
                    html.Span(status, style=badge_style(status)),
                ],
                style={"display": "flex",
                        "justifyContent": "space-between", "marginBottom": "16px"},
            ),
            html.Div(
                children=[
                    html.Span(info_linha, style={
                        "color": COR_TEXTO_MUTED, "fontSize": "0.8125rem",
                    }),
                ],
                style={"marginBottom": "8px"},
            ),
            html.Div(
                children=[
                    html.Span(portal_nome or "Sem portal", style={
                        "color": COR_TEXTO_MUTED, "fontSize": "0.8125rem",
                    }),
                ],
                style={"marginBottom": "8px"},
            ) if portal_nome else None,
            html.Div(
                children=[
                    html.Span(
                        f"Interesse: {_estrelas(interesse)}",
                        style={"color": COR_TEXTO_SEC, "fontSize": "0.8rem",
                               "marginRight": "16px"},
                    ),
                    html.Span(
                        f"Aderência: {_estrelas(aderencia)}",
                        style={"color": COR_TEXTO_SEC, "fontSize": "0.8rem"},
                    ),
                ],
                style={"marginBottom": "12px"},
            ),
            html.Div(
                children=tag_pills,
                style={"marginBottom": "12px"},
            ) if tag_pills else None,
            html.Div(
                children=[
                    html.Span(data_envio_texto, style={
                        "color": COR_TEXTO_MUTED, "fontSize": "0.8125rem",
                    }),
                ],
                style={"marginBottom": "16px"},
            ),
            html.Div(
                children=[
                    dcc.Link(
                        html.Span(
                            "Detalhes →",
                            style={
                                "color": COR_PRIMARY, "fontSize": "0.875rem",
                                "cursor": "pointer", "fontWeight": 500,
                            },
                        ),
                        href=f"/vagas/{vaga_id}",
                        style={"textDecoration": "none"},
                    ),
                ],
                style={"textAlign": "right"},
            ),
        ],
        style={
            **CARD_STYLE,
            "display": "flex",
            "flexDirection": "column",
        },
    )
