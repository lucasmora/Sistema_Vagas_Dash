from dash import html
import dash_mantine_components as dmc

from styles import COR_PRIMARY

NAV_ITENS = [
    ("/", "Dashboard", "📊"),
    ("/nova-vaga", "Nova Vaga", "➕"),
    ("/vagas", "Listar Vagas", "📋"),
    ("/portais", "Portais", "🌐"),
    ("/tags", "Tags", "🏷️"),
]


def sidebar():
    links = [
        dmc.NavLink(
            label=label,
            href=href,
            leftSection=html.Span(icon, style={"fontSize": "1.1rem"}),
            active="exact",
        )
        for href, label, icon in NAV_ITENS
    ]

    return dmc.AppShellNavbar(
        p="md",
        children=[
            dmc.Stack(
                gap="xs",
                children=[
                    dmc.Title("Sistema Vagas", order=3, c=COR_PRIMARY),
                    dmc.Divider(),
                ],
                mb="md",
            ),
            dmc.ScrollArea(
                children=dmc.Stack(gap=4, children=links),
                style={"flex": 1},
            ),
            dmc.Box(
                children=[
                    dmc.Divider(),
                    dmc.Text(
                        "v1.0.0",
                        c="dimmed",
                        size="xs",
                        ta="center",
                        py="sm",
                    ),
                ],
            ),
        ],
    )
