from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from styles import (
    COR_SUPERFICIE, COR_BORDA, COR_TEXTO, COR_TEXTO_SEC,
    COR_PRIMARY, INPUT_STYLE, CARD_STYLE, SELECT_STYLE, SOMBRA_NIVEL_1,
    COR_BORDA_CLARA,
)
from models import listar_portais, listar_tags

INPUT_LABEL = {
    "color": COR_TEXTO_SEC, "fontSize": "0.8125rem",
    "marginBottom": "6px", "marginTop": "16px",
    "fontWeight": 500,
}
INPUT_LABEL_FIRST = {
    "color": COR_TEXTO_SEC, "fontSize": "0.8125rem",
    "marginBottom": "6px", "marginTop": 0,
    "fontWeight": 500,
}

TIPO_SALARIO_OPCOES = [
    {"label": "Valor fixo", "value": "fixo"},
    {"label": "Faixa salarial", "value": "faixa"},
    {"label": "Não informado", "value": "nai"},
]

STATUS_OPCOES = [
    {"label": s, "value": s}
    for s in ["Interessado", "Currículo Enviado", "Entrevista Agendada",
              "Em Processo", "Oferta", "Aceito", "Rejeitado"]
]

MODALIDADE_OPCOES = [
    {"label": m, "value": m}
    for m in ["Remoto", "Presencial", "Híbrido"]
]

_BOTAO_PADRAO = {
    "border": "none",
    "borderRadius": "8px",
    "padding": "12px 32px",
    "fontSize": "1rem",
    "fontWeight": 600,
    "cursor": "pointer",
    "width": "100%",
    "transition": "all 0.15s ease",
}

_BOTAO_PRIMARIO = {
    **_BOTAO_PADRAO,
    "backgroundColor": COR_PRIMARY,
    "color": COR_TEXTO,
    "boxShadow": SOMBRA_NIVEL_1,
}

_BOTAO_SECUNDARIO = {
    **_BOTAO_PADRAO,
    "backgroundColor": "transparent",
    "color": COR_TEXTO_SEC,
    "border": f"1px solid {COR_BORDA}",
    "boxShadow": "none",
}


def _label(texto: str, primeiro: bool = False) -> html.Label:
    return html.Label(texto, style=INPUT_LABEL_FIRST if primeiro else INPUT_LABEL)


def _input_simples(ide: str, placeholder: str = "", tipo: str = "text",
                   value: str = "") -> dcc.Input:
    if tipo == "date":
        return dcc.DatePickerSingle(
            id=ide, date=value if value else None,
            style=INPUT_STYLE,
            className="form-control",
            display_format="YYYY-MM-DD",
        )
    return dcc.Input(
        id=ide, type=tipo, placeholder=placeholder, value=value,
        style=INPUT_STYLE,
        className="form-control",
    )


def _select(ide: str, opcoes: list, placeholder: str = "",
            value=None):
    return dbc.Select(
        id=ide,
        options=[{"label": placeholder, "value": ""}] + opcoes if placeholder else opcoes,
        value=value or "",
        style={**SELECT_STYLE, "backgroundColor": COR_SUPERFICIE},
        className="form-control",
    )


def _dropdown_multi(ide: str, opcoes: list, placeholder: str = "",
                    value=None):
    return dcc.Dropdown(
        id=ide, options=opcoes, placeholder=placeholder,
        multi=True, value=value,
        style={**INPUT_STYLE, "color": COR_TEXTO},
        className="form-control",
    )


def modal_autofill_infojobs() -> dbc.Modal:
    """Modal para auto-preenchimento de vaga do InfoJobs"""
    return dbc.Modal(
        id="modal-autofill-infojobs",
        is_open=False,
        backdrop="static",
        centered=True,
        style={"fontFamily": "var(--font-sans)"},
        children=[
            dbc.ModalHeader(
                dbc.ModalTitle("🔍 Auto-preencher InfoJobs",
                               style={"color": COR_TEXTO, "fontWeight": 600}),
                close_button=False,
                style={"backgroundColor": COR_SUPERFICIE, "borderBottom": f"1px solid {COR_BORDA}"},
            ),
            dbc.ModalBody(
                style={"backgroundColor": COR_SUPERFICIE},
                children=[
                    html.P("Cole o ID da vaga do InfoJobs (ex: 11616056):",
                           style={"color": COR_TEXTO_SEC, "marginBottom": "12px"}),
                    dcc.Input(
                        id="autofill-infojobs-id",
                        type="text",
                        placeholder="11616056",
                        style={**INPUT_STYLE, "width": "100%", "marginBottom": "16px"},
                    ),
                    html.Div(
                        id="autofill-infojobs-status",
                        style={"color": COR_TEXTO_SEC, "fontSize": "0.875rem", "marginBottom": "8px"},
                    ),
                    dcc.Loading(
                        id="autofill-loading",
                        children=html.Div(id="autofill-loading-output"),
                        type="circle",
                        color=COR_PRIMARY,
                    ),
                ],
            ),
            dbc.ModalFooter(
                style={"backgroundColor": COR_SUPERFICIE, "borderTop": f"1px solid {COR_BORDA}"},
                children=[
                    dbc.Button(
                        "Cancelar",
                        id="btn-autofill-cancel",
                        color="secondary",
                        className="btn btn-sm",
                        style={
                            "borderRadius": "8px",
                            "fontWeight": 500,
                            "marginRight": "8px",
                        },
                    ),
                    dbc.Button(
                        "Buscar e Preencher",
                        id="btn-autofill-fetch",
                        color="primary",
                        className="btn btn-sm",
                        style={
                            "backgroundColor": COR_PRIMARY,
                            "border": "none",
                            "borderRadius": "8px",
                            "fontWeight": 600,
                        },
                    ),
                ],
            ),
        ],  
    )  


def salario_inputs() -> html.Div:
    return html.Div(
        id="salario-area",
        children=[
            _label("Tipo de Salário", primeiro=True),
            dcc.RadioItems(
                id="salario-tipo",
                options=TIPO_SALARIO_OPCOES,
                value="nai",
                labelStyle={
                    "display": "inline-block",
                    "marginRight": "20px",
                    "color": COR_TEXTO,
                    "fontSize": "0.875rem",
                },
                inputStyle={"marginRight": "6px", "accentColor": COR_PRIMARY},
            ),
            html.Div(id="salario-valores", children=[
                html.Div(_label("Salário (R$)"), style={"display": "none"}),
                dcc.Input(id="salario", type="number", style={"display": "none"}),
                html.Div(_label("Salário Máximo (R$)"), style={"display": "none"}),
                dcc.Input(id="salario-max", type="number", style={"display": "none"}),
            ]),
        ],
        style={"marginBottom": "8px"},
    )


@callback(
    Output("salario-valores", "children", allow_duplicate=True),
    Input("salario-tipo", "value"),
    State("autofill-salary", "data"),
    prevent_initial_call=True,
)
def _condicional_salario(tipo: str, autofill_data):
    """Atualiza visibilidade e valores dos inputs de salário"""
    # Obter valores (autofill tem prioridade)
    val = None
    val_max = None
    if autofill_data and isinstance(autofill_data, dict):
        val = autofill_data.get("salario")
        val_max = autofill_data.get("salario_max")
    
    # Montar inputs conforme o tipo
    if tipo == "nai":
        return [
            html.Div(_label("Salário (R$)"), style={"display": "none"}),
            dcc.Input(id="salario", type="number", style={"display": "none"}),
            html.Div(_label("Salário Máximo (R$)"), style={"display": "none"}),
            dcc.Input(id="salario-max", type="number", style={"display": "none"}),
        ]
    if tipo == "fixo":
        return [
            _label("Salário (R$)"),
            _input_simples("salario", "Ex: 12000", "number",
                           value=str(val) if val is not None else ""),
            html.Div(_label("Salário Máximo (R$)"), style={"display": "none"}),
            dcc.Input(id="salario-max", type="number", style={"display": "none"}),
        ]
    # tipo == "faixa"
    return [
        _label("Salário Mínimo (R$)"),
        _input_simples("salario", "Ex: 2000", "number",
                       value=str(val) if val is not None else ""),
        _label("Salário Máximo (R$)"),
        _input_simples("salario-max", "Ex: 20000", "number",
                       value=str(val_max) if val_max is not None else ""),
    ]


def form_nova_vaga() -> html.Div:
    portais = listar_portais()
    portal_opcoes = [
        {"label": "Sem portal", "value": ""},
        *[{"label": p["nome"], "value": p["id"]} for p in portais],
    ]
    tags_disponiveis = listar_tags()
    tag_opcoes = [{"label": t["nome"], "value": t["id"]} for t in tags_disponiveis]

    return html.Div(
        children=[
            html.H3("Nova Vaga", style={
                "color": COR_TEXTO, "marginBottom": "24px", "fontWeight": 600,
                "fontSize": "1.5rem",
            }),
            dcc.Store(id="autofill-salary", data=None),
            html.Div(
                children=[
                    html.Div([
                        _label("Nome *", primeiro=True),
                        _input_simples("nova-vaga-nome", "Ex: Gerente Financeiro - Stone"),
                    ], className="col-12"),
                    html.Div([
                        _label("Empresa"),
                        _input_simples("nova-vaga-empresa", "Ex: Stone Pagamentos"),
                    ], className="col-6"),
                    html.Div([
                        _label("Link"),
                        _input_simples("nova-vaga-link", "URL da vaga"),
                    ], className="col-6"),
                    html.Div([
                        _label("Modalidade"),
                        _select("nova-vaga-modalidade", MODALIDADE_OPCOES,
                                "Selecione..."),
                    ], className="col-4"),
                    html.Div([
                        salario_inputs(),
                    ], className="col-8"),
                    html.Div([
                        _label("Portal"),
                        _select("nova-vaga-portal", portal_opcoes, "Selecione..."),
                    ], className="col-6"),
                    html.Div([
                        _label("Data Publicação"),
                        _input_simples("nova-vaga-data-publicacao", "", "date"),
                    ], className="col-3"),
                    html.Div([
                        _label("Data Encontrada"),
                        _input_simples("nova-vaga-data-encontrada", "", "date"),
                    ], className="col-3"),
                    html.Div([
                        _label("Data Envio"),
                        _input_simples("nova-vaga-data-envio", "", "date"),
                    ], className="col-3"),
                    html.Div([
                        _label("Interesse"),
                        dcc.Slider(1, 5, 1, value=3, id="nova-vaga-interesse",
                                   marks={i: str(i) for i in range(1, 6)},
                                   tooltip={"placement": "bottom",
                                            "always_visible": False}),
                    ], className="col-6"),
                    html.Div([
                        _label("Aderência"),
                        dcc.Slider(1, 5, 1, value=3, id="nova-vaga-aderencia",
                                   marks={i: str(i) for i in range(1, 6)},
                                   tooltip={"placement": "bottom",
                                            "always_visible": False}),
                    ], className="col-6"),
                    html.Div([
                        _label("Tags"),
                        _dropdown_multi("nova-vaga-tags", tag_opcoes,
                                        "Selecione..."),
                    ], className="col-12"),
                    html.Div([
                        _label("Nova Tag"),
                        html.Div([
                            _input_simples("nova-vaga-nova-tag", "Nome da tag"),
                            html.Button(
                                "Adicionar", id="btn-add-tag-vaga",
                                className="btn btn-sm",
                                style={
                                    "backgroundColor": COR_PRIMARY,
                                    "color": COR_TEXTO,
                                    "border": "none",
                                    "borderRadius": "8px",
                                    "padding": "8px 16px",
                                    "marginLeft": "8px",
                                    "cursor": "pointer",
                                    "fontWeight": 500,
                                    "transition": "all 0.15s ease",
                                },
                            ),
                        ], style={"display": "flex", "alignItems": "center"}),
                    ], className="col-12"),
                    html.Div([
                        _label("Descrição"),
                        dcc.Textarea(
                            id="nova-vaga-descricao",
                            placeholder="Texto completo do anúncio...",
                            style={**INPUT_STYLE, "minHeight": "140px",
                                   "width": "100%", "resize": "vertical"},
                            className="form-control",
                        ),
                    ], className="col-12"),
                    html.Div([
                        _label("Notas"),
                        dcc.Textarea(
                            id="nova-vaga-notas",
                            placeholder="Anotações pessoais...",
                            style={**INPUT_STYLE, "minHeight": "100px",
                                   "width": "100%", "resize": "vertical"},
                            className="form-control",
                        ),
                    ], className="col-12"),
                ],
                className="row",
                style={"margin": 0},
            ),
            html.Hr(style={
                "borderColor": COR_BORDA_CLARA, "margin": "32px 0",
                "opacity": 0.5,
            }),
            html.Button(
                "Salvar Vaga",
                id="btn-salvar-vaga",
                className="btn",
                style=_BOTAO_PRIMARIO,
            ),
            modal_autofill_infojobs(),
        ],
        style={
            **CARD_STYLE,
            "maxWidth": "800px",
            "margin": "0 auto",
        },
    )


def form_editar_vaga(vaga: dict) -> html.Div:
    portais = listar_portais()
    portal_opcoes = [
        {"label": "Sem portal", "value": ""},
        *[{"label": p["nome"], "value": p["id"]} for p in portais],
    ]
    tags_disponiveis = listar_tags()
    tag_opcoes = [{"label": t["nome"], "value": t["id"]} for t in tags_disponiveis]

    tipo_salario = "nai"
    if vaga.get("salario") is not None and vaga.get("salario_max") is not None:
        tipo_salario = "faixa"
    elif vaga.get("salario") is not None:
        tipo_salario = "fixo"

    return html.Div(
        children=[
            html.H4(f"Editar: {vaga.get('nome', '')}", style={
                "color": COR_TEXTO, "marginBottom": "20px", "fontWeight": 600,
            }),
            html.Div([
                html.Div([
                    _label("Nome *", primeiro=True),
                    _input_simples("edit-vaga-nome", value=vaga.get("nome", "")),
                ], className="col-12"),
                html.Div([
                    _label("Empresa"),
                    _input_simples("edit-vaga-empresa",
                                   value=vaga.get("empresa") or ""),
                ], className="col-6"),
                html.Div([
                    _label("Link"),
                    _input_simples("edit-vaga-link", value=vaga.get("link") or ""),
                ], className="col-6"),
                html.Div([
                    _label("Modalidade"),
                    _select("edit-vaga-modalidade", MODALIDADE_OPCOES,
                            value=vaga.get("modalidade") or ""),
                ], className="col-4"),
                html.Div([
                    _label("Salário (R$)"),
                    _input_simples("edit-vaga-salario", "Ex: 12000", "number",
                                   value=vaga.get("salario") or ""),
                ], className="col-4"),
                html.Div([
                    _label("Salário Máximo (R$)"),
                    _input_simples("edit-vaga-salario-max", "Ex: 15000", "number",
                                   value=vaga.get("salario_max") or ""),
                ], className="col-4"),
                html.Div([
                    _label("Portal"),
                    _select("edit-vaga-portal", portal_opcoes,
                            value=vaga.get("portal_id") or ""),
                ], className="col-6"),
                html.Div([
                    _label("Data Encontrada"),
                    _input_simples("edit-vaga-data-encontrada", "", "date",
                                   value=vaga.get("data_encontrada") or ""),
                ], className="col-3"),
                html.Div([
                    _label("Data Envio"),
                    _input_simples("edit-vaga-data-envio", "", "date",
                                   value=vaga.get("data_envio") or ""),
                ], className="col-3"),
                html.Div([
                    _label("Interesse"),
                    dcc.Slider(1, 5, 1, value=vaga.get("interesse") or 3,
                               id="edit-vaga-interesse",
                               marks={i: str(i) for i in range(1, 6)},
                               tooltip={"placement": "bottom",
                                        "always_visible": False}),
                ], className="col-6"),
                html.Div([
                    _label("Aderência"),
                    dcc.Slider(1, 5, 1, value=vaga.get("aderencia") or 3,
                               id="edit-vaga-aderencia",
                               marks={i: str(i) for i in range(1, 6)},
                               tooltip={"placement": "bottom",
                                        "always_visible": False}),
                ], className="col-6"),
                html.Div([
                    _label("Tags"),
                    _dropdown_multi("edit-vaga-tags", tag_opcoes),
                ], className="col-12"),
                html.Div([
                    _label("Descrição"),
                    dcc.Textarea(
                        id="edit-vaga-descricao",
                        value=vaga.get("descricao") or "",
                        style={**INPUT_STYLE, "minHeight": "140px",
                               "width": "100%", "resize": "vertical"},
                        className="form-control",
                    ),
                ], className="col-12"),
                html.Div([
                    _label("Notas"),
                    dcc.Textarea(
                        id="edit-vaga-notas",
                        value=vaga.get("notas") or "",
                        style={**INPUT_STYLE, "minHeight": "100px",
                               "width": "100%", "resize": "vertical"},
                        className="form-control",
                    ),
                ], className="col-12"),
            ], className="row", style={"margin": 0}),
            html.Div([
                html.Button(
                    "Salvar alterações",
                    id="btn-salvar-edicao",
                    className="btn",
                    style={
                        **_BOTAO_PRIMARIO,
                        "width": "auto",
                    },
                ),
                html.Button(
                    "Cancelar",
                    id="btn-cancelar-edicao",
                    className="btn",
                    style={
                        **_BOTAO_SECUNDARIO,
                        "width": "auto",
                        "marginLeft": "12px",
                    },
                ),
            ], style={"marginTop": "24px", "display": "flex"}),
        ],
        style={**CARD_STYLE},
    )


def form_portal(portal: dict = None) -> html.Div:
    editando = portal is not None
    return html.Div(
        children=[
            html.H4(
                "Editar Portal" if editando else "Novo Portal",
                style={"color": COR_TEXTO, "marginBottom": "16px", "fontWeight": 600},
            ),
            html.Div([
                _label("Nome", primeiro=True),
                _input_simples(
                    "form-portal-nome", "Ex: LinkedIn",
                    value=portal["nome"] if editando else "",
                ),
                _label("URL Base"),
                _input_simples(
                    "form-portal-url", "Ex: linkedin.com",
                    value=portal.get("url_base", "") if editando else "",
                ),
                _label("Tipo de Login"),
                _input_simples(
                    "form-portal-login", "Ex: e-mail",
                    value=portal.get("tipo_login", "") if editando else "",
                ),
                _label("Última Atualização"),
                _input_simples(
                    "form-portal-data", "", "date",
                    value=portal.get("ultima_atualizacao", "") if editando else "",
                ),
                _label("Notas"),
                dcc.Textarea(
                    id="form-portal-notas",
                    placeholder="Observações sobre o portal...",
                    value=portal.get("notas", "") if editando else "",
                    style={**INPUT_STYLE, "minHeight": "100px",
                           "width": "100%", "resize": "vertical"},
                    className="form-control",
                ),
            ]),
            html.Div([
                html.Button(
                    "Salvar Portal" if not editando else "Atualizar",
                    id="btn-salvar-portal",
                    className="btn",
                    style={**_BOTAO_PRIMARIO, "width": "auto"},
                ),
                html.Button(
                    "Cancelar",
                    id="btn-cancelar-edicao-portal",
                    className="btn",
                    style={**_BOTAO_SECUNDARIO, "width": "auto", "marginLeft": "12px"},
                ) if editando else None,
            ], style={"display": "flex", "marginTop": "16px"}),
        ],
        style={**CARD_STYLE},
    )


def form_tag() -> html.Div:
    return html.Div(
        children=[
            html.H4("Nova Tag", style={
                "color": COR_TEXTO, "marginBottom": "16px", "fontWeight": 600,
            }),
            html.Div([
                _label("Nome", primeiro=True),
                _input_simples("form-tag-nome", "Ex: Python"),
            ]),
            html.Button(
                "Adicionar",
                id="btn-add-tag",
                className="btn",
                style={**_BOTAO_PRIMARIO, "marginTop": "16px"},
            ),
        ],
        style={**CARD_STYLE},
    )
