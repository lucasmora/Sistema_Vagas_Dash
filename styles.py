# Design system adaptado ao Dash Mantine Components (dark)

# Tokens de cor mapeados para as CSS variables do Mantine dark theme
COR_FUNDO = "var(--mantine-color-body)"
COR_SUPERFICIE = "var(--mantine-color-dark-6)"
COR_ELEVADO = "var(--mantine-color-dark-5)"
COR_BORDA_CLARA = "var(--mantine-color-dark-4)"
COR_BORDA = "var(--mantine-color-dark-3)"
COR_TEXTO = "var(--mantine-color-text)"
COR_TEXTO_SEC = "var(--mantine-color-dimmed)"
COR_TEXTO_MUTED = "var(--mantine-color-dimmed)"
COR_PRIMARY = "var(--mantine-primary-color-filled)"
COR_DESTAQUE = "var(--mantine-color-violet-5)"
COR_SUCESSO = "var(--mantine-color-teal-5)"
COR_ALERTA = "var(--mantine-color-yellow-6)"
COR_PERIGO = "var(--mantine-color-red-6)"

STATUS_CORES = {
    "Interessado": "#A7A9CD",
    "Currículo Enviado": "#2ED3C8",
    "Entrevista Agendada": "#F5A524",
    "Em Processo": "#8B7CFF",
    "Oferta": "#2FCB70",
    "Aceito": "#2ED3C8",
    "Rejeitado": "#FF5F6D",
}

PIPELINE_ORDEM = [
    "Interessado",
    "Currículo Enviado",
    "Entrevista Agendada",
    "Em Processo",
    "Oferta",
    "Aceito",
]

SOMBRA_NIVEL_1 = "var(--mantine-shadow-sm)"

# Espaçamento Airy
ESP_XS = "4px"
ESP_SM = "8px"
ESP_MD = "16px"
ESP_LG = "24px"
ESP_XL = "32px"

INPUT_PADDING_Y = "10px"
INPUT_PADDING_X = "14px"

RAIO_BORDA = "var(--mantine-radius-md)"
RAIO_BORDA_PILL = "9999px"

CARD_STYLE = {
    "backgroundColor": COR_SUPERFICIE,
    "border": f"1px solid {COR_BORDA_CLARA}",
    "borderRadius": RAIO_BORDA,
    "boxShadow": SOMBRA_NIVEL_1,
    "padding": f"{ESP_LG} {ESP_XL}",
}

INPUT_STYLE = {
    "backgroundColor": COR_ELEVADO,
    "border": f"1px solid {COR_BORDA}",
    "borderRadius": RAIO_BORDA,
    "color": COR_TEXTO,
    "padding": f"{INPUT_PADDING_Y} {INPUT_PADDING_X}",
    "fontSize": "0.875rem",
    "height": "auto",
    "width": "100%",
    "transition": "border-color 0.15s ease, box-shadow 0.15s ease",
}

SELECT_STYLE = {
    **INPUT_STYLE,
    "appearance": "auto",
}

SIDEBAR_WIDTH = 260
CONTENT_PADDING = "32px 40px"


def badge_style(status: str) -> dict:
    cor = STATUS_CORES.get(status, COR_BORDA)
    return {
        "backgroundColor": f"{cor}1A",
        "border": f"1px solid {cor}40",
        "color": cor,
        "padding": f"{ESP_XS} {ESP_MD}",
        "borderRadius": RAIO_BORDA_PILL,
        "fontSize": "0.8125rem",
        "fontWeight": 500,
        "display": "inline-flex",
        "alignItems": "center",
    }


def tag_style() -> dict:
    return {
        "backgroundColor": f"{COR_DESTAQUE}18",
        "color": COR_DESTAQUE,
        "padding": f"{ESP_XS} {ESP_SM}",
        "borderRadius": RAIO_BORDA_PILL,
        "fontSize": "0.75rem",
        "fontWeight": 500,
        "marginRight": "6px",
        "marginBottom": "4px",
        "display": "inline-block",
        "border": f"1px solid {COR_DESTAQUE}30",
    }


def pipeline_step_style(ativo: bool, cor: str) -> dict:
    return {
        "width": "36px",
        "height": "36px",
        "borderRadius": "50%",
        "border": f"2px solid {cor if ativo else COR_BORDA_CLARA}",
        "backgroundColor": cor if ativo else "transparent",
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "center",
        "color": "#FFFFFF" if ativo else COR_TEXTO_MUTED,
        "fontWeight": 600,
        "fontSize": "0.85rem",
        "zIndex": 2,
        "transition": "all 0.2s ease",
    }


def pipeline_connector_style(ativo: bool) -> dict:
    return {
        "flex": 1,
        "height": "2px",
        "backgroundColor": COR_BORDA_CLARA if not ativo else STATUS_CORES.get("Aceito", COR_PRIMARY),
        "marginTop": "17px",
        "transition": "background-color 0.3s ease",
    }


COLUNA_ESTILO = {
    "marginBottom": "20px",
    "width": "100%",
}
