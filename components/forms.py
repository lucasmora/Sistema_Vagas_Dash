from dash import html, dcc, callback, Input, Output
from styles import (
    COR_SUPERFICIE, COR_BORDA, COR_TEXTO, COR_TEXTO_SEC,
    COR_PRIMARY, INPUT_STYLE, CARD_STYLE,
)
from models import listar_portais, listar_tags

INPUT_LABEL = {"color": COR_TEXTO_SEC, "fontSize": "0.85rem", "marginBottom": "4px", "marginTop": "12px"}
INPUT_LABEL_FIRST = {"color": COR_TEXTO_SEC, "fontSize": "0.85rem", "marginBottom": "4px", "marginTop": 0}
DROPDOWN_STYLE = {**INPUT_STYLE, "color": COR_TEXTO}

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


def _label(texto: str, primeiro: bool = False) -> html.Label:
    return html.Label(texto, style=INPUT_LABEL_FIRST if primeiro else INPUT_LABEL)


def _input_simples(ide: str, placeholder: str = "", tipo: str = "text",
                   value: str = "") -> dcc.Input:
    if tipo == "date":
        return dcc.DatePickerSingle(
            id=ide,             date=value if value else None,
            style=INPUT_STYLE,
            className="form-control",
            display_format="YYYY-MM-DD",
        )
    return dcc.Input(
        id=ide, type=tipo, placeholder=placeholder, value=value,
        style=INPUT_STYLE,
        className="form-control",
    )


def _dropdown(ide: str, opcoes: list, placeholder: str = "",
              multi: bool = False, value=None):
    return dcc.Dropdown(
        id=ide, options=opcoes, placeholder=placeholder,
        multi=multi, value=value,
        style=DROPDOWN_STYLE,
        className="form-control",
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
                },
                inputStyle={"marginRight": "6px"},
            ),
            html.Div(id="salario-valores", children=[
                _label("Salário (R$)"),
                _input_simples("salario", "Ex: 12000", "number"),
                _label("Salário Máximo (R$)"),
                _input_simples("salario-max", "Ex: 15000", "number"),
            ]),
        ],
        style={"marginBottom": "8px"},
    )


@callback(
    Output("salario-valores", "children"),
    Input("salario-tipo", "value"),
)
def _condicional_salario(tipo: str):
    if tipo == "nai":
        return []
    if tipo == "fixo":
        return [
            _label("Salário (R$)"),
            _input_simples("salario", "Ex: 12000", "number"),
        ]
    return [
        _label("Salário Mínimo (R$)"),
        _input_simples("salario", "Ex: 12000", "number"),
        _label("Salário Máximo (R$)"),
        _input_simples("salario-max", "Ex: 15000", "number"),
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
            }),
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
                        _dropdown("nova-vaga-modalidade", MODALIDADE_OPCOES,
                                  "Selecione..."),
                    ], className="col-4"),
                    html.Div([
                        salario_inputs(),
                    ], className="col-8"),
                    html.Div([
                        _label("Portal"),
                        _dropdown("nova-vaga-portal", portal_opcoes, "Selecione..."),
                    ], className="col-6"),
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
                                   tooltip={"placement": "bottom", "always_visible": False}),
                    ], className="col-6"),
                    html.Div([
                        _label("Aderência"),
                        dcc.Slider(1, 5, 1, value=3, id="nova-vaga-aderencia",
                                   marks={i: str(i) for i in range(1, 6)},
                                   tooltip={"placement": "bottom", "always_visible": False}),
                    ], className="col-6"),
                    html.Div([
                        _label("Tags"),
                        _dropdown("nova-vaga-tags", tag_opcoes, "Selecione...", multi=True),
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
                                    "color": "#fff",
                                    "border": "none",
                                    "borderRadius": "8px",
                                    "padding": "6px 16px",
                                    "marginLeft": "8px",
                                    "cursor": "pointer",
                                },
                            ),
                        ], style={"display": "flex", "alignItems": "center"}),
                    ], className="col-12"),
                    html.Div([
                        _label("Descrição"),
                        dcc.Textarea(
                            id="nova-vaga-descricao",
                            placeholder="Texto completo do anúncio...",
                            style={**INPUT_STYLE, "minHeight": "120px", "width": "100%"},
                            className="form-control",
                        ),
                    ], className="col-12"),
                    html.Div([
                        _label("Notas"),
                        dcc.Textarea(
                            id="nova-vaga-notas",
                            placeholder="Anotações pessoais...",
                            style={**INPUT_STYLE, "minHeight": "80px", "width": "100%"},
                            className="form-control",
                        ),
                    ], className="col-12"),
                ],
                className="row",
                style={"margin": 0},
            ),
            html.Hr(style={"borderColor": COR_BORDA, "margin": "24px 0"}),
            html.Button(
                "Salvar Vaga",
                id="btn-salvar-vaga",
                className="btn",
                style={
                    "backgroundColor": COR_PRIMARY,
                    "color": "#fff",
                    "border": "none",
                    "borderRadius": "8px",
                    "padding": "12px 32px",
                    "fontSize": "1rem",
                    "fontWeight": 600,
                    "cursor": "pointer",
                    "width": "100%",
                },
            ),
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
                    _dropdown("edit-vaga-modalidade", MODALIDADE_OPCOES,
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
                    _dropdown("edit-vaga-portal", portal_opcoes,
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
                               tooltip={"placement": "bottom", "always_visible": False}),
                ], className="col-6"),
                html.Div([
                    _label("Aderência"),
                    dcc.Slider(1, 5, 1, value=vaga.get("aderencia") or 3,
                               id="edit-vaga-aderencia",
                               marks={i: str(i) for i in range(1, 6)},
                               tooltip={"placement": "bottom", "always_visible": False}),
                ], className="col-6"),
                html.Div([
                    _label("Tags"),
                    _dropdown("edit-vaga-tags", tag_opcoes, multi=True),
                ], className="col-12"),
                html.Div([
                    _label("Descrição"),
                    dcc.Textarea(
                        id="edit-vaga-descricao",
                        value=vaga.get("descricao") or "",
                        style={**INPUT_STYLE, "minHeight": "120px", "width": "100%"},
                        className="form-control",
                    ),
                ], className="col-12"),
                html.Div([
                    _label("Notas"),
                    dcc.Textarea(
                        id="edit-vaga-notas",
                        value=vaga.get("notas") or "",
                        style={**INPUT_STYLE, "minHeight": "80px", "width": "100%"},
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
                        "backgroundColor": COR_PRIMARY, "color": "#fff",
                        "border": "none", "borderRadius": "8px",
                        "padding": "10px 24px", "fontWeight": 600,
                        "cursor": "pointer", "marginRight": "12px",
                    },
                ),
                html.Button(
                    "Cancelar",
                    id="btn-cancelar-edicao",
                    className="btn",
                    style={
                        "backgroundColor": "transparent", "color": COR_TEXTO_SEC,
                        "border": f"1px solid {COR_BORDA}", "borderRadius": "8px",
                        "padding": "10px 24px", "cursor": "pointer",
                    },
                ),
            ], style={"marginTop": "20px", "display": "flex"}),
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
                    style={**INPUT_STYLE, "minHeight": "80px", "width": "100%"},
                    className="form-control",
                ),
            ]),
            html.Button(
                "Salvar Portal" if not editando else "Atualizar",
                id="btn-salvar-portal",
                className="btn",
                style={
                    "backgroundColor": COR_PRIMARY, "color": "#fff",
                    "border": "none", "borderRadius": "8px",
                    "padding": "10px 24px", "fontWeight": 600,
                    "cursor": "pointer", "width": "100%", "marginTop": "16px",
                },
            ),
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
                style={
                    "backgroundColor": COR_PRIMARY, "color": "#fff",
                    "border": "none", "borderRadius": "8px",
                    "padding": "10px 24px", "fontWeight": 600,
                    "cursor": "pointer", "width": "100%", "marginTop": "16px",
                },
            ),
        ],
        style={**CARD_STYLE},
    )
