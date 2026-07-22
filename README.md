# Sistema de Vagas Dash

Dashboard web em **Python (Dash/Plotly/Dash Bootstrap Components)** para gerenciar candidaturas a vagas de emprego. Permite cadastrar vagas, acompanhar pipeline de seleção, importar dados do **InfoJobs** via parser customizado (JSON-LD + regex, sem BeautifulSoup), e visualizar métricas/gráficos.

---

## 🎯 Objetivo

Centralizar o acompanhamento de candidaturas em um só lugar: cadastro manual + importação automática do InfoJobs, organização por portais/tags, pipeline Kanban (Interessado → Currículo Enviado → Entrevista Agendada → Em Processo → Oferta → Aceito · Rejeitado terminal), dashboard com métricas e gráficos.

---

## 🛠 Stack Tecnológico

| Camada | Tecnologia |
|--------|------------|
| **Web Framework** | Dash ≥ 3.0 + Dash Bootstrap Components 2.x |
| **Visualização** | Plotly 5.x |
| **Dados** | SQLite (via `sqlite3` stdlib) + SQL raw |
| **Parser InfoJobs** | `httpx` + `regex` + `json` (stdlib) — **sem BeautifulSoup** |
| **Container** | Docker (Python 3.11 slim) + docker compose |
| **UI/Estilo** | Dark mode custom (CSS inline + `index_string`), fontes IBM Plex Sans + JetBrains Mono |

---

## 📁 Estrutura do Projeto

```
Sistema_Vagas_Dash/
├── app.py                 # Entry point Dash + layout global + routing
├── database.py            # SQLite schema + connection pool + migrations
├── models.py              # CRUD: portais, vagas, tags, histórico de status
├── styles.py              # Design system (cores, spacing, shadows, componentes)
├── requirements.txt       # Dependências Python
├── Dockerfile / docker-compose.yml
├── pages/                 # Páginas (rotas Dash)
│   ├── dashboard.py       # Métricas + gráficos (pizza, barras)
│   ├── vagas.py           # Lista com filtros (status, portal, tag, busca)
│   ├── nova_vaga.py       # Formulário + parser InfoJobs (modal autofill)
│   ├── detalhe_vaga.py    # Detalhe + pipeline Kanban + histórico
│   ├── portais.py         # CRUD portais
│   └── tags.py            # CRUD tags
├── components/
│   ├── cards.py           # vaga_card, metric_card
│   ├── charts.py          # Plotly figures (pizza status, barras currículos/portais)
│   ├── forms.py           # Formulários reutilizáveis
│   ├── layout.py          # metric_card, coluna_estilo
│   ├── navbar.py          # Sidebar + navegação
│   └── pipeline.py        # Componente visual Kanban pipeline
└── services/
    └── infojobs_parser.py # Parser assíncrono InfoJobs (JSON-LD + regex HTML)
```

---

## 🗄 Modelo de Dados (SQLite)

| Tabela | Descrição |
|--------|-----------|
| `portais` | Portais de emprego (InfoJobs, LinkedIn, etc.) |
| `vagas` | Vagas com nome, empresa, link, salário, salário_max, modalidade, descrição, interesse (1-5), aderência (1-5), status, portal, datas (encontrada/envio/publicação), notas, fonte_id |
| `tags` | Tags livres para categorização |
| `vaga_tags` | N:N vagas ↔ tags |
| `historico_status` | Log automático de mudanças de status (trigger SQLite) |

**Status válidos:** `Interessado`, `Currículo Enviado`, `Entrevista Agendada`, `Em Processo`, `Oferta`, `Aceito`, `Rejeitado`

---

## 🚀 Como Rodar

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
docker run -p 8050:8050 -v vagas_db:/app/data vagas-dash
```

> O banco é persistido via volume Docker `vagas_db` (mapeado em `/app/data/`).

---

## ⚙️ Funcionalidades Principais

| Página | Funcionalidades |
|--------|-----------------|
| **Dashboard** | 4 cards de métricas + 3 gráficos Plotly (pizza status, barras currículos/dia, barras por portal) |
| **Vagas** | Lista em cards com filtros laterais (status multi-check, portal dropdown, tag dropdown, busca texto), excluir |
| **Nova Vaga** | Formulário completo com sliders de interesse/aderência, tipo de salário (fixo/faixa/não informado), tags inline, + **modal autofill InfoJobs** (cola ID → parser JSON-LD + HTML → pré-preenche tudo) |
| **Detalhe Vaga** | Visualização completa + pipeline Kanban clicável + histórico de status + editar/excluir |
| **Portais** | CRUD lateral (lista à esquerda, form à direita) |
| **Tags** | CRUD simples + criação rápida inline no formulário de vaga |

---

## 🔧 Parser InfoJobs (`services/infojobs_parser.py`)

- **Zero dependências pesadas** — só `httpx`, `re`, `json`, `html` (stdlib)
- **2 requests paralelos** (asyncio): página da vaga + aba "Empresa"
- **Extração principal**: JSON-LD `schema.org/JobPosting` (dados estruturados confiáveis)
- **Complementos via regex mínimo**: modalidade, salário bruto, listas (exigências, valorizado, benefícios), habilidades/tags, detalhes da empresa
- Retorna `dict` pronto para `models.criar_vaga()` + extras organizados em `extras{}`

---

## 🐳 Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DB_PATH` | `vagas.db` | Caminho do arquivo SQLite |

---

## 📦 Dependências Principais (`requirements.txt`)

```
dash>=3.0.4
dash-bootstrap-components>=2.0.4
plotly>=5.24.1
pandas>=2.2.2
httpx>=0.27.0
```

---

## 🎨 Design System (Resumo)

- **Tema**: Dark mode navy (`#060B17` background)
- **Cores semânticas**: Primary teal `#2ED3C8`, Destaque roxo `#8B7CFF`, Sucesso verde `#2FCB70`, Alerta âmbar `#F5A524`, Perigo vermelho `#FF5F6D`
- **Status colors**: Mapeamento fixo por status (usado em badges, pipeline, gráficos)
- **Tipografia**: IBM Plex Sans (UI) + JetBrains Mono (code/data)
- **Espaçamento**: Sistema 4px base (xs=4, sm=8, md=16, lg=24, xl=32)
- **Componentes**: Cards elevados, inputs dark, badges pill, tags, pipeline steps

---

## 📝 Próximos Passos / Ideias

- [ ] Testes automatizados (pytest + dash.testing)
- [ ] Exportar relatórios (PDF/Excel)
- [ ] Mais parsers (LinkedIn, Catho, Gupy)
- [ ] Autenticação multi-usuário
- [ ] Notificações/alertas de prazos
- [ ] Docs de deploy (Fly.io, Railway, Render)