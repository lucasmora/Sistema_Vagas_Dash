import plotly.express as px
import pandas as pd

from models import vagas_por_status, curriculos_por_dia, vagas_por_portal
from styles import COR_TEXTO, COR_TEXTO_SEC, COR_TEXTO_MUTED, COR_BORDA_CLARA, COR_SUPERFICIE, STATUS_CORES, COR_PRIMARY, COR_DESTAQUE


def _tema_dark(fig) -> None:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "IBM Plex Sans", "color": COR_TEXTO_SEC, "size": 12},
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(font={"color": COR_TEXTO_SEC}),
    )
    fig.update_xaxes(
        gridcolor=COR_BORDA_CLARA, zerolinecolor=COR_BORDA_CLARA,
        tickfont={"color": COR_TEXTO_MUTED, "family": "IBM Plex Sans"},
    )
    fig.update_yaxes(
        gridcolor=COR_BORDA_CLARA, zerolinecolor=COR_BORDA_CLARA,
        tickfont={"color": COR_TEXTO_MUTED, "family": "IBM Plex Sans"},
    )


def fig_pizza_status():
    dados = vagas_por_status()
    if not dados:
        fig = px.pie(title="Vagas por Status", template="plotly_dark")
        fig.update_layout(
            annotations=[dict(text="Nenhum dado", showarrow=False,
                              font={"color": COR_TEXTO_SEC})]
        )
        _tema_dark(fig)
        return fig
    df = pd.DataFrame(dados)
    cores = [STATUS_CORES.get(s, COR_BORDA_CLARA) for s in df["status"]]
    fig = px.pie(
        df, names="status", values="qtd",
        color_discrete_sequence=cores,
        hole=0.4,
        template="plotly_dark",
    )
    fig.update_traces(
        textposition="inside", textinfo="label+percent",
        marker=dict(line=dict(color=COR_SUPERFICIE, width=2)),
        textfont=dict(color=COR_TEXTO),
    )
    _tema_dark(fig)
    return fig


def fig_barras_curriculos():
    dados = curriculos_por_dia()
    if not dados:
        fig = px.bar(title="Currículos Enviados por Dia", template="plotly_dark")
        fig.update_layout(
            annotations=[dict(text="Nenhum dado", showarrow=False,
                              font={"color": COR_TEXTO_SEC})]
        )
        _tema_dark(fig)
        return fig
    df = pd.DataFrame(dados)
    fig = px.bar(
        df, x="data_envio", y="qtd",
        labels={"data_envio": "Data", "qtd": "Currículos"},
        color_discrete_sequence=[COR_PRIMARY],
        template="plotly_dark",
    )
    fig.update_traces(marker=dict(line=dict(color=COR_PRIMARY, width=0)))
    _tema_dark(fig)
    return fig


def fig_barras_portais():
    dados = vagas_por_portal()
    if not dados:
        fig = px.bar(title="Vagas por Portal", template="plotly_dark")
        fig.update_layout(
            annotations=[dict(text="Nenhum dado", showarrow=False,
                              font={"color": COR_TEXTO_SEC})]
        )
        _tema_dark(fig)
        return fig
    df = pd.DataFrame(dados)
    fig = px.bar(
        df, x="qtd", y="portal", orientation="h",
        labels={"qtd": "Vagas", "portal": "Portal"},
        color_discrete_sequence=[COR_DESTAQUE],
        template="plotly_dark",
    )
    fig.update_traces(marker=dict(line=dict(color=COR_DESTAQUE, width=0)))
    _tema_dark(fig)
    fig.update_yaxes(autorange="reversed")
    return fig
