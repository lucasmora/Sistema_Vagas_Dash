import dash_mantine_components as dmc
from dash import dcc

from styles import STATUS_CORES, COR_BORDA


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


def vaga_card(vaga: dict, portal_nome: str = ""):
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
            dmc.Badge(
                tag if isinstance(tag, str) else tag.get("nome", ""),
                variant="light",
                color=COR_BORDA,
                size="sm",
                radius="xl",
            )
        )

    return dmc.Paper(
        p="lg",
        radius="md",
        shadow="sm",
        withBorder=True,
        mb="md",
        style={"display": "flex", "flexDirection": "column"},
        children=[
            dmc.Group(
                justify="space-between",
                align="start",
                wrap="nowrap",
                gap="md",
                children=[
                    dmc.Stack(gap=0, children=[
                        dmc.Text(nome, fw=600, size="lg"),
                        dmc.Text(empresa, size="sm", c="dimmed"),
                    ]),
                    dmc.Badge(
                        status,
                        color=STATUS_CORES.get(status, COR_BORDA),
                        variant="light",
                        radius="xl",
                        style={"padding": "18px"},
                    ),
                ],
                mb="sm",
            ),
            dmc.Text(info_linha, size="sm", c="dimmed", mb="xs"),
            dmc.Text(
                portal_nome or "Sem portal",
                size="sm",
                c="dimmed",
                mb="xs",
            ) if portal_nome else None,
            dmc.Text(
                f"Interesse: {_estrelas(interesse)}   ·   Aderência: {_estrelas(aderencia)}",
                size="sm",
                c="dimmed",
                mb="xs",
            ),
            dmc.Group(
                children=tag_pills,
                gap=6,
                mb="xs",
            ) if tag_pills else None,
            dmc.Text(data_envio_texto, size="sm", c="dimmed", mb="md"),
            dmc.Group(
                justify="flex-end",
                children=[
                    dcc.Link(
                        dmc.Badge(
                            "Detalhes →",
                            color="teal",
                            variant="outline",
                            radius="xl",
                            size="md",
                            style={"cursor": "pointer", "padding": "12px"},
                        ),
                        href=f"/vagas/{vaga_id}",
                        style={"textDecoration": "none"},
                    ),
                ],
            ),
        ],
    )
