COR_FUNDO = "#0E1117"
COR_SUPERFICIE = "#1A1D24"
COR_BORDA = "#2C303A"
COR_TEXTO = "#E4E6EB"
COR_TEXTO_SEC = "#9CA3AF"
COR_PRIMARY = "#00BFA6"
COR_DESTAQUE = "#6C63FF"

STATUS_CORES = {
    "Interessado": "#6C757D",
    "Currículo Enviado": "#0DCAF0",
    "Entrevista Agendada": "#FFC107",
    "Em Processo": "#6C63FF",
    "Oferta": "#198754",
    "Aceito": "#00BFA6",
    "Rejeitado": "#DC3545",
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

CARD_STYLE = {
    "backgroundColor": COR_SUPERFICIE,
    "border": f"1px solid {COR_BORDA}",
    "borderRadius": "12px",
    "padding": "24px 32px",
}

INPUT_STYLE = {
    "backgroundColor": COR_SUPERFICIE,
    "border": f"1px solid {COR_BORDA}",
    "borderRadius": "8px",
    "color": COR_TEXTO,
}

SIDEBAR_WIDTH = 2
CONTENT_WIDTH = 10

CONTENT_PADDING = "24px 32px"

BADGE_OPACITY = 0.2
TAG_OPACITY = 0.2

def badge_style(status: str) -> dict:
    cor = STATUS_CORES.get(status, COR_BORDA)
    return {
        "backgroundColor": f"{cor}33",
        "border": f"1px solid {cor}",
        "color": cor,
        "padding": "4px 12px",
        "borderRadius": "20px",
        "fontSize": "0.85rem",
        "fontWeight": 500,
    }

def tag_style() -> dict:
    return {
        "backgroundColor": f"{COR_DESTAQUE}33",
        "color": COR_DESTAQUE,
        "padding": "2px 10px",
        "borderRadius": "12px",
        "fontSize": "0.75rem",
        "marginRight": "6px",
        "marginBottom": "4px",
        "display": "inline-block",
    }

def pipeline_step_style(ativo: bool, cor: str) -> dict:
    return {
        "width": "32px",
        "height": "32px",
        "borderRadius": "50%",
        "border": f"2px solid {cor if ativo else COR_BORDA}",
        "backgroundColor": cor if ativo else "transparent",
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "center",
        "color": COR_TEXTO if ativo else COR_TEXTO_SEC,
        "fontWeight": "bold",
        "fontSize": "0.85rem",
        "zIndex": 2,
    }

def pipeline_connector_style(ativo: bool) -> dict:
    return {
        "flex": 1,
        "height": "2px",
        "backgroundColor": COR_BORDA if not ativo else STATUS_CORES.get("Aceito", COR_PRIMARY),
        "marginTop": "15px",
    }


COLUNA_ESTILO = {
    "marginBottom": "20px",
    "width": "100%",
}

def coluna_estilo() -> dict:
    return COLUNA_ESTILO


def input_style() -> dict:
    return {
        "backgroundColor": COR_SUPERFICIE,
        "border": f"1px solid {COR_BORDA}",
        "borderRadius": "8px",
        "color": COR_TEXTO,
        "padding": "8px 12px",
    }