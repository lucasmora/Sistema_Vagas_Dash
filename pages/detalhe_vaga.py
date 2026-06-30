import dash
from dash import html, dcc, callback, Input, Output, State, callback_context, no_update, MATCH, ALL
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from models import get_vaga, listar_historico, atualizar_vaga, excluir_vaga, get_tags_da_vaga, criar_tag
from components.pipeline import pipeline_view
from components.forms import form_editar_vaga, form_nova_vaga
from styles import (
    COR_TEXTO, COR_TEXTO_SEC, COR_TEXTO_MUTED,
    COR_BORDA_CLARA, COR_PRIMARY, COR_PERIGO, COR_ELEVADO,
    CARD_STYLE, tag_style, SOMBRA_NIVEL_1,
    COLUNA_ESTILO,
)


def _info_campo(label, valor):
    if isinstance(valor, str) and (valor.startswith("http://") or valor.startswith("https://")):
        valor_elem = html.A(
            valor, href=valor, target="_blank",
            style={"color": COR_PRIMARY, "textDecoration": "none",
                   "fontSize": "0.875rem", "fontWeight": 500},
        )
    else:
        valor_elem = html.P(valor or "—", style={
            "color": COR_TEXTO, "margin": "4px 0 0 0", "fontSize": "0.875rem",
        })
    return html.Div(
        children=[
            html.Span(label, style={
                "color": COR_TEXTO_SEC, "fontSize": "0.8125rem", "fontWeight": 600,
                "textTransform": "uppercase", "letterSpacing": "0.3px",
            }),
            valor_elem,
        ],
        style=COLUNA_ESTILO,
    )


def layout() -> html.Div:
    return html.Div([
        dcc.Store(id="vaga-id-store", data=None),
        html.Div(id="page-content-placeholder"),
    ])


@callback(
    Output("page-content-placeholder", "children"),
    Output("vaga-id-store", "data"),
    Input("url", "pathname"),
    prevent_initial_call=True,
)
def display_page(pathname):
    if not pathname.startswith("/vagas/"):
        raise PreventUpdate
    
    try:
        vaga_id = int(pathname.split("/")[-1])
    except (ValueError, IndexError):
        raise PreventUpdate
    
    vaga = get_vaga(vaga_id)
    if not vaga:
        return html.Div([
            html.H2("Vaga não encontrada", style={"color": COR_TEXTO_SEC}),
            dcc.Link("Voltar para Listar Vagas", href="/vagas"),
        ]), None
    
    tags = get_tags_da_vaga(vaga_id)
    vaga["_tags"] = tags
    historico = listar_historico(vaga_id)
    vaga["_historico"] = historico
    
    return detalhes_vaga(vaga), vaga_id


def detalhes_vaga(vaga: dict) -> html.Div:
    vaga_id = vaga["id"]
    
    _BOTAO_DARK = {
        "color": COR_TEXTO,
        "border": "none",
        "borderRadius": "8px",
        "padding": "12px 32px",
        "fontWeight": 600,
        "cursor": "pointer",
        "transition": "all 0.15s ease",
        "boxShadow": SOMBRA_NIVEL_1,
    }

    return html.Div([
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4(
                            f"{vaga.get('nome', 'Sem nome')} - {vaga.get('empresa') or 'Confidencial'}",
                            style={
                                "color": COR_TEXTO,
                                "margin": 0,
                                "fontSize": "1.5rem",
                                "fontWeight": 700,
                            },
                        ),
                        html.P(
                            f"ID: {vaga_id}",
                            style={
                                "color": COR_TEXTO_SEC,
                                "margin": "8px 0 0 0",
                                "fontSize": "0.875rem",
                            },
                        ),
                    ], style={"marginBottom": "24px"}),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H5("Informações", style={
                                        "color": COR_TEXTO, "marginBottom": "20px",
                                        "fontWeight": 600, "fontSize": "1.1rem",
                                    }),
                                    dbc.Row([
                                        _info_campo("Nome", vaga.get("nome")),
                                        _info_campo("Empresa", vaga.get("empresa") or "Confidencial"),
                                        _info_campo("Link", vaga.get("link") or "—"),
                                        _info_campo("Modalidade", vaga.get("modalidade") or "—"),
                                        _info_campo("Interesse", vaga.get("interesse") or "—"),
                                        _info_campo("Aderência", vaga.get("aderencia") or "—"),
                                        _info_campo("Status", vaga.get("status") or "—"),
                                        _info_campo("Data Encontrada", vaga.get("data_encontrada") or "—"),
                                        _info_campo("Data Envio", vaga.get("data_envio") or "⏳ Não enviado"),
                                        _info_campo("Portal", vaga.get("portal_nome") or "Sem portal"),
                                    ], className="g-3"),
                                ]),
                            ], style=CARD_STYLE),
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.Div(
                                        "📄 Descrição",
                                        id="btn-toggle-descricao",
                                        n_clicks=0,
                                        style={
                                            "color": COR_TEXTO, "marginBottom": "12px",
                                            "fontWeight": 600, "cursor": "pointer",
                                            "fontSize": "1.1rem",
                                        },
                                    ),
                                    dbc.Collapse(
                                        dcc.Textarea(
                                            value=vaga.get("descricao") or "",
                                            style={
                                                "width": "100%",
                                                "height": "150px",
                                                "backgroundColor": COR_ELEVADO,
                                                "border": f"1px solid {COR_BORDA_CLARA}",
                                                "borderRadius": "8px",
                                                "padding": "12px",
                                                "color": COR_TEXTO,
                                                "resize": "none",
                                                "fontFamily": "var(--font-mono)",
                                            },
                                            readOnly=True,
                                        ),
                                        id="collapse-descricao",
                                        is_open=False,
                                    ),
                                ]),
                            ], style=CARD_STYLE),
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.Div(
                                        "📝 Notas",
                                        id="btn-toggle-notas",
                                        n_clicks=0,
                                        style={
                                            "color": COR_TEXTO, "marginBottom": "12px",
                                            "fontWeight": 600, "cursor": "pointer",
                                            "fontSize": "1.1rem",
                                        },
                                    ),
                                    dbc.Collapse(
                                        dcc.Textarea(
                                            value=vaga.get("notas") or "",
                                            style={
                                                "width": "100%",
                                                "height": "150px",
                                                "backgroundColor": COR_ELEVADO,
                                                "border": f"1px solid {COR_BORDA_CLARA}",
                                                "borderRadius": "8px",
                                                "padding": "12px",
                                                "color": COR_TEXTO,
                                                "resize": "none",
                                                "fontFamily": "var(--font-mono)",
                                            },
                                            readOnly=True,
                                        ),
                                        id="collapse-notas",
                                        is_open=False,
                                    ),
                                ]),
                            ], style=CARD_STYLE),
                        ], width=6),
                    ], className="g-4"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H5("Tags", style={
                                        "color": COR_TEXTO, "marginBottom": "12px",
                                        "fontWeight": 600, "fontSize": "1.1rem",
                                    }),
                                    html.Div([
                                        *[html.Span(tag["nome"] if isinstance(tag, dict) else tag,
                                                   style=tag_style()) for tag in vaga.get("_tags", [])],
                                    ], style={"display": "flex", "flexWrap": "wrap", "gap": "8px"}),
                                ]),
                            ], style=CARD_STYLE),
                        ], width=4),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H5("Pipeline", style={
                                        "color": COR_TEXTO, "marginBottom": "12px",
                                        "fontWeight": 600, "fontSize": "1.1rem",
                                    }),
                                    pipeline_view(vaga.get("status", "Interessado")),
                                ]),
                            ], style=CARD_STYLE),
                        ], width=8),
                    ], className="g-4"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.Div(
                                        "📜 Histórico de Status",
                                        id="btn-toggle-historico",
                                        n_clicks=0,
                                        style={
                                            "color": COR_TEXTO, "marginBottom": "12px",
                                            "fontWeight": 600, "cursor": "pointer",
                                            "fontSize": "1.1rem",
                                        },
                                    ),
                                    dbc.Collapse(
                                        html.Div(
                                            children=[html.Div([
                                                html.Strong(f"{h.get('data_mudanca', '—')}: ", style={"color": COR_TEXTO_SEC}),
                                                html.Span(f"{h.get('status_anterior', '—')} → {h.get('status_novo', '—')}", style={"color": COR_TEXTO}),
                                            ], style={"marginBottom": "8px"}) for h in vaga.get("_historico", [])],
                                            style={"padding": "12px"},
                                        ),
                                        id="collapse-historico",
                                        is_open=False,
                                    ),
                                ]),
                            ], style=CARD_STYLE),
                        ], width=12),
                    ]),
                ], width=12),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H5("Alterar Status", style={
                                "color": COR_TEXTO, "marginBottom": "16px",
                                "fontWeight": 600, "fontSize": "1.1rem",
                            }),
                            dbc.Row([
                                dbc.Col([
                                    dcc.Dropdown(
                                        id="status-dropdown",
                                        options=[
                                            {"label": s, "value": s}
                                            for s in ["Interessado", "Currículo Enviado", "Entrevista Agendada",
                                                     "Em Processo", "Oferta", "Aceito", "Rejeitado"]
                                        ],
                                        value=vaga.get("status", "Interessado"),
                                        placeholder="Selecione um status...",
                                        style={
                                            "backgroundColor": COR_ELEVADO,
                                            "border": f"1px solid {COR_BORDA_CLARA}",
                                            "borderRadius": "8px",
                                            "color": COR_TEXTO,
                                        },
                                    ),
                                ], width=8),
                                dbc.Col([
                                    html.Button(
                                        "Atualizar Status",
                                        id="btn-atualizar-status",
                                        className="btn",
                                        style={
                                            "backgroundColor": COR_PRIMARY,
                                            "color": COR_TEXTO,
                                            "border": "none",
                                            "borderRadius": "8px",
                                            "padding": "12px 16px",
                                            "fontWeight": 600,
                                            "cursor": "pointer",
                                            "width": "100%",
                                            "transition": "all 0.15s ease",
                                        },
                                    ),
                                ], width=4),
                            ], className="g-4"),
                        ], style=CARD_STYLE),
                    ], width=12),
                ]),
            ]),
            html.Hr(style={"borderColor": COR_BORDA_CLARA, "margin": "32px 0", "opacity": 0.5}),
            dbc.Row([
                dbc.Col([
                    html.Button(
                        "Editar",
                        id={"type": "btn-editar-vaga", "index": vaga_id},
                        className="btn",
                        style={
                            **_BOTAO_DARK,
                            "backgroundColor": COR_PRIMARY,
                            "marginRight": "12px",
                        },
                    ),
                    html.Button(
                        "Excluir",
                        id={"type": "btn-excluir-vaga-detalhe", "index": vaga_id},
                        className="btn",
                        style={
                            **_BOTAO_DARK,
                            "backgroundColor": COR_PERIGO,
                        },
                    ),
                ], style={"display": "flex"}),
            ]),
            html.Div(id="edit-mode-placeholder", style={"marginTop": "32px"}),
        ], style={"padding": "0"}),
    ])


@callback(
    Output({"type": "btn-editar-vaga", "index": ALL}, "n_clicks"),
    Output("edit-mode-placeholder", "children"),
    Input({"type": "btn-editar-vaga", "index": ALL}, "n_clicks"),
    State("vaga-id-store", "data"),
    prevent_initial_call=True,
)
def editar_vaga(n_clicks_list, vaga_id):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    n_clicks_list = n_clicks_list or []
    new_clicks = [None] * len(n_clicks_list)
    
    vaga = get_vaga(vaga_id)
    if not vaga:
        return new_clicks, html.Div([
            html.P("Vaga não encontrada", style={"color": COR_PERIGO}),
        ])
    
    return new_clicks, form_editar_vaga(vaga)


@callback(
    Output("edit-mode-placeholder", "children", allow_duplicate=True),
    Output("vagas-trigger", "data", allow_duplicate=True),
    Output("notification", "data", allow_duplicate=True),
    Input({"type": "btn-excluir-vaga-detalhe", "index": ALL}, "n_clicks"),
    State("vaga-id-store", "data"),
    prevent_initial_call=True,
)
def excluir_vaga_detalhe(n_clicks_list, vaga_id):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    if not vaga_id:
        raise PreventUpdate
    
    try:
        excluir_vaga(vaga_id)
        return None, None, {"message": "Vaga excluída!", "type": "success"}
    except Exception as e:
        return None, None, {"message": f"Erro ao excluir vaga: {str(e)}", "type": "danger"}


@callback(
    Output("status-dropdown", "value", allow_duplicate=True),
    Output("vagas-trigger", "data", allow_duplicate=True),
    Output("notification", "data", allow_duplicate=True),
    Input("btn-atualizar-status", "n_clicks"),
    State("status-dropdown", "value"),
    State("vaga-id-store", "data"),
    prevent_initial_call=True,
)
def atualizar_status(n_clicks, novo_status, vaga_id):
    if not n_clicks or not novo_status or not vaga_id:
        raise PreventUpdate
    
    vaga = get_vaga(vaga_id)
    if not vaga:
        return no_update, None, {"message": "Vaga não encontrada", "type": "danger"}
    
    if vaga.get("status") == novo_status:
        return no_update, None, {"message": "Status já está definido", "type": "info"}
    
    try:
        atualizar_vaga(vaga_id, **{
            "nome": vaga.get("nome") or "",
            "empresa": vaga.get("empresa") or "",
            "link": vaga.get("link") or "",
            "salario": vaga.get("salario") or None,
            "salario_max": vaga.get("salario_max") or None,
            "modalidade": vaga.get("modalidade") or "",
            "descricao": vaga.get("descricao") or "",
            "interesse": vaga.get("interesse") or 3,
            "aderencia": vaga.get("aderencia") or 3,
            "status": novo_status,
            "portal_id": vaga.get("portal_id") or None,
            "data_encontrada": vaga.get("data_encontrada") or "",
            "data_envio": vaga.get("data_envio") or "",
            "notas": vaga.get("notas") or "",
            "tag_ids": [t.get("id") if isinstance(t, dict) else t for t in vaga.get("_tags", [])],
        })
        return novo_status, None, {"message": "Status atualizado com sucesso!", "type": "success"}
    except Exception as e:
        return no_update, None, {"message": f"Erro ao atualizar status: {str(e)}", "type": "danger"}


@callback(
    Output("vagas-trigger", "data", allow_duplicate=True),
    Output("notification", "data", allow_duplicate=True),
    Input("btn-salvar-edicao", "n_clicks"),
    State("edit-vaga-nome", "value"),
    State("edit-vaga-empresa", "value"),
    State("edit-vaga-link", "value"),
    State("edit-vaga-salario", "value"),
    State("edit-vaga-salario-max", "value"),
    State("edit-vaga-modalidade", "value"),
    State("edit-vaga-portal", "value"),
    State("edit-vaga-data-encontrada", "date"),
    State("edit-vaga-data-envio", "date"),
    State("edit-vaga-interesse", "value"),
    State("edit-vaga-aderencia", "value"),
    State("edit-vaga-tags", "value"),
    State("edit-vaga-descricao", "value"),
    State("edit-vaga-notas", "value"),
    State("vaga-id-store", "data"),
    State("vagas-trigger", "data"),
    prevent_initial_call=True,
)
def salvar_edicao_vaga(
    n_clicks, nome, empresa, link, salario, salario_max, modalidade,
    portal, data_encontrada, data_envio, interesse, aderencia, tag_ids,
    descricao, notas, vaga_id, trigger
):
    if not n_clicks:
        raise PreventUpdate
    
    nome = (nome or "").strip()
    if not nome:
        return no_update, None, {"message": "Nome é obrigatório", "type": "warning"}
    
    tag_ids = tag_ids or []
    try:
        atualizar_vaga(
            vaga_id,
            nome=nome,
            empresa=empresa or "",
            link=link or "",
            salario=float(salario) if salario else None,
            salario_max=float(salario_max) if salario_max else None,
            modalidade=modalidade or "",
            descricao=descricao or "",
            interesse=int(interesse) if interesse else 3,
            aderencia=int(aderencia) if aderencia else 3,
            status="Interessado",
            portal_id=int(portal) if portal and portal != "" else None,
            data_encontrada=data_encontrada or "",
            data_envio=data_envio or "",
            notas=notas or "",
            tag_ids=[int(t) for t in tag_ids] if tag_ids else None,
        )
        return trigger + 1, None, {"message": "Vaga atualizada com sucesso!", "type": "success"}
    except Exception as e:
        return no_update, None, {"message": f"Erro ao atualizar vaga: {str(e)}", "type": "danger"}

@callback(
    Output("collapse-descricao", "is_open"),
    Input("btn-toggle-descricao", "n_clicks"),
    State("collapse-descricao", "is_open"),
    prevent_initial_call=True,
)
def toggle_descricao(n_clicks, is_open):
    if not n_clicks:
        raise PreventUpdate
    return not is_open


@callback(
    Output("collapse-notas", "is_open"),
    Input("btn-toggle-notas", "n_clicks"),
    State("collapse-notas", "is_open"),
    prevent_initial_call=True,
)
def toggle_notas(n_clicks, is_open):
    if not n_clicks:
        raise PreventUpdate
    return not is_open


@callback(
    Output("collapse-historico", "is_open"),
    Input("btn-toggle-historico", "n_clicks"),
    State("collapse-historico", "is_open"),
    prevent_initial_call=True,
)
def toggle_historico(n_clicks, is_open):
    if not n_clicks:
        raise PreventUpdate
    return not is_open
