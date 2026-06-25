# Plano de Implementação — Sistema_Vagas

App pessoal para rastrear candidaturas a vagas de emprego. Monousuário, dados locais, interface Dash no navegador.

## Docker

### Arquivos de Configuração
- `Dockerfile` — imagem Python 3.11 slim com dependências
- `docker-compose.yml` — serviço app + volume persistente para SQLite
- `requirements.txt` — dependências Python (Dash, Plotly, Pandas, etc.)
- `.dockerignore` — excluir `__pycache__`, `.git`, `*.db`, `venv`

### Volume Persistente
- Volume `vagas_db` mapeado para `/app/data`
- Banco salvo em `/app/data/vagas.db` (sobrevive a rebuilds)

### Comandos Úteis
```bash
docker compose up --build   # build + sobe
docker compose up -d        # detached
docker compose down         # para
docker compose logs -f      # logs
```

---

## Stack Tecnológica

| Tecnologia | Finalidade |
|---|---|
| Python | Linguagem |
| Dash | Framework web |
| Plotly | Gráficos interativos |
| Pandas | Apoio para gráficos |
| SQLite 3 | Banco de dados local |

---

## Database — Schema SQLite

### Tabela: `portais`

| Coluna | Tipo | Restrições | Descrição | Exemplo |
|---|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | Identificador único do portal | 1 |
| nome | TEXT | UNIQUE NOT NULL | Nome do portal de vagas | LinkedIn |
| url_base | TEXT | | URL base do portal | linkedin.com |
| tipo_login | TEXT | | Método de login usado no portal | e-mail |
| ultima_atualizacao | DATE | | Data da última atualização do perfil no portal | 2025-12-10 |
| notas | TEXT | | Observações sobre o portal | Conta criada em 2020 |
| created_at | TIMESTAMP | DEFAULT localtime | Data/hora de criação do registro | 2025-11-01 14:30:00 |

### Tabela: `vagas`

| Coluna | Tipo | Restrições | Descrição | Exemplo |
|---|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | Identificador único da vaga | 42 |
| nome | TEXT | NOT NULL | Título curto que identifica a vaga | Gerente Financeiro - Stone |
| empresa | TEXT | | Nome da empresa contratante (pode ser NULL = vaga confidencial) | Stone Pagamentos |
| link | TEXT | | URL original da vaga no portal | https://linkedin.com/jobs/123 |
| salario | REAL | | Valor fixo ou valor mínimo da faixa salarial (R\$) | 12000 |
| salario_max | REAL | | Valor máximo da faixa salarial (NULL se fixo ou não informado) | 15000 |
| modalidade | TEXT | | Regime de trabalho | Remoto |
| descricao | TEXT | | Texto completo colado do anúncio da vaga | \*texto longo com requisitos, benefícios...\* |
| interesse | INTEGER | CHECK(1-5) | Nível de interesse na vaga (1 a 5) | 5 |
| aderencia | INTEGER | CHECK(1-5) | Nível de aderência do perfil à vaga (1 a 5) | 4 |
| status | TEXT | CHECK(7 valores) | Status atual no pipeline de candidatura | Entrevista Agendada |
| portal_id | INTEGER | FK → portais(id) | Referência ao portal onde a vaga foi encontrada (NULL = sem portal) | 1 |
| data_encontrada | DATE | | Data em que a vaga foi encontrada | 2025-11-15 |
| data_envio | DATE | | Data de envio do currículo (NULL = não enviado) | 2025-11-20 |
| notas | TEXT | | Anotações pessoais sobre a vaga ou processo seletivo | Precisa estudar SQL avançado |
| created_at | TIMESTAMP | DEFAULT localtime | Data/hora de criação do registro | 2025-11-15 09:00:00 |
| updated_at | TIMESTAMP | DEFAULT localtime | Data/hora da última alteração | 2025-11-20 14:30:00 |

### Tabela: `tags`

| Coluna | Tipo | Restrições | Descrição | Exemplo |
|---|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | Identificador único da tag | 7 |
| nome | TEXT | UNIQUE NOT NULL | Nome da tag para categorizar vagas | Python |

### Tabela: `vaga_tags` (N:N)

| Coluna | Tipo | Restrições | Descrição | Exemplo |
|---|---|---|---|---|
| vaga_id | INTEGER | FK → vagas(id) ON DELETE CASCADE | Referência à vaga | 42 |
| tag_id | INTEGER | FK → tags(id) ON DELETE CASCADE | Referência à tag | 7 |
| (PK) | | (vaga_id, tag_id) | Garante unicidade da associação | |

### Tabela: `historico_status`

| Coluna | Tipo | Restrições | Descrição | Exemplo |
|---|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | Identificador único do registro | 105 |
| vaga_id | INTEGER | FK → vagas(id) ON DELETE CASCADE | Referência à vaga | 42 |
| status_anterior | TEXT | | Status antes da mudança (NULL no primeiro registro) | Interessado |
| status_novo | TEXT | NOT NULL | Status após a mudança | Currículo Enviado |
| data_mudanca | TIMESTAMP | DEFAULT localtime | Data/hora em que a mudança ocorreu | 2025-11-20 14:30:00 |

### Regras do Banco

- `get_db()` é um context manager com `sqlite3.Row` como row_factory e `PRAGMA foreign_keys=ON`
- `sqlite3.Row` sempre convertido para `dict` antes de passar ao Pandas/Plotly
- Timestamps sempre em hora local (`datetime('now','localtime')`), NUNCA UTC
- Datas armazenadas em ISO (`YYYY-MM-DD`), exibidas em DD/MM/YYYY

---

## Design System

### Paleta de Cores

| Token | Hex | Uso |
|---|---|---|
| COR_FUNDO | `#0E1117` | Fundo da página (body) |
| COR_SUPERFICIE | `#1A1D24` | Cards, inputs, superfícies elevadas |
| COR_BORDA | `#2C303A` | Bordas de cards, inputs, divisores |
| COR_TEXTO | `#E4E6EB` | Texto principal, títulos |
| COR_TEXTO_SEC | `#9CA3AF` | Labels, placeholders, texto secundário |
| COR_PRIMARY | `#00BFA6` | Botões, links, destaque principal (verde-água) |
| COR_DESTAQUE | `#6C63FF` | Tags pills, gráfico, destaque secundário (roxo) |

### Cores dos Status do Pipeline

| Status | Cor |
|---|---|
| Interessado | `#6C757D` |
| Currículo Enviado | `#0DCAF0` |
| Entrevista Agendada | `#FFC107` |
| Em Processo | `#6C63FF` |
| Oferta | `#198754` |
| Aceito | `#00BFA6` |
| Rejeitado | `#DC3545` |

### Regras de Layout

- Layout responsivo com `dbc.Row` / `dbc.Col` (sistema grid Bootstrap)
- Cards com `background: #1A1D24`, `border: 1px solid #2C303A`, `borderRadius: 12px`
- Inputs com `background: #1A1D24`, `border: 1px solid #2C303A`, `borderRadius: 8px`
- Sidebar fixa à esquerda (2 colunas de largura) com conteúdo à direita (10 colunas)
- Sidebar ocupa 100vh, com navegação vertical e informações do sistema no rodapé
- Badges de status com fundo 20% de opacidade da cor do status e borda 1px sólida
- Tags exibidas como pills com fundo `#6C63FF` a 20% de opacidade e texto na cor `#6C63FF`
- Todo o conteúdo tem padding interno de 24px 32px

### Pipeline Visual

```
Interessado → Currículo Enviado → Entrevista Agendada → Em Processo → Oferta → Aceito
```

- Exibido como linha horizontal com bolinhas numeradas (1 a 6) conectadas por traços
- **Rejeitado** é status terminal — acessível de qualquer posição no pipeline
- Bolinhas preenchidas com a cor do status até o estágio atual; as seguintes ficam na cor da borda

---

## Roteamento (app.py)

- `dcc.Location(id="url", refresh=False)` para navegação manual (sem Dash Pages)
- `app.config.suppress_callback_exceptions = True` — necessário para roteamento manual
- 3 stores globais: `edit_mode`, `editing_portal_id`, `notification` (`selected_vaga_id` removido — ID vem da URL)
- Sidebar fixa à esquerda (2 colunas) com `dcc.Link` para navegação (sem callback)
- Conteúdo à direita (10 colunas) renderizado via callback `display_page`
- Callback `display_page`: parseia `pathname` (ex: `/vagas/42` → page="vagas", vaga_id=42) + `edit_mode`
- Callback `show_notification`: lê store `notification` e exibe `dbc.Alert` dismissable com duração 4s

| Rota | Página | Funcionalidade |
|---|---|---|
| `/` ou `/dashboard` | Dashboard | Métricas + gráficos |
| `/nova-vaga` | Nova Vaga | Formulário completo de criação |
| `/vagas` | Listar Vagas | Grid de cards + filtros |
| `/vagas/<id>` | Detalhe da Vaga | Pipeline, info, edição inline, status, histórico |
| `/portais` | Portais | CRUD com lista + formulário |
| `/tags` | Tags | Lista + formulário de adição |

### Navegação programática (botão "Detalhes" na listagem)
- Botão "Detalhes" em cada card: `dcc.Link(href=f"/vagas/{vaga_id}", ...)` — navegação instantânea sem callback
- Para navegação via callback (ex: após salvar): callback atualiza `dcc.Location(href="/vagas/42")` + `refresh=False`

---

## Regras de Negócio

1. **Salário**: 3 modos — valor fixo (`salario` preenchido, `salario_max=NULL`), faixa (ambos preenchidos), não informado (ambos NULL)
2. **Data envio**: se NULL, exibir "⏳ Currículo não enviado" / "⏳ Não enviado"
3. **Nome** é o campo principal de identificação (ex: "Gerente Financeiro - Stone") — **obrigatório**
4. **Empresa** é opcional (NULL = vaga confidencial/oculta por segurança)
5. **Histórico de status** registrado automaticamente sempre que o status muda
6. **Tags** têm relação N:N com vagas (tabela `vaga_tags`)

---

## Descrição das Páginas

### Dashboard
- 4 metric cards (Total, Ativas, Em Entrevista, Currículos)
- Gráfico pizza: vagas por status
- Gráfico barras: currículos enviados por dia
- Gráfico barras horizontal: vagas por portal
- Cada gráfico envolto em `dcc.Loading`

### Nova Vaga
- Formulário completo: nome, empresa (opcional), link, modalidade, salário (RadioItems + input/slider condicional), portal, data encontrada, data envio, interesse, aderência, tags (dropdown multi + campo para criar nova), descrição, notas
- Botão "Salvar Vaga" com validação (**apenas nome obrigatório**)
- Callback condicional para exibir campo de salário conforme tipo selecionado
- Após salvar com sucesso: callback atualiza `dcc.Location(href=f"/vagas/{nova_vaga_id}")` → redireciona para detalhe

### Listar Vagas
- Linha de filtros: status (multi), portal, tag, busca textual
- Grid de cards em 2 colunas
- Cada card: nome, empresa, badge de status (cor dinâmica), salário, portal, modalidade, data envio, interesse/aderência (estrelas), tags (pills), botão "Detalhes"
- Botão "Detalhes": `dcc.Link(href=f"/vagas/{vaga_id}", ...)` — navegação direta sem callback

### Detalhe da Vaga (`/vagas/<id>`)
- Botão voltar (`dcc.Link(href="/vagas", ...)`) + nome + empresa
- Pipeline visual (bolinhas numeradas conectadas por traços)
- Card de informações (tabela com todos os campos)
- Link da vaga (se existir)
- Descrição e Notas em cards com collapse (toggle ao clicar)
- Tags em pills
- Seletor de status + botão "Atualizar Status"
- Histórico de status em collapse
- Botões: Editar, Excluir
- **Modo edição**: substitui info por formulário inline; botões "Salvar alterações" e "Cancelar"
- `vaga_id` extraído do `pathname` no callback `display_page` (não usa store)

### Portais
- Coluna esquerda: lista de cards com nome, url, login, última atualização, notas; botões Editar e Excluir
- Coluna direita: formulário contextual (novo ou edição)
- Store `editing_portal_id` controla qual formulário exibir

### Tags
- Coluna esquerda: lista de tags com botão Excluir
- Coluna direita: campo nome + botão "Adicionar"

---

## Padrão de Callbacks

```python
from dash import html, dcc, callback, Input, Output, State, no_update, callback_context, PreventUpdate

@callback(
    Output("output-id", "children"),
    Input("input-id", "value"),
    State("store-id", "data"),
    prevent_initial_call=True,
)
def minha_funcao(valor, store_data):
    if not valor:
        raise PreventUpdate
    return html.P(f"Resultado: {valor}")
```

### Navegação programática (padrão manual com `refresh=False`)

```python
@callback(
    Output("url", "href", allow_duplicate=True),
    Input("btn-salvar", "n_clicks"),
    State("form-data", "data"),
    prevent_initial_call=True,
)
def salvar_e_redirecionar(n_clicks, form_data):
    if not n_clicks:
        raise PreventUpdate
    vaga_id = criar_vaga(form_data)
    return f"/vagas/{vaga_id}"  # navega sem refresh
```

### Pattern-Matching Callbacks (botões dinâmicos)

```python
# IDs no formato: {"type": "btn-detalhe", "index": vaga_id}

@callback(
    Output({"type": "btn-detalhe", "index": MATCH}, "n_clicks"),
    Input({"type": "btn-detalhe", "index": MATCH}, "n_clicks"),
    prevent_initial_call=True,
)
def navegar_detalhe(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    vaga_id = callback_context.triggered_id["index"]
    return f"/vagas/{vaga_id}"  # ou usar dcc.Link no layout (preferível)
```

### Partial Updates com `Patch` (Dash 2.9+)

```python
from dash import Patch

@callback(
    Output("tabela-vagas", "data", allow_duplicate=True),
    Input("btn-filtrar", "n_clicks"),
    State("filtros", "data"),
    prevent_initial_call=True,
)
def atualizar_tabela(n_clicks, filtros):
    if not n_clicks:
        raise PreventUpdate
    dados = buscar_vagas(filtros)
    patched = Patch()
    patched.extend(dados)  # ou patched[i] = novo_valor para item específico
    return patched
```

---

### Boas Práticas (oficiais)

| Prática | Quando usar |
|---|---|
| `prevent_initial_call=True` | Sempre em callbacks de botão (evita execução no load) |
| `raise PreventUpdate` | Em vez de `return no_update` — mais explícito e performático |
| `allow_duplicate=True` | Apenas quando **necessário** (múltiplos callbacks no mesmo output) — prefira `dcc.Link` para navegação |
| `Patch` | Atualizações parciais de listas/tabelas/figuras (evita re-render completo) |
| `suppress_callback_exceptions=True` | Obrigatório no `app.py` para roteamento manual (layout dinâmico) |
| Callbacks no módulo da página | Organização — importados no `app.py` antes de `app.run()` |
| `callback_context.triggered_id` | Para saber qual input disparou (pattern-matching ou múltiplos inputs) |

- **Navegação preferencial via `dcc.Link`** (sem callback) — use callback apenas quando precisar processar dados antes de navegar
- Botões dinâmicos: `{"type": "btn-tipo", "index": id}` com `MATCH`/`ALL`
- Evite `allow_duplicate` desnecessário — prefira outputs separados ou callback único com `ctx.triggered_id`

---

## Ordem de Implementação Sugerida

| Passo | O quê |
|---|---|
| 1 | **Docker + styles** — `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `.dockerignore`, `styles.py` |
| 2 | **Database + Models** — `database.py` (conexão, schema, init_db), `models.py` (CRUD completo) |
| 3 | **App Shell** — `app.py` (layout raiz, stores, callbacks globais, routing), `components/navbar.py` (sidebar), `components/layout.py` (metric_card) |
| 4 | **Shared Components** — `components/cards.py` (vaga_card), `components/pipeline.py` (pipeline_view), `components/forms.py` (form_editar_vaga), `components/charts.py` |
| 5 | **Dashboard** — `pages/dashboard.py` |
| 6 | **Páginas Simples** — `pages/portais.py`, `pages/tags.py` |
| 7 | **Vagas (Core)** — `pages/vagas.py` (listagem + filtros), `pages/detalhe_vaga.py`, `pages/nova_vaga.py` |
