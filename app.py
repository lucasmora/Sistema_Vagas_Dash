import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

from components.navbar import sidebar
from database import init_db
from pages import dashboard, portais, tags, vagas, nova_vaga, detalhe_vaga, vagas, nova_vaga, detalhe_vaga
from styles import (
    COR_FUNDO, COR_TEXTO_SEC, COR_TEXTO, COR_SUPERFICIE, COR_ELEVADO,
    COR_BORDA, COR_BORDA_CLARA, COR_PRIMARY, SIDEBAR_WIDTH, CONTENT_PADDING,
)

init_db()

app = dash.Dash(
    __name__,
    title="Sistema de Vagas",
    update_title="",
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.DARKLY],
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
            :root {
                --font-sans: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
            }
            body {
                font-family: var(--font-sans);
                background-color: #0F0F23 !important;
                color: #EAEAFA;
            }
            .form-control {
                font-family: var(--font-sans);
                background-color: #24244A !important;
                border-color: #40406A !important;
                color: #EAEAFA !important;
            }
            .form-control:focus {
                border-color: #00ADB5 !important;
                box-shadow: 0 0 0 3px rgba(0, 173, 181, 0.25) !important;
            }
            .form-control::placeholder {
                color: #7A7A9A !important;
            }
            code, pre, kbd, samp { font-family: var(--font-mono); }
            /* Select / Dropdown dark overrides */
            .Select-control {
                background-color: #24244A !important;
                border-color: #40406A !important;
                color: #EAEAFA !important;
            }
            .Select-menu-outer {
                background-color: #1A1A34 !important;
                border-color: #40406A !important;
            }
            .Select-option {
                background-color: #1A1A34 !important;
                color: #A8A8C8 !important;
            }
            .Select-option.is-focused {
                background-color: #24244A !important;
                color: #EAEAFA !important;
            }
            .Select-option.is-selected {
                background-color: #00ADB5 !important;
                color: #FFF !important;
            }
            .Select-value-label {
                color: #EAEAFA !important;
            }
            .Select-placeholder {
                color: #7A7A9A !important;
            }
            .Select--multi .Select-value {
                background-color: #7C6FFF28 !important;
                border-color: #7C6FFF50 !important;
                color: #7C6FFF !important;
            }
            .Select--multi .Select-value-icon {
                border-color: #7C6FFF50 !important;
                color: #7C6FFF !important;
            }
            .Select--multi .Select-value-label {
                color: #7C6FFF !important;
            }
            /* DatePickerSingle dark overrides */
            .DateInput, .DateInput_input {
                background-color: #24244A !important;
                border-color: #40406A !important;
                color: #EAEAFA !important;
                font-family: var(--font-sans) !important;
            }
            .DateInput_input__focused {
                border-color: #00ADB5 !important;
            }
            .CalendarMonth, .CalendarMonthGrid {
                background-color: #1A1A34 !important;
            }
            .DayPicker {
                background-color: #1A1A34 !important;
            }
            .CalendarMonth_caption {
                color: #EAEAFA !important;
            }
            .DayPicker_weekHeader {
                color: #A8A8C8 !important;
            }
            .DayPickerNavigation_button {
                background-color: #24244A !important;
                border-color: #40406A !important;
            }
            .CalendarDay__default {
                background-color: #24244A !important;
                border-color: #40406A !important;
                color: #EAEAFA !important;
            }
            .CalendarDay__default:hover {
                background-color: #00ADB5 !important;
                color: #FFF !important;
            }
            .CalendarDay__selected {
                background-color: #00ADB5 !important;
                border-color: #00ADB5 !important;
                color: #FFF !important;
            }
            .CalendarDay__selected:hover {
                background-color: #00ADB5 !important;
                color: #FFF !important;
            }
            .CalendarDay__outside {
                background-color: transparent !important;
            }
            .SingleDatePickerInput__withBorder {
                border-color: #40406A !important;
            }
            /* rc-slider (Slider component) dark */
            .rc-slider-track {
                background-color: #00ADB5 !important;
            }
            .rc-slider-handle {
                border-color: #00ADB5 !important;
                background-color: #EAEAFA !important;
            }
            .rc-slider-rail {
                background-color: #40406A !important;
            }
            .rc-slider-mark-text {
                color: #7A7A9A !important;
            }
            .rc-slider-dot {
                border-color: #40406A !important;
                background-color: #24244A !important;
            }
            .rc-slider-dot-active {
                border-color: #00ADB5 !important;
            }
            /* Toast overrides */
            .toast {
                background-color: #1A1A34 !important;
                border-color: #40406A !important;
                color: #EAEAFA !important;
            }
            .toast-header {
                background-color: #24244A !important;
                border-color: #40406A !important;
                color: #EAEAFA !important;
            }
            /* Links inside text */
            a { color: #00ADB5 !important; }
            a:hover { color: #33C5CB !important; }
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
