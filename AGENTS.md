# AGENTS.md — Sistema_Vagas_Dash

## Run / Dev Commands
```bash
# Local
python app.py                    # runs on http://localhost:8050

# Docker
docker-compose up --build        # builds image, runs on port 8050
docker run -p 8050:8050 -e DB_PATH=/app/data/vagas.db -v vagas_db:/app/data vagas-dash
```

## Project Structure (key entrypoints)
```
app.py              # Dash app factory, routing, global layout, sidebar, notifications
db/database.py      # SQLite schema, migrations, connection context manager
db/models.py        # CRUD: portais, vagas, tags, historico_status
styles.py           # Design system (Mantine tokens, spacing, status colors)
pages/              # Route handlers (dashboard, vagas, nova_vaga, detalhe_vaga, portais, tags)
components/         # Reusable UI: cards, charts, forms, vaga_form, layout, navbar, pipeline
services/infojobs_parser.py  # Async parser (httpx + regex + JSON-LD, no BeautifulSoup)
```

> **UI stack**: Dash Mantine Components (`dmc.*`) — NOT Dash Bootstrap Components. No `dbc` imports anywhere.

## Database
- File: `vagas.db` (persisted via docker volume at `/app/data/vagas.db`)
- Env: `DB_PATH` (default `vagas.db`)
- Schema managed in `db/database.py:SCHEMA_SQL` + `migrar_schema()` for additive migrations
- Foreign keys ON, triggers for `updated_at` and `historico_status` on status change

## Known Issue (from erro.md) — FIXED
~~**Callback ID mismatch** on `/nova-vaga`~~ — resolved in `components/vaga_form.py`:
- `salario-tipo` radio (fixo | faixa | nai) + `_condicional_salario()` callback toggles the `salario`/`salario-max` inputs
- `autofill-salary` store carries parsed values into the conditional render
- `salvar_vaga` reads `State('salario', 'value')` / `State('salario-max', 'value')` only when visible

## Parser InfoJobs (`services/infojobs_parser.py`)
- **No BeautifulSoup** — uses `httpx.AsyncClient`, `re`, `json`, `html` (stdlib)
- 2 parallel requests: vacancy page + company tab
- Primary extraction: JSON-LD `schema.org/JobPosting`
- Regex fallbacks: modalidade, salário bruto, listas (exigências/valorizado/benefícios), skills/tags, empresa detalhes
- Returns `dict` compatible with `db.models.criar_vaga()` + `extras{}` for UI

## Dash Conventions
- **Routing**: `app.py:display_page()` switches on `pathname` → returns page `layout()`
- **State stores**: `editing_portal_id`, `notification` (in `app.py`); per-page: `vaga-form-mode`, `autofill-salary`, `autofill-source`, `form-saved-event`, `vagas-trigger`, `portais-trigger`, `tags-trigger`, `editing_tag_id`, `excluir_tag_id`, `vaga-id-store`, `detalhe-trigger`
- **Notifications**: `dmc.NotificationContainer` (app.py layout) via `notification` store + `show_notification` callback → sends `{"action": "show", "title", "message", "color", "autoClose": 4000}`
- **Forms**: vaga form in `components/vaga_form.py` (`form_vaga()` single create/edit form + save/autofill callbacks); `components/forms.py` has `form_portal`, `form_tag`, input helpers, `modal_autofill_infojobs`
- **Callbacks**: defined at module level in each page/component file; use `prevent_initial_call=True` and `allow_duplicate=True` where needed

## Style System (`styles.py`)
- Colors: Mantine CSS variables — `COR_FUNDO="var(--mantine-color-body)"`, `COR_PRIMARY="var(--mantine-primary-color-filled)"`, `COR_DESTAQUE="var(--mantine-color-violet-5)"` (teal-5/yellow-6/red-6 for success/alert/danger); status hex map in `STATUS_CORES`
- Spacing scale: 4px base (xs=4, sm=8, md=16, lg=24, xl=32)
- Fonts: IBM Plex Sans (UI), JetBrains Mono (code) — loaded via `index_string` in `app.py`
- Component styles: `CARD_STYLE`, `INPUT_STYLE`, `SELECT_STYLE`, `SOMBRA_NIVEL_1`
- Sidebar width: `SIDEBAR_WIDTH = 260`

## Dependencies
```
dash>=3.0.4
dash-mantine-components>=2.0.0
plotly>=5.24.1
pandas>=2.2.2
httpx>=0.27.0
```
No test/lint/typecheck config present.

## Environment
- Python 3.11+ (Dockerfile uses `python:3.11-slim`)
- SQLite file persists in `vagas.db` (gitignored)
- No auth, single-user local tool

## Common Tasks
| Task | How |
|------|-----|
| Add page | Create `pages/nova_pagina.py` with `layout()`, import in `app.py`, add route in `display_page()` |
| Add model | Edit `db/database.py:SCHEMA_SQL`, add migration in `migrar_schema()`, add CRUD in `db/models.py` |
| Modify parser | Edit `services/infojobs_parser.py` — test with `python -m services.infojobs_parser <vaga_id>` |
| Debug callback | Check browser console; Dash logs callback registration errors on page load |