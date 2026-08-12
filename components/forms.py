from dash import html, dcc, callback, Input, Output, State
import dash_mantine_components as dmc

from styles import COR_TEXTO_SEC
from models import listar_portais, listar_tags

TIPO_SALARIO_OPCOES = [
    {"label": "Valor fixo", "value": "fixo"},
    {"label": "Faixa salarial", "value": "faixa"},
    {"label": "Não informado", "value": "nai"},
]

MODALIDADE_OPCOES = [
    {"label": m, "value": m}
    for m in ["Remoto", "Presencial", "Híbrido"]
]


def _text_input(ide: str, placeholder: str = "", value: str = ""):
    return dmc.TextInput(
        id=ide,
        placeholder=placeholder,
        value=value or "",
    )


def _number_input(ide: str, placeholder: str = "", value=None):
    return dmc.NumberInput(
        id=ide,
        placeholder=placeholder,
        value=value if value is not None else None,
        min=0,
        allowNegative=False,
    )


def _date_input(ide: str, value=None):
    return dmc.DateInput(
        id=ide,
        value=value or None,
        valueFormat="YYYY-MM-DD",
        clearable=True,
        placeholder="DD/MM/AAAA",
    )


def _select(ide: str, opcoes: list, placeholder: str = "Selecione...",
            value=None):
    return dmc.Select(
        id=ide,
        data=opcoes,
        placeholder=placeholder,
        clearable=True,
        allowDeselect=True,
        value=value or None,
    )


def _dropdown_multi(ide: str, opcoes: list, placeholder: str = "Selecione...",
                    value=None):
    return dmc.MultiSelect(
        id=ide,
        data=opcoes,
        placeholder=placeholder,
        clearable=True,
        value=value or [],
    )


def _slider_campo(label: str, ide: str, value):
    return html.Div([
        dmc.Text(label, size="sm", c="dimmed", mb=4),
        dmc.Slider(
            id=ide,
            min=1,
            max=5,
            step=1,
            value=value,
            marks=[{"value": i, "label": str(i)} for i in range(1, 6)],
            mb="xs",
        ),
    ])


def _col(span: int, children):
    return dmc.GridCol(span=span, children=children)


def modal_autofill_infojobs():
    """Modal para auto-preenchimento de vaga do InfoJobs"""
    return dmc.Modal(
        id="modal-autofill-infojobs",
        opened=False,
        title="🔍 Auto-preencher InfoJobs",
        centered=True,
        keepMounted=True,
        withCloseButton=True,
        children=[
            dmc.Text(
                "Cole o ID da vaga do InfoJobs (ex: 11616056):",
                size="sm",
                c="dimmed",
                mb="md",
            ),
            dmc.TextInput(
                id="autofill-infojobs-id",
                placeholder="11616056",
                mb="md",
            ),
            html.Div(
                id="autofill-infojobs-status",
                style={"color": COR_TEXTO_SEC, "fontSize": "0.875rem"},
            ),
            dmc.Group(
                justify="flex-end",
                mt="lg",
                children=[
                    dmc.Button(
                        "Cancelar",
                        id="btn-autofill-cancel",
                        variant="default",
                    ),
                    dmc.Button(
                        "Buscar e Preencher",
                        id="btn-autofill-fetch",
                        color="teal",
                        variant="filled",
                    ),
                ],
            ),
        ],
    )


def salario_inputs() -> html.Div:
    return html.Div(
        id="salario-area",
        children=[
            dmc.RadioGroup(
                id="salario-tipo",
                label="Tipo de Salário",
                value="nai",
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
            html.Div(id="salario-valores", children=[
                dmc.NumberInput(id="salario", label="Salário (R$)",
                                style={"display": "none"}),
                dmc.NumberInput(id="salario-max", label="Salário Máximo (R$)",
                                style={"display": "none"}),
            ]),
        ],
        style={"marginBottom": "16px"},
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

    if tipo == "nai":
        return [
            dmc.NumberInput(id="salario", label="Salário (R$)",
                            style={"display": "none"}),
            dmc.NumberInput(id="salario-max", label="Salário Máximo (R$)",
                            style={"display": "none"}),
        ]
    if tipo == "fixo":
        return [
            dmc.NumberInput(id="salario", label="Salário (R$)",
                            placeholder="Ex: 12000",
                            value=val if val is not None else None),
            dmc.NumberInput(id="salario-max", label="Salário Máximo (R$)",
                            style={"display": "none"}),
        ]
    return [
        dmc.NumberInput(id="salario", label="Salário Mínimo (R$)",
                        placeholder="Ex: 2000",
                        value=val if val is not None else None),
        dmc.NumberInput(id="salario-max", label="Salário Máximo (R$)",
                        placeholder="Ex: 20000",
                        value=val_max if val_max is not None else None),
    ]


def form_nova_vaga():
    portais = listar_portais()
    portal_opcoes = [
        {"label": p["nome"], "value": p["id"]} for p in portais
    ]
    tags_disponiveis = listar_tags()
    tag_opcoes = [{"label": t["nome"], "value": t["id"]} for t in tags_disponiveis]

    return dmc.Paper(
        p="xl",
        radius="md",
        shadow="sm",
        withBorder=True,
        style={"maxWidth": 800, "margin": "0 auto"},
        children=[
            dmc.Title("Nova Vaga", order=3, mb="lg"),
            dcc.Store(id="autofill-salary", data=None),
            dmc.Grid(
                gutter="md",
                children=[
                    _col(12, dmc.TextInput(
                        id="nova-vaga-nome",
                        label="Nome *",
                        placeholder="Ex: Gerente Financeiro - Stone",
                        withAsterisk=True,
                    )),
                    _col(6, dmc.TextInput(
                        id="nova-vaga-empresa",
                        label="Empresa",
                        placeholder="Ex: Stone Pagamentos",
                    )),
                    _col(6, dmc.TextInput(
                        id="nova-vaga-link",
                        label="Link",
                        placeholder="URL da vaga",
                    )),
                    _col(4, dmc.Select(
                        id="nova-vaga-modalidade",
                        label="Modalidade",
                        data=MODALIDADE_OPCOES,
                        placeholder="Selecione...",
                        clearable=True,
                    )),
                    _col(8, salario_inputs()),
                    _col(6, dmc.Select(
                        id="nova-vaga-portal",
                        label="Portal",
                        data=portal_opcoes,
                        placeholder="Selecione...",
                        clearable=True,
                    )),
                    _col(3, _date_input("nova-vaga-data-publicacao")),
                    _col(3, _date_input("nova-vaga-data-encontrada")),
                    _col(3, _date_input("nova-vaga-data-envio")),
                    _col(6, _slider_campo("Interesse", "nova-vaga-interesse", 3)),
                    _col(6, _slider_campo("Aderência", "nova-vaga-aderencia", 3)),
                    _col(12, dmc.MultiSelect(
                        id="nova-vaga-tags",
                        label="Tags",
                        data=tag_opcoes,
                        placeholder="Selecione...",
                        clearable=True,
                        hidePickedOptions=True,
                    )),
                    _col(12, dmc.Group(
                        gap="xs",
                        align="flex-end",
                        children=[
                            dmc.TextInput(
                                id="nova-vaga-nova-tag",
                                label="Nova Tag",
                                placeholder="Nome da tag",
                                style={"flex": 1},
                            ),
                            dmc.Button(
                                "Adicionar",
                                id="btn-add-tag-vaga",
                                variant="light",
                                color="teal",
                            ),
                        ],
                    )),
                    _col(12, dmc.Textarea(
                        id="nova-vaga-descricao",
                        label="Descrição",
                        placeholder="Texto completo do anúncio...",
                        autosize=True,
                        minRows=6,
                        resize="vertical",
                    )),
                    _col(12, dmc.Textarea(
                        id="nova-vaga-notas",
                        label="Notas",
                        placeholder="Anotações pessoais...",
                        autosize=True,
                        minRows=4,
                        resize="vertical",
                    )),
                ],
            ),
            dmc.Divider(my="xl"),
            dmc.Button(
                "Salvar Vaga",
                id="btn-salvar-vaga",
                color="teal",
                variant="filled",
                size="md",
                fullWidth=True,
            ),
            modal_autofill_infojobs(),
        ],
    )


def form_editar_vaga(vaga: dict):
    portais = listar_portais()
    portal_opcoes = [
        {"label": p["nome"], "value": p["id"]} for p in portais
    ]
    tags_disponiveis = listar_tags()
    tag_opcoes = [{"label": t["nome"], "value": t["id"]} for t in tags_disponiveis]

    return dmc.Paper(
        p="xl",
        radius="md",
        shadow="sm",
        withBorder=True,
        children=[
            dmc.Title(f"Editar: {vaga.get('nome', '')}", order=4, mb="lg"),
            dmc.Grid(
                gutter="md",
                children=[
                    _col(12, dmc.TextInput(
                        id="edit-vaga-nome",
                        label="Nome *",
                        value=vaga.get("nome", ""),
                        withAsterisk=True,
                    )),
                    _col(6, dmc.TextInput(
                        id="edit-vaga-empresa",
                        label="Empresa",
                        value=vaga.get("empresa") or "",
                    )),
                    _col(6, dmc.TextInput(
                        id="edit-vaga-link",
                        label="Link",
                        value=vaga.get("link") or "",
                    )),
                    _col(4, dmc.Select(
                        id="edit-vaga-modalidade",
                        label="Modalidade",
                        data=MODALIDADE_OPCOES,
                        placeholder="Selecione...",
                        clearable=True,
                        value=vaga.get("modalidade") or None,
                    )),
                    _col(4, dmc.NumberInput(
                        id="edit-vaga-salario",
                        label="Salário (R$)",
                        placeholder="Ex: 12000",
                        value=vaga.get("salario") or None,
                        min=0,
                        allowNegative=False,
                    )),
                    _col(4, dmc.NumberInput(
                        id="edit-vaga-salario-max",
                        label="Salário Máximo (R$)",
                        placeholder="Ex: 15000",
                        value=vaga.get("salario_max") or None,
                        min=0,
                        allowNegative=False,
                    )),
                    _col(6, dmc.Select(
                        id="edit-vaga-portal",
                        label="Portal",
                        data=portal_opcoes,
                        placeholder="Selecione...",
                        clearable=True,
                        value=vaga.get("portal_id") or None,
                    )),
                    _col(3, _date_input("edit-vaga-data-encontrada",
                                        value=vaga.get("data_encontrada") or None)),
                    _col(3, _date_input("edit-vaga-data-envio",
                                        value=vaga.get("data_envio") or None)),
                    _col(6, _slider_campo("Interesse", "edit-vaga-interesse",
                                          vaga.get("interesse") or 3)),
                    _col(6, _slider_campo("Aderência", "edit-vaga-aderencia",
                                          vaga.get("aderencia") or 3)),
                    _col(12, dmc.MultiSelect(
                        id="edit-vaga-tags",
                        label="Tags",
                        data=tag_opcoes,
                        placeholder="Selecione...",
                        clearable=True,
                        hidePickedOptions=True,
                    )),
                    _col(12, dmc.Textarea(
                        id="edit-vaga-descricao",
                        label="Descrição",
                        value=vaga.get("descricao") or "",
                        autosize=True,
                        minRows=6,
                        resize="vertical",
                    )),
                    _col(12, dmc.Textarea(
                        id="edit-vaga-notas",
                        label="Notas",
                        value=vaga.get("notas") or "",
                        autosize=True,
                        minRows=4,
                        resize="vertical",
                    )),
                ],
            ),
            dmc.Group(
                mt="xl",
                children=[
                    dmc.Button(
                        "Salvar alterações",
                        id="btn-salvar-edicao",
                        color="teal",
                        variant="filled",
                    ),
                    dmc.Button(
                        "Cancelar",
                        id="btn-cancelar-edicao",
                        variant="default",
                    ),
                ],
            ),
        ],
    )


def form_portal(portal: dict = None):
    editando = portal is not None
    return dmc.Paper(
        p="xl",
        radius="md",
        shadow="sm",
        withBorder=True,
        children=[
            dmc.Title(
                "Editar Portal" if editando else "Novo Portal",
                order=4,
                mb="lg",
            ),
            dmc.Stack(
                gap="md",
                children=[
                    dmc.TextInput(
                        id="form-portal-nome",
                        label="Nome",
                        placeholder="Ex: LinkedIn",
                        value=portal["nome"] if editando else "",
                    ),
                    dmc.TextInput(
                        id="form-portal-url",
                        label="URL Base",
                        placeholder="Ex: linkedin.com",
                        value=portal.get("url_base", "") if editando else "",
                    ),
                    dmc.TextInput(
                        id="form-portal-login",
                        label="Tipo de Login",
                        placeholder="Ex: e-mail",
                        value=portal.get("tipo_login", "") if editando else "",
                    ),
                    _date_input("form-portal-data",
                                value=portal.get("ultima_atualizacao", "") if editando else None),
                    dmc.Textarea(
                        id="form-portal-notas",
                        label="Notas",
                        placeholder="Observações sobre o portal...",
                        value=portal.get("notas", "") if editando else "",
                        autosize=True,
                        minRows=4,
                        resize="vertical",
                    ),
                ],
            ),
            dmc.Group(
                mt="lg",
                children=[
                    dmc.Button(
                        "Salvar Portal" if not editando else "Atualizar",
                        id="btn-salvar-portal",
                        color="teal",
                        variant="filled",
                    ),
                    dmc.Button(
                        "Cancelar",
                        id="btn-cancelar-edicao-portal",
                        variant="default",
                    ) if editando else None,
                ],
            ),
        ],
    )


def form_tag():
    return dmc.Paper(
        p="xl",
        radius="md",
        shadow="sm",
        withBorder=True,
        children=[
            dmc.Title("Nova Tag", order=4, mb="lg"),
            dmc.TextInput(
                id="form-tag-nome",
                label="Nome",
                placeholder="Ex: Python",
            ),
            dmc.Button(
                "Adicionar",
                id="btn-add-tag",
                color="teal",
                variant="filled",
                mt="lg",
            ),
        ],
    )
