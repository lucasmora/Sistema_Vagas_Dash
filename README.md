<div align="center">

# 💼 Sistema de Vagas Dash

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Dash](https://img.shields.io/badge/Dash-3.0%2B-1f77b4?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?style=flat-square&logo=docker&logoColor=white)
![Licença](https://img.shields.io/badge/Licen%C3%A7a-MIT-22c55e?style=flat-square)
![Versão](https://img.shields.io/badge/Vers%C3%A3o-1.0.0-blue?style=flat-square)

</div>

**Descrição**
-------------
Dashboard web em **Python (Dash/Plotly/Dash Mantine Components)** para gerenciar candidaturas a vagas de emprego. Permite cadastrar vagas, acompanhar pipeline de seleção, importar dados do **InfoJobs** via parser customizado (JSON-LD + regex, sem BeautifulSoup), e visualizar métricas/gráficos.

**Objetivo**
-----------
Centralizar o acompanhamento de candidaturas em um só lugar: cadastro manual + importação automática do InfoJobs, organização por portais/tags, pipeline Kanban (Interessado → Currículo Enviado → Entrevista Agendada → Em Processo → Oferta → Aceito · Rejeitado terminal), dashboard com métricas e gráficos.

**Stack Tecnológico**
--------------------
| Camada | Tecnologia |
|--------|------------|
| **Web Framework** | Dash ≥ 3.0 + Dash Mantine Components 2.x |
| **Visualização** | Plotly 5.x |
| **Dados** | SQLite (via `sqlite3` stdlib) + SQL raw |
| **Parser InfoJobs** | `httpx` + `regex` + `json` (stdlib) |
| **Container** | Docker (Python 3.11 slim) + docker compose |
| **UI/Estilo** | Dark mode Mantine (`MantineProvider` + `index_string`), fontes IBM Plex Sans + JetBrains Mono |

**Estrutura do Projeto**
-----------------------
```
Sistema_Vagas_Dash/
├── app.py                 # Entry point Dash + layout global + routing + notificações
├── db/database.py            # SQLite schema + connection context manager + migrations
├── db/models.py              # CRUD: portais, vagas, tags, histórico de status
├── styles.py              # Design system (tokens Mantine, spacing, status colors)
├── requirements.txt       # Dependências Python
├── Dockerfile / docker-compose.yml
├── pages/                 # Páginas (rotas Dash)
│   ├── dashboard.py       # Métricas + gráficos (pizza, barras)
│   ├── vagas.py           # Lista com filtros (status, portal, tag, busca)
│   ├── nova_vaga.py       # Monta o formulário de vaga (form_vaga)
│   ├── detalhe_vaga.py    # Detalhe + pipeline Kanban + histórico + editar/excluir
│   ├── portais.py         # CRUD portais
│   └── tags.py            # CRUD tags
├── components/
│   ├── cards.py           # vaga_card
│   ├── charts.py          # Plotly figures (pizza status, barras currículos/portais)
│   ├── forms.py           # Formulários (portal, tag), helpers de input, modal autofill InfoJobs
│   ├── vaga_form.py       # Formulário único de vaga (criar/editar) + callbacks salvar/autofill
│   ├── layout.py          # metric_card
│   ├── navbar.py          # Sidebar + navegação
│   └── pipeline.py        # Componente visual Kanban pipeline
└── services/
    └── infojobs_parser.py # Parser assíncrono InfoJobs (JSON-LD + regex HTML)
```

**Modelo de Dados (SQLite)**
---------------------------
| Tabela | Descrição |
|--------|-----------|
| `portais` | Portais de emprego (InfoJobs, LinkedIn, etc.) |
| `vagas` | Vagas com nome, empresa, link, salário, salário_max, modalidade, descrição, interesse (1-5), aderência (1-5), status, portal, datas (encontrada/envio/publicação), notas, fonte_id, timestamps (created_at/updated_at) |
| `tags` | Tags livres para categorização |
| `vaga_tags` | N:N vagas ↔ tags |
| `historico_status` | Log automático de mudanças de status (trigger SQLite) |

**Status válidos:** `Interessado`, `Currículo Enviado`, `Entrevista Agendada`, `Em Processo`, `Oferta`, `Aceito`, `Rejeitado`

**Como Rodar**
-------------
### Local (Python 3.11+)
```bash
pip install -r requirements.txt
python app.py
# Acesse http://localhost:8050
```

### Docker
```bash
docker compose up --build
# ou
docker build -t vagas-dash .
docker run -p 8050:8050 -e DB_PATH=/app/data/vagas.db -v vagas_db:/app/data vagas-dash
```

> O banco é persistido via volume Docker `vagas_db` (mapeado em `/app/data/`).

**Funcionalidades Principais**
-----------------------------
| Página | Funcionalidades |
|--------|-----------------|
| **Dashboard** | 4 cards de métricas + 3 gráficos Plotly (pizza status, barras currículos/dia, barras por portal) |
| **Vagas** | Lista em cards com filtros laterais (status multi-check, portal dropdown, tag dropdown, busca texto) — exclusão feita na página de detalhe |
| **Nova Vaga** | Formulário completo com sliders de interesse/aderência, tipo de salário (fixo/faixa/não informado), tags inline, + **modal autofill InfoJobs** (cola ID → parser JSON-LD + HTML → pré-preenche tudo) |
| **Detalhe Vaga** | Visualização completa + pipeline Kanban + histórico de status + editar/excluir |
| **Portais** | CRUD lateral (lista à esquerda, form à direita) |
| **Tags** | CRUD simples + criação rápida inline no formulário de vaga |

**Parser InfoJobs** (`services/infojobs_parser.py`)
--------------------------------------------------
- **Zero dependências pesadas** — só `httpx`, `re`, `json`, `html` (stdlib)
- **2 requests paralelos** (asyncio): página da vaga + aba "Empresa"
- **Extração principal**: JSON-LD `schema.org/JobPosting` (dados estruturados confiáveis)
- **Complementos via regex mínimo**: modalidade, salário bruto, listas (exigências, valorizado, benefícios), habilidades/tags, detalhes da empresa
- Retorna `dict` pronto para `db.models.criar_vaga()` + extras organizados em `extras{}`

**Variáveis de Ambiente**
------------------------
| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DB_PATH` | `vagas.db` | Caminho do arquivo SQLite |

**Dependências Principais** (`requirements.txt`)
------------------------------------------------
```
dash>=3.0.4
dash-mantine-components>=2.0.0
plotly>=5.24.1
pandas>=2.2.2
httpx>=0.27.0
```

**Design System (Resumo)**
--------------------------
- **Tema**: Dark mode via `dmc.MantineProvider` (theme teal), cores via CSS variables do Mantine (`var(--mantine-*)` em `styles.py`)
- **Cores semânticas**: `COR_PRIMARY` = filled teal, `COR_DESTAQUE` = violet-5, `COR_SUCESSO` = teal-5, `COR_ALERTA` = yellow-6, `COR_PERIGO` = red-6
- **Status colors**: Mapeamento fixo hex por status (`STATUS_CORES` em `styles.py`) — usado em badges, pipeline, gráficos
- **Tipografia**: IBM Plex Sans (UI) + JetBrains Mono (code/data)
- **Espaçamento**: Sistema 4px base (xs=4, sm=8, md=16, lg=24, xl=32)
- **Componentes**: Cards elevados (Paper), inputs dark, badges pill, tags, pipeline steps

**Licença**
----------
MIT. Sinta-se livre para usar, modificar e distribuir, contanto que essa licença seja mantida.

**Como este projeto foi desenvolvido**
--------------------------------------
- Definição dos requisitos e funcionalidades por mim.
- Desenvolvimento assistido por agentes e ferramentas de IA.
- Revisão e adaptação manual de todo o código gerado.
- Testes e validação das funcionalidades.
- Documentação escrita e mantida por mim.

**Versões/Alterações**
---------------------
- **1.0.0** – Versão inicial: dashboard de métricas, CRUD de vagas/portais/tags, pipeline Kanban, parser InfoJobs e empacotamento Docker.
