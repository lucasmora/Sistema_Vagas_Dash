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
                --bg: #060B17;
                --surface: #101728;
                --surface-raised: #17233C;
                --border: #2D4470;
                --text: #F5F7FF;
                --text-secondary: #D6E0F2;
                --text-muted: #99A8C2;
                --primary: #2ED3C8;
                --accent: #8B7CFF;
                --success: #2FCB70;
                --warning: #F5A524;
                --danger: #FF5F6D;
                --Dash-Text-Strong: var(--text);
                --Dash-Text-Medium: var(--text-secondary);
                --Dash-Text-Weak: var(--text-muted);
            }
            body {
                font-family: var(--font-sans);
                background-color: var(--bg) !important;
                color: var(--text);
            }
            .form-control {
                font-family: var(--font-sans);
                background-color: var(--surface-raised) !important;
                border-color: var(--border) !important;
                color: var(--text) !important;
                width: 100% !important;
                box-sizing: border-box;
            }
            .form-control:focus {
                border-color: var(--primary) !important;
                box-shadow: 0 0 0 3px rgba(46, 211, 200, 0.28) !important;
            }
            .form-control::placeholder {
                color: var(--text-muted) !important;
            }
            .dash-input-container > input.dash-input-element {
                width: 100% !important;
                display: block !important;
                box-sizing: border-box !important;
            }
            /* Força DatePickerSingle (Dash 3.x) a ocupar 100% da largura */
            .dash-datepicker {
                width: 100% !important;
            }
            .dash-datepicker-input-wrapper {
                width: 100% !important;
                display: block !important;
            }
            .dash-datepicker-input-wrapper > div {
                width: 100% !important;
            }
            .dash-datepicker-input-wrapper input.dash-datepicker-input {
                width: 100% !important;
            }
            /* Força Dropdown (dcc.Dropdown) a ocupar 100% */
            .Select,
            .Select-control {
                width: 100% !important;
            }
            code, pre, kbd, samp { font-family: var(--font-mono); }
            /* Select / Dropdown dark overrides */
            .Select-control {
                background-color: var(--surface-raised) !important;
                border-color: var(--border) !important;
                color: var(--text) !important;
            }
            .Select-menu-outer {
                background-color: var(--surface) !important;
                border-color: var(--border) !important;
            }
            .Select-option {
                background-color: var(--surface) !important;
                color: var(--text-secondary) !important;
            }
            .Select-option.is-focused {
                background-color: var(--surface-raised) !important;
                color: var(--text) !important;
            }
            .Select-option.is-selected {
                background-color: var(--primary) !important;
                color: #FFF !important;
            }
            .Select-value-label {
                color: var(--text) !important;
            }
            .Select-placeholder {
                color: var(--text-muted) !important;
            }
            .Select--multi .Select-value {
                background-color: #8B7CFF28 !important;
                border-color: #8B7CFF50 !important;
                color: var(--accent) !important;
            }
            .Select--multi .Select-value-icon {
                border-color: #8B7CFF50 !important;
                color: var(--accent) !important;
            }
            .Select--multi .Select-value-label {
                color: var(--accent) !important;
            }
            /* DatePickerSingle dark overrides */
            .DateInput, .DateInput_input {
                background-color: var(--surface-raised) !important;
                border-color: var(--border) !important;
                color: var(--text) !important;
                font-family: var(--font-sans) !important;
            }
            .DateInput_input__focused {
                border-color: var(--primary) !important;
            }
            .CalendarMonth, .CalendarMonthGrid {
                background-color: var(--surface) !important;
            }
            .DayPicker {
                background-color: var(--surface) !important;
            }
            .CalendarMonth_caption {
                color: var(--text) !important;
            }
            .DayPicker_weekHeader {
                color: var(--text-secondary) !important;
            }
            .DayPickerNavigation_button {
                background-color: var(--surface-raised) !important;
                border-color: var(--border) !important;
            }
            .CalendarDay__default {
                background-color: var(--surface-raised) !important;
                border-color: var(--border) !important;
                color: var(--text) !important;
            }
            .CalendarDay__default:hover {
                background-color: var(--primary) !important;
                color: #FFF !important;
            }
            .CalendarDay__selected {
                background-color: var(--primary) !important;
                border-color: var(--primary) !important;
                color: #FFF !important;
            }
            .CalendarDay__selected:hover {
                background-color: var(--primary) !important;
                color: #FFF !important;
            }
            .CalendarDay__outside {
                background-color: transparent !important;
            }
            .SingleDatePickerInput__withBorder {
                border-color: var(--border) !important;
            }
            /* rc-slider (Slider component) dark */
            .rc-slider-track {
                background-color: var(--primary) !important;
            }
            .rc-slider-handle {
                border-color: var(--primary) !important;
                background-color: var(--text) !important;
            }
            .rc-slider-rail {
                background-color: var(--border) !important;
            }
            .rc-slider-mark-text {
                color: var(--text-muted) !important;
            }
            .rc-slider-dot {
                border-color: var(--border) !important;
                background-color: var(--surface-raised) !important;
            }
            .rc-slider-dot-active {
                border-color: var(--primary) !important;
            }
            /* Toast overrides */
            .toast {
                background-color: var(--surface) !important;
                border-color: var(--border) !important;
                color: var(--text) !important;
            }
            .toast-header {
                background-color: var(--surface-raised) !important;
                border-color: var(--border) !important;
                color: var(--text) !important;
            }
            /* Links inside text */
            a { color: var(--primary) !important; }
            a:hover { color: #6FE8E0 !important; }
            /* Dash checklist / radio labels */
            .dash-checkbox-option, .dash-radio-option {
                background-color: transparent !important;
            }
            label, .form-check-label, .dash-label {
                color: var(--text) !important;
                background-color: transparent !important;
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
