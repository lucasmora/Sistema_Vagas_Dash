import plotly.express as px
import pandas as pd

from models import vagas_por_status, curriculos_por_dia, vagas_por_portal
from styles import COR_FUNDO, COR_TEXTO, COR_BORDA, STATUS_CORES


def _tema_escuro(fig) -> None:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": COR_TEXTO, "size": 12},
        margin=dict(l=20, r=20, t=30, b=20),
    )
    fig.update_xaxes(
        gridcolor=COR_BORDA, zerolinecolor=COR_BORDA,
        tickfont={"color": COR_TEXTO},
    )
    fig.update_yaxes(
        gridcolor=COR_BORDA, zerolinecolor=COR_BORDA,
        tickfont={"color": COR_TEXTO},
    )


def fig_pizza_status():
    dados = vagas_por_status()
    if not dados:
        return px.pie(title="Vagas por Status").update_layout(
            annotations=[dict(text="Nenhum dado", showarrow=False,
                              font={"color": COR_TEXTO})]
        )
    df = pd.DataFrame(dados)
    cores = [STATUS_CORES.get(s, COR_BORDA) for s in df["status"]]
    fig = px.pie(
        df, names="status", values="qtd",
        color_discrete_sequence=cores,
        hole=0.4,
    )
    fig.update_traces(
        textposition="inside", textinfo="label+percent",
        marker=dict(line=dict(color=COR_FUNDO, width=2)),
    )
    _tema_escuro(fig)
    return fig


def fig_barras_curriculos():
    dados = curriculos_por_dia()
    if not dados:
        return px.bar(title="Currículos Enviados por Dia").update_layout(
            annotations=[dict(text="Nenhum dado", showarrow=False,
                              font={"color": COR_TEXTO})]
        )
    df = pd.DataFrame(dados)
    fig = px.bar(
        df, x="data_envio", y="qtd",
        labels={"data_envio": "Data", "qtd": "Currículos"},
        color_discrete_sequence=["#00BFA6"],
    )
    fig.update_traces(marker=dict(line=dict(color="#00BFA6", width=0)))
    _tema_escuro(fig)
    return fig


def fig_barras_portais():
    dados = vagas_por_portal()
    if not dados:
        return px.bar(title="Vagas por Portal").update_layout(
            annotations=[dict(text="Nenhum dado", showarrow=False,
                              font={"color": COR_TEXTO})]
        )
    df = pd.DataFrame(dados)
    fig = px.bar(
        df, x="qtd", y="portal", orientation="h",
        labels={"qtd": "Vagas", "portal": "Portal"},
        color_discrete_sequence=["#6C63FF"],
    )
    fig.update_traces(marker=dict(line=dict(color="#6C63FF", width=0)))
    _tema_escuro(fig)
    fig.update_yaxes(autorange="reversed")
    return fig
