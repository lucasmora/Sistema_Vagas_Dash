import dash
from dash import html, dcc, callback, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from models import criar_vaga, listar_portais, listar_tags, criar_tag
from components.forms import form_nova_vaga, form_editar_vaga
from styles import (
    COR_TEXTO, COR_TEXTO_SEC, COR_BORDA, COR_PRIMARY,
    COR_FUNDO, CARD_STYLE, input_style,
)


def layout() -> html.Div:
    return html.Div([
        html.H2("Nova Vaga", style={
            "color": COR_TEXTO, "fontWeight": 600, "marginBottom": "24px",
        }),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Formulário de Vaga", style={
                            "color": COR_TEXTO, "marginBottom": "20px", "fontWeight": 600,
                        }),
                        form_nova_vaga(),
                    ]),
                ], style={**CARD_STYLE}),
            ], width=12),
        ]),
    ])


@callback(
    Output("url", "href", allow_duplicate=True),
    Output("notification", "data", allow_duplicate=True),
    Input("btn-salvar-vaga", "n_clicks"),
    State("nova-vaga-nome", "value"),
    State("nova-vaga-empresa", "value"),
    State("nova-vaga-link", "value"),
    State("salario", "value"),
    State("salario-max", "value"),
    State("nova-vaga-modalidade", "value"),
    State("nova-vaga-portal", "value"),
    State("nova-vaga-data-encontrada", "date"),
    State("nova-vaga-data-envio", "date"),
    State("nova-vaga-interesse", "value"),
    State("nova-vaga-aderencia", "value"),
    State("nova-vaga-tags", "value"),
    State("nova-vaga-descricao", "value"),
    State("nova-vaga-notas", "value"),
    prevent_initial_call=True,
)
def salvar_vaga(n_clicks, nome, empresa, link, salario, salario_max, modalidade,
               portal, data_encontrada, data_envio, interesse, aderencia, tag_ids,
               descricao, notas):
    if not n_clicks:
        raise PreventUpdate
    
    nome = (nome or "").strip()
    if not nome:
        return no_update, {"message": "Nome é obrigatório", "type": "warning"}
    
    tag_ids = tag_ids or []
    try:
        vaga_id = criar_vaga(
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
        return f"/vagas/{vaga_id}", {"message": "Vaga criada com sucesso!", "type": "success"}
    except Exception as e:
        return no_update, {"message": f"Erro ao criar vaga: {str(e)}", "type": "danger"}


@callback(
    Output("nova-vaga-tags", "options"),
    Input("btn-add-tag-vaga", "n_clicks"),
    State("nova-vaga-nova-tag", "value"),
    prevent_initial_call=True,
)
def add_tag_na_vaga(n_clicks, nome):
    if not n_clicks:
        raise PreventUpdate
    nome = (nome or "").strip()
    if not nome:
        raise PreventUpdate
    criar_tag(nome)
    return [{"label": t["nome"], "value": t["id"]} for t in listar_tags()]