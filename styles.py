# Paleta Dark Mode (WCAG AA-friendly)

COR_FUNDO = "#060B17"        # Background principal (navy profundo)
COR_SUPERFICIE = "#101728"   # Superfícies (cards, sidebar)
COR_ELEVADO = "#17233C"      # Elevado (hover, pipeline bg, dropdowns)
COR_BORDA_CLARA = "#22324D"  # Bordas sutis
COR_BORDA = "#2D4470"        # Bordas fortes (inputs)
COR_TEXTO = "#F5F7FF"        # Texto primário (alto contraste)
COR_TEXTO_SEC = "#D6E0F2"    # Texto secundário
COR_TEXTO_MUTED = "#99A8C2"  # Texto muted (contraste adequado)
COR_PRIMARY = "#2ED3C8"      # Teal mais vivo para contraste em dark
COR_DESTAQUE = "#8B7CFF"     # Roxo destaque
COR_SUCESSO = "#2FCB70"      # Verde
COR_ALERTA = "#F5A524"       # Âmbar
COR_PERIGO = "#FF5F6D"       # Vermelho

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

STATUS_TERMINAL = "Rejeitado"

# Sombras escuras (mais intensas em dark mode)
SOMBRA_NIVEL_1 = "0 1px 3px rgba(2,8,23,0.45), 0 1px 2px rgba(2,8,23,0.3)"
SOMBRA_NIVEL_2 = "0 6px 12px rgba(2,8,23,0.55), 0 3px 6px rgba(2,8,23,0.4)"

# Espaçamento Airy
ESP_XS = "4px"
ESP_SM = "8px"
ESP_MD = "16px"
ESP_LG = "24px"
ESP_XL = "32px"

# Espaçamento específico para inputs
INPUT_PADDING_Y = "10px"
INPUT_PADDING_X = "14px"

# Raio de borda
RAIO_BORDA = "8px"
RAIO_BORDA_PILL = "9999px"

CARD_STYLE = {
    "backgroundColor": COR_SUPERFICIE,
    "border": f"1px solid {COR_BORDA_CLARA}",
    "borderRadius": RAIO_BORDA,
    "boxShadow": SOMBRA_NIVEL_1,
    "padding": f"{ESP_LG} {ESP_XL}",
    "transition": "box-shadow 0.2s ease, border-color 0.2s ease",
}

CARD_STYLE_HOVER = {
    **CARD_STYLE,
    "boxShadow": SOMBRA_NIVEL_2,
    "borderColor": COR_BORDA,
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

INPUT_FOCUS_STYLE = {
    "borderColor": COR_PRIMARY,
    "boxShadow": f"0 0 0 3px rgba(46, 211, 200, 0.28)",
}

SELECT_STYLE = {
    **INPUT_STYLE,
    "appearance": "auto",
}

SIDEBAR_WIDTH = 2
CONTENT_WIDTH = 10
CONTENT_PADDING = "32px 40px"

BADGE_OPACITY = 0.1
TAG_OPACITY = 0.12


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


def input_style() -> dict:
    return {
        **INPUT_STYLE,
    }


def input_focus_style() -> dict:
    return {
        **INPUT_STYLE,
        **INPUT_FOCUS_STYLE,
    }


def select_style() -> dict:
    return {**SELECT_STYLE}


COLUNA_ESTILO = {
    "marginBottom": "20px",
    "width": "100%",
}


def coluna_estilo() -> dict:
    return COLUNA_ESTILO
