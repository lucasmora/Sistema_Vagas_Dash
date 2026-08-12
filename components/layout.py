import dash_mantine_components as dmc
from styles import COR_PRIMARY


def metric_card(titulo: str, valor, cor: str = COR_PRIMARY):
    return dmc.Paper(
        p="lg",
        radius="md",
        shadow="sm",
        withBorder=True,
        children=[
            dmc.Text(
                titulo,
                size="xs",
                tt="uppercase",
                c="dimmed",
                fw=500,
            ),
            dmc.Title(str(valor), order=2, c=cor),
        ],
    )
