from datetime import datetime
from dash import html
import dash_mantine_components as dmc

from styles import COR_TEXTO_SEC


def iso_para_br(value):
    """Converte data ISO (YYYY-MM-DD) ou objeto date para DD/MM/YYYY.
    Se o valor já estiver em outro formato, devolve-o intacto."""
    if not value:
        return None
    texto = str(value).strip()
    if len(texto) >= 10:
        try:
            return datetime.strptime(texto[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            pass
    return texto


def br_para_iso(value):
    """Converte data DD/MM/YYYY para ISO (YYYY-MM-DD).
    Se o valor já estiver em outro formato, devolve-o intacto."""
    if not value:
        return ""
    texto = str(value).strip()
    if len(texto) >= 10:
        try:
            return datetime.strptime(texto[:10], "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            pass
    return texto


def _date_input(ide: str, label: str = None, value=None):
    return dmc.DateInput(
        id=ide,
        label=label,
        value=iso_para_br(value) if value else None,
        valueFormat="DD/MM/YYYY",
        clearable=True,
        placeholder="DD/MM/AAAA",
    )


def _slider_campo(label: str, ide: str, value):
    return html.Div([
        dmc.Text(label, size="sm", c="dimmed", mb=4, fw=600),
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
                        withAsterisk=True,
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
                                label="Última Atualização",
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


def form_tag(nome: str = "", tag_id=None):
    editando = tag_id is not None
    return dmc.Paper(
        p="xl",
        radius="md",
        shadow="sm",
        withBorder=True,
        children=[
            dmc.Title(
                "Editar Tag" if editando else "Nova Tag",
                order=4,
                mb="lg",
            ),
            dmc.Stack(
                gap="md",
                children=[
                    dmc.TextInput(
                        id="form-tag-nome",
                        label="Nome",
                        placeholder="Ex: Python",
                        value=nome,
                    ),
                    dmc.Text(
                        "As tags são salvas em letras minúsculas.",
                        size="xs",
                        c="dimmed",
                    ),
                ],
            ),
            dmc.Group(
                mt="lg",
                children=[
                    dmc.Button(
                        "Atualizar" if editando else "Adicionar",
                        id="btn-add-tag",
                        color="teal",
                        variant="filled",
                    ),
                    dmc.Button(
                        "Cancelar",
                        id="btn-cancelar-edicao-tag",
                        variant="default",
                    ) if editando else None,
                ],
            ),
        ],
    )
