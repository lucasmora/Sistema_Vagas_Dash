import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

from components.navbar import sidebar
from database import init_db
from pages import dashboard, portais, tags, vagas, nova_vaga, detalhe_vaga, vagas, nova_vaga, detalhe_vaga
from styles import (
    COR_FUNDO, COR_TEXTO_SEC, SIDEBAR_WIDTH, CONTENT_PADDING,
)

init_db()

app = dash.Dash(
    __name__,
    title="Sistema de Vagas",
    update_title="",
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.DARKLY],
)

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="edit_mode", data=False),
        dcc.Store(id="editing_portal_id", data=None),
        dcc.Store(id="notification", data=None),
        sidebar(),
        html.Div(
            [
                html.Div(id="notification-output"),
                html.Div(id="page-content"),
            ],
            style={
                "marginLeft": f"{100 * SIDEBAR_WIDTH / 12}%",
                "padding": CONTENT_PADDING,
                "minHeight": "100vh",
                "backgroundColor": COR_FUNDO,
            },
        ),
    ]
)


def _pagina_placeholder(titulo: str, descricao: str = "") -> html.Div:
    return html.Div(
        [
            html.H2(titulo, style={"color": COR_TEXTO_SEC, "marginBottom": "12px"}),
            html.P(descricao or f"Página {titulo} — em construção",
                   style={"color": COR_TEXTO_SEC}),
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


@callback(
    Output("notification-output", "children"),
    Output("notification", "data", allow_duplicate=True),
    Input("notification", "data"),
    prevent_initial_call=True,
)
def show_notification(data):
    if data is None:
        raise dash.exceptions.PreventUpdate
    return dbc.Toast(
        data.get("message", ""),
        header={
            "success": "Sucesso",
            "danger": "Erro",
            "warning": "Atenção",
            "info": "Info",
        }.get(data.get("type", "info"), "Notificação"),
        is_open=True,
        duration=4000,
        dismissable=True,
        icon=data.get("type", "info"),
        style={
            "position": "fixed",
            "top": 20,
            "right": 20,
            "zIndex": 9999,
            "minWidth": "300px",
        },
    ), None


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
