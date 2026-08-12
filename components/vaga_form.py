from datetime import date
from dash import html, callback, Input, Output, State, no_update
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from components.forms import (
    modal_autofill_infojobs, iso_para_br, br_para_iso,
    _date_input, _col, _slider_campo,
)
from db.models import (
    criar_vaga, criar_tag, get_portal, get_vaga,
    atualizar_vaga, listar_portais, listar_tags,
)
from services.infojobs_parser import parse_vaga_infojobs_dict
from styles import (
    COR_ALERTA, COR_PERIGO, COR_SUCESSO
)

MODALIDADE_OPCOES = [
    {"label": m, "value": m}
    for m in ["Remoto", "Presencial", "Híbrido"]
]

SALARIO_MASK = {
    "prefix": "R$ ",
    "thousandSeparator": ".",
    "decimalSeparator": ",",
    "decimalScale": 0,
}


def _derivar_tipo_salario(salario, salario_max):
    if salario and salario_max:
        return "faixa"
    if salario:
        return "fixo"
    return "nai"


def _salario_valores(tipo: str, salario=None, salario_max=None):
    if tipo == "nai":
        return [
            dmc.NumberInput(id="salario", label="Salário (R$)",
                            **SALARIO_MASK,
                            style={"display": "none"}),
            dmc.NumberInput(id="salario-max", label="Salário Máximo (R$)",
                            **SALARIO_MASK,
                            style={"display": "none"}),
        ]
    if tipo == "fixo":
        return [
            dmc.NumberInput(id="salario", label="Salário (R$)",
                            placeholder="Ex: 12000",
                            value=salario if salario is not None else None,
                            **SALARIO_MASK),
            dmc.NumberInput(id="salario-max", label="Salário Máximo (R$)",
                            **SALARIO_MASK,
                            style={"display": "none"}),
        ]
    return [
        dmc.NumberInput(id="salario", label="Salário Mínimo (R$)",
                        placeholder="Ex: 2000",
                        value=salario if salario is not None else None,
                        **SALARIO_MASK),
        dmc.NumberInput(id="salario-max", label="Salário Máximo (R$)",
                        placeholder="Ex: 20000",
                        value=salario_max if salario_max is not None else None,
                        **SALARIO_MASK),
    ]


def salario_inputs(tipo: str = "nai", salario=None, salario_max=None) -> html.Div:
    return html.Div(
        id="salario-area",
        children=[
            dmc.RadioGroup(
                id="salario-tipo",
                label="Tipo de Salário",
                value=tipo,
                children=dmc.Group(
                    gap="lg",
                    mt="xs",
                    children=[
                        dmc.Radio(label="Valor fixo", value="fixo"),
                        dmc.Radio(label="Faixa salarial", value="faixa"),
                        dmc.Radio(label="Não informado", value="nai"),
                    ],
                ),
            ),
            html.Div(
                id="salario-valores",
                children=_salario_valores(tipo, salario, salario_max),
            ),
        ],
        style={"marginBottom": "16px"},
    )


def form_vaga(vaga: dict = None):
    """Formulário único para criar (vaga=None) ou editar vaga.

    Usa IDs fixos e compartilhados; quando `vaga` é passado, pré-preenche
    todos os campos com os valores atuais."""
    editando = vaga is not None
    portais = listar_portais()
    portal_opcoes = [
        {"label": p["nome"], "value": str(p["id"])} for p in portais
    ]
    tags_disponiveis = listar_tags()

    salario = vaga.get("salario") if editando else None
    salario_max = vaga.get("salario_max") if editando else None
    salario_tipo = (
        _derivar_tipo_salario(salario, salario_max) if editando else "nai"
    )

    tags_value = (
        [t["nome"] for t in vaga.get("_tags", [])
         if isinstance(t, dict) and t.get("nome")]
        if editando else []
    )

    def valor(campo, default=""):
        if not editando:
            return default
        return vaga.get(campo) or default

    if editando:
        titulo = dmc.Title(f"Editar: {valor('nome')}", order=4, mb="lg")
    else:
        titulo = dmc.Title("Nova Vaga", order=3, mb="lg")

    grid_children = [
        _col(12, dmc.TextInput(
            id="vaga-nome",
            label="Nome",
            placeholder="Ex: Gerente Financeiro - Stone",
            value=valor("nome"),
            withAsterisk=True,
        )),
        _col(6, dmc.TextInput(
            id="vaga-empresa",
            label="Empresa",
            placeholder="Ex: Stone Pagamentos",
            value=valor("empresa"),
        )),
        _col(6, dmc.TextInput(
            id="vaga-link",
            label="Link",
            placeholder="URL da vaga",
            value=valor("link"),
        )),
        _col(4, dmc.Select(
            id="vaga-modalidade",
            label="Modalidade",
            data=MODALIDADE_OPCOES,
            placeholder="Selecione...",
            clearable=True,
            value=vaga.get("modalidade") or None if editando else None,
        )),
        _col(8, salario_inputs(salario_tipo, salario, salario_max)),
        _col(6, dmc.Select(
            id="vaga-portal",
            label="Portal",
            data=portal_opcoes,
            placeholder="Selecione...",
            clearable=True,
            value=str(vaga["portal_id"]) if editando and vaga.get("portal_id") else None,
        )),
        _col(3, _date_input("vaga-data-publicacao", label="Data de Publicação",
                            value=vaga.get("data_publicacao") if editando else None)),
        _col(3, _date_input("vaga-data-encontrada", label="Data Encontrada",
                            value=vaga.get("data_encontrada") if editando else None)),
        _col(3, _date_input("vaga-data-envio", label="Data de Envio",
                            value=vaga.get("data_envio") if editando else None)),
        _col(6, _slider_campo("Interesse", "vaga-interesse",
                              (vaga.get("interesse") or 3) if editando else 3)),
        _col(6, _slider_campo("Aderência", "vaga-aderencia",
                              (vaga.get("aderencia") or 3) if editando else 3)),
        _col(12, dmc.TagsInput(
            id="vaga-tags",
            label="Tags",
            data=[t["nome"] for t in tags_disponiveis],
            value=tags_value,
            placeholder="Digite e pressione Enter para criar",
            splitChars=[","],
            clearable=True,
        )),
        _col(12, dmc.Textarea(
            id="vaga-descricao",
            label="Descrição",
            placeholder="Texto completo do anúncio...",
            value=valor("descricao"),
            autosize=True,
            minRows=6,
            resize="vertical",
        )),
        _col(12, dmc.Textarea(
            id="vaga-notas",
            label="Notas",
            placeholder="Anotações pessoais...",
            value=valor("notas"),
            autosize=True,
            minRows=4,
            resize="vertical",
        )),
    ]

    if editando:
        acoes = dmc.Group(
            mt="xl",
            children=[
                dmc.Button(
                    "Salvar alterações",
                    id="btn-salvar-vaga",
                    color="teal",
                    variant="filled",
                ),
                dmc.Button(
                    "Cancelar",
                    id="btn-cancelar-edicao",
                    variant="default",
                ),
            ],
        )
    else:
        acoes = dmc.Button(
            "Salvar Vaga",
            id="btn-salvar-vaga",
            color="teal",
            variant="filled",
            size="md",
            fullWidth=True,
        )

    return dmc.Paper(
        p="xl",
        radius="md",
        shadow="sm",
        withBorder=True,
        style={"maxWidth": 800, "margin": "0 auto"},
        children=[
            titulo,
            dmc.Grid(gutter="md", children=grid_children),
            dmc.Divider(my="xl"),
            acoes,
            modal_autofill_infojobs(),
        ],
    )


@callback(
    Output("salario-valores", "children", allow_duplicate=True),
    Input("salario-tipo", "value"),
    State("autofill-salary", "data"),
    prevent_initial_call=True,
)
def _condicional_salario(tipo: str, autofill_data):
    """Atualiza visibilidade e valores dos inputs de salário"""
    val = None
    val_max = None
    if autofill_data and isinstance(autofill_data, dict):
        val = autofill_data.get("salario")
        val_max = autofill_data.get("salario_max")
    return _salario_valores(tipo, val, val_max)


@callback(
    Output("modal-autofill-infojobs", "opened", allow_duplicate=True),
    Input("vaga-portal", "value"),
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
    Output("modal-autofill-infojobs", "opened", allow_duplicate=True),
    Input("btn-autofill-cancel", "n_clicks"),
    prevent_initial_call=True,
)
def fechar_modal_autofill(n_clicks):
    """Fecha modal sem preencher"""
    if not n_clicks:
        raise PreventUpdate
    return False


@callback(
    Output("vaga-nome", "value"),
    Output("vaga-empresa", "value"),
    Output("vaga-link", "value"),
    Output("salario-tipo", "value", allow_duplicate=True),
    Output("autofill-salary", "data"),
    Output("vaga-modalidade", "value"),
    Output("vaga-descricao", "value"),
    Output("vaga-notas", "value"),
    Output("vaga-data-encontrada", "value"),
    Output("vaga-data-publicacao", "value"),
    Output("autofill-source", "data"),
    Output("modal-autofill-infojobs", "opened", allow_duplicate=True),
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
        return (no_update,) * 12 + (html.Span("⚠️ Digite o ID da vaga",
                                                style={"color": COR_ALERTA}),)

    try:
        dados = parse_vaga_infojobs_dict(vaga_id)
    except Exception as e:
        return (no_update,) * 12 + (html.Span(f"❌ Erro na requisição: {str(e)}",
                                                style={"color": COR_PERIGO}),)

    if dados is None:
        return (no_update,) * 12 + (html.Span("❌ Vaga não encontrada ou JSON-LD ausente",
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
        dados.get("nome", ""),          # vaga-nome
        dados.get("empresa", ""),       # vaga-empresa
        dados.get("link", ""),          # vaga-link
        salario_tipo,                   # salario-tipo (radio)
        salario_store,                  # autofill-salary (store)
        modalidade,                     # vaga-modalidade
        dados.get("descricao", ""),     # vaga-descricao
        dados.get("notas", ""),         # vaga-notas
        iso_para_br(hoje),              # vaga-data-encontrada (HOJE)
        iso_para_br(data_publicacao),   # vaga-data-publicacao
        fonte_data,                     # autofill-source (store)
        False,                          # modal opened (fechar)
        html.Span("✅ Vaga preenchida com sucesso!",
                  style={"color": COR_SUCESSO, "fontWeight": 600}),
    )


@callback(
    Output("notification", "data", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Output("form-saved-event", "data", allow_duplicate=True),
    Input("btn-salvar-vaga", "n_clicks"),
    State("vaga-form-mode", "data"),
    State("form-saved-event", "data"),
    State("vaga-nome", "value"),
    State("vaga-empresa", "value"),
    State("vaga-link", "value"),
    State("salario", "value"),
    State("salario-max", "value"),
    State("vaga-modalidade", "value"),
    State("vaga-portal", "value"),
    State("vaga-data-encontrada", "value"),
    State("vaga-data-envio", "value"),
    State("vaga-interesse", "value"),
    State("vaga-aderencia", "value"),
    State("vaga-tags", "value"),
    State("vaga-descricao", "value"),
    State("vaga-notas", "value"),
    State("vaga-data-publicacao", "value"),
    State("autofill-source", "data"),
    prevent_initial_call=True,
)
def salvar_vaga(n_clicks, modo_data, evento, nome, empresa, link, salario,
                salario_max, modalidade, portal, data_encontrada, data_envio,
                interesse, aderencia, tag_ids, descricao, notas, data_publicacao,
                fonte_data):
    """Cria ou atualiza a vaga conforme o modo guardado em vaga-form-mode"""
    if not n_clicks:
        raise PreventUpdate

    modo = (modo_data or {}).get("modo", "nova")
    vaga_id = (modo_data or {}).get("id") if modo == "editar" else None

    nome = (nome or "").strip()
    if not nome:
        return {"message": "Nome é obrigatório", "type": "warning"}, no_update, no_update

    tag_ids = tag_ids or []
    tag_ids_ok = []
    for tag_nome in tag_ids:
        tag_nome = str(tag_nome or "").strip().lower()
        if not tag_nome:
            continue
        tid = criar_tag(tag_nome)
        if tid:
            tag_ids_ok.append(tid)

    fonte_id = ""
    if fonte_data and isinstance(fonte_data, dict):
        if not data_publicacao:
            data_publicacao = fonte_data.get("data_publicacao", "")
        fonte_id = fonte_data.get("fonte_id", "")

    campos = dict(
        nome=nome,
        empresa=empresa or "",
        link=link or "",
        salario=float(salario) if salario else None,
        salario_max=float(salario_max) if salario_max else None,
        modalidade=modalidade or "",
        descricao=descricao or "",
        interesse=int(interesse) if interesse else 3,
        aderencia=int(aderencia) if aderencia else 3,
        portal_id=int(portal) if portal and portal != "" else None,
        data_encontrada=br_para_iso(data_encontrada),
        data_envio=br_para_iso(data_envio),
        notas=notas or "",
        tag_ids=tag_ids_ok or None,
        data_publicacao=br_para_iso(data_publicacao),
        fonte_id=fonte_id,
    )

    try:
        if modo == "editar" and vaga_id:
            vaga_atual = get_vaga(vaga_id)
            if not vaga_atual:
                return {"message": "Vaga não encontrada", "type": "danger"}, no_update, no_update
            campos["data_publicacao"] = (
                campos["data_publicacao"] or vaga_atual.get("data_publicacao") or ""
            )
            campos["fonte_id"] = fonte_id or vaga_atual.get("fonte_id") or ""
            campos["status"] = vaga_atual.get("status") or "Interessado"
            atualizar_vaga(vaga_id, **campos)
            return (
                {"message": "Vaga atualizada com sucesso!", "type": "success"},
                no_update,
                (evento or 0) + 1,
            )

        campos["status"] = "Interessado"
        criar_vaga(**campos)
        return {"message": "Vaga criada com sucesso!", "type": "success"}, "/vagas", no_update
    except Exception as e:
        return {"message": f"Erro ao salvar vaga: {str(e)}", "type": "danger"}, no_update, no_update