from datetime import datetime, date
from dash import html, dcc, callback, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from models import criar_vaga, listar_portais, listar_tags, criar_tag, get_portal
from components.forms import form_nova_vaga, form_editar_vaga
from services.infojobs_parser import parse_vaga_infojobs_dict
from styles import (
    COR_TEXTO, COR_TEXTO_SEC, COR_BORDA_CLARA, COR_PRIMARY,
    COR_ALERTA, COR_PERIGO, COR_SUCESSO, CARD_STYLE, INPUT_STYLE,
)


def layout() -> html.Div:
    return html.Div([
        html.H2("Nova Vaga", style={
            "color": COR_TEXTO, "fontWeight": 600, "marginBottom": "24px",
        }),
        dcc.Store(id="autofill-source", data=None),
        dbc.Row([
            dbc.Col([
                form_nova_vaga(),
            ], width=12),
        ]),
    ])


@callback(
    Output("modal-autofill-infojobs", "is_open", allow_duplicate=True),
    Input("nova-vaga-portal", "value"),
    prevent_initial_call=True,
)
def abrir_modal_autofill(portal_id):
    """Abre modal se o portal selecionado for InfoJobs"""
    if not portal_id or portal_id == "":
        raise PreventUpdate
    portal = get_portal(int(portal_id))
    if portal and "infojobs" in portal.get("nome", "").lower():
        return True
    return False


@callback(
    Output("modal-autofill-infojobs", "is_open", allow_duplicate=True),
    Input("btn-autofill-cancel", "n_clicks"),
    prevent_initial_call=True,
)
def fechar_modal_autofill(n_clicks):
    """Fecha modal sem preencher"""
    if not n_clicks:
        raise PreventUpdate
    return False


@callback(
    Output("nova-vaga-nome", "value"),
    Output("nova-vaga-empresa", "value"),
    Output("nova-vaga-link", "value"),
    Output("salario-tipo", "value", allow_duplicate=True),
    Output("autofill-salary", "data"),
    Output("nova-vaga-modalidade", "value"),
    Output("nova-vaga-descricao", "value"),
    Output("nova-vaga-notas", "value"),
    Output("nova-vaga-data-encontrada", "date"),
    Output("nova-vaga-data-publicacao", "date"),
    Output("autofill-source", "data"),
    Output("modal-autofill-infojobs", "is_open", allow_duplicate=True),
    Output("autofill-infojobs-status", "children"),
    Input("btn-autofill-fetch", "n_clicks"),
    State("autofill-infojobs-id", "value"),
    prevent_initial_call=True,
)
def buscar_e_preencher(n_clicks, vaga_id):
    """Busca dados da vaga no InfoJobs e preenche o formulário"""
    if not n_clicks:
        raise PreventUpdate

    vaga_id = (vaga_id or "").strip()
    if not vaga_id:
        return (no_update,) * 11 + (html.Span("⚠️ Digite o ID da vaga",
                                                style={"color": COR_ALERTA}),)

    try:
        dados = parse_vaga_infojobs_dict(vaga_id)
    except Exception as e:
        return (no_update,) * 11 + (html.Span(f"❌ Erro na requisição: {str(e)}",
                                                style={"color": COR_PERIGO}),)

    if dados is None:
        return (no_update,) * 11 + (html.Span("❌ Vaga não encontrada ou JSON-LD ausente",
                                                style={"color": COR_PERIGO}),)

    # --- Salário: definir tipo e dados para o _condicional_salario ---
    salario_tipo = "nai"
    salario_store = None
    if dados.get("salario") and dados.get("salario_max"):
        salario_tipo = "faixa"
        salario_store = {"salario": float(dados["salario"]), "salario_max": float(dados["salario_max"])}
    elif dados.get("salario"):
        salario_tipo = "fixo"
        salario_store = {"salario": float(dados["salario"]), "salario_max": None}

    # --- Modalidade (normalizar) ---
    modalidade = dados.get("modalidade", "")
    modalidade_map = {
        "remoto": "Remoto", "presencial": "Presencial",
        "hibrido": "Híbrido", "híbrido": "Híbrido",
    }
    modalidade = modalidade_map.get(modalidade.lower(), modalidade)

    # --- Datas ---
    hoje = date.today().isoformat()
    data_publicacao = dados.get("data_publicacao", "")

    # --- Store com dados extras para o salvar ---
    fonte_data = {
        "fonte_id": dados.get("fonte_id", ""),
        "data_publicacao": data_publicacao,
    }

    return (
        dados.get("nome", ""),          # nova-vaga-nome
        dados.get("empresa", ""),       # nova-vaga-empresa
        dados.get("link", ""),          # nova-vaga-link
        salario_tipo,                   # salario-tipo (radio)
        salario_store,                  # autofill-salary (store)
        modalidade,                     # nova-vaga-modalidade
        dados.get("descricao", ""),     # nova-vaga-descricao
        dados.get("notas", ""),         # nova-vaga-notas
        hoje,                           # nova-vaga-data-encontrada (HOJE)
        data_publicacao,                # nova-vaga-data-publicacao
        fonte_data,                     # autofill-source (store)
        False,                          # modal is_open (fechar)
        html.Span("✅ Vaga preenchida com sucesso!",
                  style={"color": COR_SUCESSO, "fontWeight": 600}),
    )


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
    State("nova-vaga-data-publicacao", "date"),
    State("autofill-source", "data"),
    prevent_initial_call=True,
)
def salvar_vaga(n_clicks, nome, empresa, link, salario, salario_max, modalidade,
               portal, data_encontrada, data_envio, interesse, aderencia, tag_ids,
               descricao, notas, data_publicacao, fonte_data):
    if not n_clicks:
        raise PreventUpdate
    
    nome = (nome or "").strip()
    if not nome:
        return no_update, {"message": "Nome é obrigatório", "type": "warning"}
    
    tag_ids = tag_ids or []
    fonte_id = ""
    if fonte_data and isinstance(fonte_data, dict):
        if not data_publicacao:
            data_publicacao = fonte_data.get("data_publicacao", "")
        fonte_id = fonte_data.get("fonte_id", "")
    
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
            data_publicacao=data_publicacao or "",
            fonte_id=fonte_id,
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
