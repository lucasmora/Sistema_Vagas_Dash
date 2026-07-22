# AGENTS.md — Sistema_Vagas_Dash

## Run / Dev Commands
```bash
# Local
python app.py                    # runs on http://localhost:8050

# Docker
docker-compose up --build        # builds image, runs on port 8050
docker run -p 8050:8050 -v $(pwd)/vagas.db:/app/vagas.db vagas-dash
```

## Project Structure (key entrypoints)
```
app.py              # Dash app factory, routing, global layout, sidebar, notifications
database.py         # SQLite schema, migrations, connection context manager
models.py           # CRUD: portais, vagas, tags, historico_status
styles.py           # Design system (colors, spacing, component styles)
pages/              # Route handlers (dashboard, vagas, nova_vaga, detalhe_vaga, portais, tags)
components/         # Reusable UI: cards, charts, forms, layout, navbar, pipeline
services/infojobs_parser.py  # Async parser (httpx + regex + JSON-LD, no BeautifulSoup)
```

## Database
- File: `vagas.db` (persisted via docker volume at `/app/data/vagas.db`)
- Env: `DB_PATH` (default `vagas.db`)
- Schema managed in `database.py:SCHEMA_SQL` + `migrar_schema()` for additive migrations
- Foreign keys ON, triggers for `updated_at` and `historico_status` on status change

## Known Issue (from erro.md)
**Callback ID mismatch** on `/nova-vaga`: code references `State('salario', 'value')` but layout uses dynamic IDs:
- `salario-tipo` (RadioItems: "fixo" | "faixa" | "nai")
- `salario` input only rendered when `salario-tipo != "nai"`
- `salario-max` input only rendered when `salario-tipo == "faixa"`

Fix: update callback to read `salario-tipo` + conditional `salario`/`salario-max` states.

## Parser InfoJobs (`services/infojobs_parser.py`)
- **No BeautifulSoup** — uses `httpx.AsyncClient`, `re`, `json`, `html` (stdlib)
- 2 parallel requests: vacancy page + company tab
- Primary extraction: JSON-LD `schema.org/JobPosting`
- Regex fallbacks: modalidade, salário bruto, listas (exigências/valorizado/benefícios), skills/tags, empresa detalhes
- Returns `dict` compatible with `models.criar_vaga()` + `extras{}` for UI

## Dash Conventions
- **Routing**: `app.py:display_page()` switches on `pathname` → returns page `layout()`
- **State stores**: `dcc.Store(id="edit_mode")`, `editing_portal_id`, `notification`, `vagas-trigger`, `portais-trigger`
- **Notifications**: `dbc.Toast` via `notification` store + `show_notification` callback
- **Forms**: built in `components/forms.py` (`form_nova_vaga`, `form_editar_vaga`, `form_portal`, `form_tag`, `salario_inputs`, `modal_autofill_infojobs`)
- **Callbacks**: defined at module level in each page file; use `prevent_initial_call=True` and `allow_duplicate=True` where needed

## Style System (`styles.py`)
- Colors: `COR_FUNDO="#060B17"`, `COR_PRIMARY="#2ED3C8"`, `COR_DESTAQUE="#8B7CFF"`, status colors map in `STATUS_COLORS`
- Spacing scale: 4px base (xs=4, sm=8, md=16, lg=24, xl=32)
- Fonts: IBM Plex Sans (UI), JetBrains Mono (code) — loaded via `index_string` in `app.py`
- Component styles: `CARD_STYLE`, `INPUT_STYLE`, `SELECT_STYLE`, `SOMBRA_NIVEL_1/2/3`

## Dependencies
```
dash>=3.0.4
dash-bootstrap-components>=2.0.4
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
| Add model | Edit `database.py:SCHEMA_SQL`, add migration in `migrar_schema()`, add CRUD in `models.py` |
| Modify parser | Edit `services/infojobs_parser.py` — test with `python -m services.infojobs_parser <vaga_id>` |
| Debug callback | Check browser console; Dash logs callback registration errors on page load |