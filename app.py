import dash
from dash import html, dcc, callback, Input, Output
import dash_mantine_components as dmc

from components.navbar import sidebar
from db.database import init_db
from pages import dashboard, portais, tags, vagas, nova_vaga, detalhe_vaga
from styles import COR_TEXTO_SEC, SIDEBAR_WIDTH as SIDEBAR_WIDTH_PX

init_db()

THEME = {
    "primaryColor": "teal",
    "fontFamily": "'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "fontFamilyMonospace": "'JetBrains Mono', 'Fira Code', monospace",
}

app = dash.Dash(
    __name__,
    title="Sistema de Vagas",
    update_title="",
    suppress_callback_exceptions=True,
    index_string="""
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
        <style>
            html, body {
                font-family: var(--mantine-font-family);
                background-color: var(--mantine-color-body);
                color: var(--mantine-color-text);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
""",
)

app.layout = dmc.MantineProvider(
    theme=THEME,
    forceColorScheme="dark",
    children=[
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="editing_portal_id", data=None),
        dcc.Store(id="notification", data=None),
        dmc.NotificationContainer(id="notification-container", position="top-right"),
        dmc.AppShell(
            children=[
                sidebar(),
                dmc.AppShellMain(
                    html.Div(id="page-content"),
                ),
            ],
            navbar={"width": SIDEBAR_WIDTH_PX, "breakpoint": "sm", "collapsed": {"mobile": True}},
            padding="xl",
            withBorder=True,
        ),
    ],
)


def _pagina_placeholder(titulo: str, descricao: str = "") -> html.Div:
    return html.Div(
        [
            html.H2(titulo, style={"color": COR_TEXTO_SEC, "marginBottom": "12px"}),
            html.P(descricao, style={"color": COR_TEXTO_SEC}),
        ]
    )


@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname: str):
    if not pathname:
        pathname = "/"

    pathname = pathname.rstrip("/")

    if pathname in ("", "/dashboard"):
        return dashboard.layout()
    if pathname == "/nova-vaga":
        return nova_vaga.layout()
    if pathname == "/vagas":
        return vagas.layout()
    if pathname.startswith("/vagas/"):
        return detalhe_vaga.layout()
    if pathname == "/portais":
        return portais.layout()
    if pathname == "/tags":
        return tags.layout()
    return _pagina_placeholder("404", "Página não encontrada")


NOTIFICACAO_TITULOS = {
    "success": "Sucesso",
    "danger": "Erro",
    "warning": "Atenção",
    "info": "Info",
}

NOTIFICACAO_CORES = {
    "success": "green",
    "danger": "red",
    "warning": "yellow",
    "info": "blue",
}


@callback(
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Output("notification", "data", allow_duplicate=True),
    Input("notification", "data"),
    prevent_initial_call=True,
)
def show_notification(data):
    if data is None:
        raise dash.exceptions.PreventUpdate
    tipo = data.get("type", "info")
    return (
        [
            {
                "action": "show",
                "title": NOTIFICACAO_TITULOS.get(tipo, "Notificação"),
                "message": data.get("message", ""),
                "color": NOTIFICACAO_CORES.get(tipo, "blue"),
                "autoClose": 4000,
                "withCloseButton": True,
            }
        ],
        None,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
