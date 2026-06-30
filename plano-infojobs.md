# Plano de Mudança

## Resumo

Corrigir e aprimorar o auto-preenchimento de vagas do InfoJobs, ajustando 7 problemas identificados nos testes com a vaga ID 11701447: título truncado, modalidade não preenchida, faixa salarial incorreta, data encontrada errada, notas duplicadas, HTML entities não decodificadas, e aproveitamento do `baseSalary` do JSON-LD. Adicionar campo `data_publicacao` ao banco e ao formulário.

---

## Contexto

O sistema `Sistema_Vagas_Dash` é um app Dash monousuário para rastrear candidaturas. Recentemente foi implementada uma feature de auto-preenchimento que, ao selecionar o portal "InfoJobs" no formulário de nova vaga, abre um modal para colar o ID da vaga e preenche automaticamente os campos.

A implementação atual tem os seguintes problemas, identificados com a vaga de teste ID 11701447 ("Desenvolvedor Web - Loja Virtual Chatbot"):

| # | Problema | Comportamento Atual | Comportamento Esperado |
|---|----------|---------------------|------------------------|
| 1 | Título truncado | `"Desenvolvedor Web"` (JSON-LD) | `"Desenvolvedor Web - Loja Virtual Chatbot"` (header HTML) |
| 2 | Modalidade ausente | Campo vazio | `"Presencial"` (ou o valor correto do HTML) |
| 3 | Faixa salarial | Mostra apenas R$ 2000 (min), como "fixo" | Mostra R$ 2.000 a R$ 20.000 (faixa com dois inputs) |
| 4 | Data encontrada errada | Preenchida com `data_publicacao` (2026-06-09) | Deve ser a data de HOJE |
| 5 | Notas inchadas | Duplica salário, modalidade, requisitos etc. | Deve conter só dados não salvos em campos próprios |
| 6 | HTML entities cruas | `"H&#xED;brido"`, `"Participa&#xE7;&#xE3;o"` | `"Híbrido"`, `"Participação"` |
| 7 | `baseSalary` ignorado | Parser usa regex no HTML para salário | JSON-LD já tem `minValue`/`maxValue` prontos |

---

## Objetivos

1. Extrair o título completo da vaga do `<h2 class="js_vacancyHeaderTitle">`
2. Decodificar HTML entities (`html.unescape()`) em todos os campos
3. Extrair `minValue`/`maxValue` do `baseSalary` do JSON-LD
4. Preencher faixa salarial corretamente no formulário (2 inputs quando aplicável)
5. Preencher `data_encontrada` com a data de hoje
6. Adicionar coluna `data_publicacao` ao banco + DatePicker no formulário
7. Auto-preenchimento de `data_publicacao` com a data do InfoJobs
8. Enxugar `notas` para conter apenas dados sem campo próprio
9. Adicionar coluna `fonte_id` ao banco (ID externo da vaga)
10. Corrigir a extração de modalidade (regex + decode)

---

## Não-Objetivos

- **Não** serão adicionadas colunas para `tipo_contrato`, `local_cidade`, `local_estado`, `empresa_setor` ou `empresa_porte` — estes campos continuarão em `notas` como texto livre
- **Não** será refatorado o modelo de dados além das colunas `data_publicacao` e `fonte_id`
- **Não** será alterada a página de edição de vagas (`form_editar_vaga`) — apenas o formulário de nova vaga
- **Não** será modificada a página de listagem, dashboard, ou detalhe da vaga
- **Não** será implementada busca reversa (InfoJobs → sistema) ou sincronização automática

---

## Decisões Tomadas

1. **Título**: Usar regex no `<h2 class="js_vacancyHeaderTitle">` do HTML, com fallback para JSON-LD `title`
2. **HTML entities**: Aplicar `html.unescape()` do módulo `html` (stdlib) em todos os campos extraídos (título, modalidade, salário, descrição, requisitos, benefícios, habilidades)
3. **Salário**: Extrair `minValue`/`maxValue` do `baseSalary` do JSON-LD quando presente; usar o texto HTML como fallback
4. **Faixa salarial**: No callback `buscar_e_preencher`, quando `salario_min` E `salario_max` existirem, criar 2 inputs (`salario` + `salario-max`) com labels "Salário Mínimo (R$)" e "Salário Máximo (R$)"
5. **Data encontrada**: Preencher com `datetime.now().strftime("%Y-%m-%d")` (hoje)
6. **Data publicação**: Adicionar coluna `data_publicacao DATE` + DatePicker `nova-vaga-data-publicacao` no formulário + auto-preenchimento com a data ISO do JSON-LD
7. **Fonte ID**: Adicionar coluna `fonte_id TEXT` para armazenar o ID externo (ex: "11701447")
8. **Notas**: Conter APENAS: ID InfoJobs, data publicação, data validade, localização, tipo contrato, dados da empresa (setor, porte, matriz), adequação média. **Excluir**: salário, modalidade, descrição, requisitos, benefícios, habilidades (já vão em `extras` ou em campos próprios)
9. **Modalidade**: Refinar regex para capturar o texto após `<use xlink:href="#house-and-building" />` dentro do bloco `VacancyHeader`, evitando similar jobs
10. **Salário-tipo**: O radio `salario-tipo` continuará sem ser alterado pelo callback de autofill (permanece "nai" visualmente). O input correto será criado em `salario-valores.children`, e o `salvar_vaga` callback lerá `salario.value` e `salario-max.value` corretamente

---

## Impacto na Arquitetura

### Módulos afetados

| Módulo | Arquivo | Tipo de mudança |
|--------|---------|-----------------|
| Parser InfoJobs | `services/infojobs_parser.py` | ✏️ Modificação: regex título, baseSalary, html.unescape() |
| Callbacks | `pages/nova_vaga.py` | ✏️ Modificação: faixa salarial, data=hoje, notas enxutas |
| Componentes | `components/forms.py` | ✏️ Modificação: + DatePicker data_publicacao |
| Banco | `models.py` + `database.py` | ✏️ Modificação: + colunas data_publicacao, fonte_id |
| Layout app | `app.py` | ✅ Nenhuma mudança |
| Outras páginas | `pages/vagas.py`, `pages/detalhe_vaga.py` | ✅ Nenhuma mudança |

### Banco de dados afetado

**Tabela `vagas`**: 2 novas colunas

```sql
ALTER TABLE vagas ADD COLUMN data_publicacao DATE;
ALTER TABLE vagas ADD COLUMN fonte_id TEXT;
```

**Tabela `portais`**: ✅ Nenhuma mudança

### Frontend afetado

- `pages/nova_vaga.py`: Callback de preenchimento ajustado (faixa salarial, data hoje, notas)
- `components/forms.py`: + DatePicker `nova-vaga-data-publicacao` no formulário

---

## Fases de Implementação

### Fase 1 — Parser: título, entities, baseSalary

**Objetivo**: Extrair dados corretos do InfoJobs

**Tarefas**:

1. Em `_extrair_json_ld()`, também extrair `baseSalary.value.minValue` e `maxValue` quando presentes
2. Criar função `_extrair_titulo_html(html) -> str` que busca o `<h2 class="js_vacancyHeaderTitle">` e retorna o texto completo
3. Modificar `parse_vaga_infojobs()` para usar o título HTML com fallback para JSON-LD
4. Aplicar `html.unescape()` em todos os campos relevantes da VagaInfoJobs (titulo, modalidade, salario_bruto, descricao, requisitos, beneficios, habilidades, empresa_detalhes.*)
5. No `_parse_salario()`, priorizar `baseSalary` do JSON-LD sobre regex no HTML
6. Ajustar `_extrair_modalidade()` para buscar especificamente no bloco `VacancyHeader`

**Resultado Esperado**:

```python
parse_vaga_infojobs_dict("11701447")
# → nome: "Desenvolvedor Web - Loja Virtual Chatbot"
# → modalidade: "Presencial" (decodificado)
# → salario: 2000.0, salario_max: 20000.0
```

**Dependências**: Nenhuma

---

### Fase 2 — Banco: novas colunas

**Objetivo**: Adicionar suporte a `data_publicacao` e `fonte_id` no banco

**Tarefas**:

1. Em `database.py`, adicionar ao `SCHEMA_SQL` as novas colunas na `CREATE TABLE IF NOT EXISTS vagas` (importante: a cláusula CREATE não adiciona coluna se a tabela já existe)
2. Criar função `migrar_schema()` em `database.py` ou `models.py` que executa:
   ```sql
   ALTER TABLE vagas ADD COLUMN data_publicacao DATE;
   ALTER TABLE vagas ADD COLUMN fonte_id TEXT;
   ```
   com try/except para colunas já existentes
3. Chamar `migrar_schema()` no `init_db()` do `app.py`

**Resultado Esperado**: Banco com colunas novas; `SELECT data_publicacao, fonte_id FROM vagas LIMIT 1` funciona

**Dependências**: Nenhuma

---

### Fase 3 — Models: suporte às novas colunas

**Objetivo**: `criar_vaga()` e `atualizar_vaga()` aceitarem os novos campos

**Tarefas**:

1. Em `models.py`, adicionar parâmetros `data_publicacao: str = ""` e `fonte_id: str = ""` em `criar_vaga()`
2. Atualizar o INSERT SQL para incluir `data_publicacao` e `fonte_id`
3. Atualizar `atualizar_vaga()` com os mesmos novos parâmetros
4. Atualizar o UPDATE SET para incluir os novos campos

**Resultado Esperado**: `criar_vaga(data_publicacao="2026-06-09", fonte_id="11701447")` persiste no banco

**Dependências**: Fase 2

---

### Fase 4 — Formulário: DatePicker data_publicacao

**Objetivo**: Adicionar campo de data de publicação no formulário de nova vaga

**Tarefas**:

1. Em `components/forms.py`, dentro de `form_nova_vaga()`, adicionar um `dcc.DatePickerSingle(id="nova-vaga-data-publicacao")` ao lado do DatePicker de "Data Encontrada", com label "Data Publicação"
2. Exportar o componente no layout

**Resultado Esperado**: DatePicker "Data Publicação" visível no formulário /nova-vaga

**Dependências**: Nenhuma

---

### Fase 5 — Callbacks: preenchimento corrigido

**Objetivo**: Ajustar o callback `buscar_e_preencher` para todas as correções de preenchimento

**Tarefas**:

1. Em `pages/nova_vaga.py`, modificar `buscar_e_preencher()`:
   - **Salário**: Verificar se `salario_min` AND `salario_max` existem:
     - Se ambos: criar 2 inputs (`id="salario"` + `id="salario-max"`) com labels "Salário Mínimo (R$)" e "Salário Máximo (R$)"
     - Se só min: criar 1 input (`id="salario"`) com label "Salário (R$)"
     - Se nenhum: `salario_valores = []`
   - **Data encontrada**: Usar `datetime.now().strftime("%Y-%m-%d")`
   - **Data publicação**: Adicionar output `nova-vaga-data-publicacao.date` com a data ISO do JSON-LD
   - **Notas**: Gerar notas enxutas (sem salário, modalidade, descrição, requisitos, benefícios, habilidades), apenas:
     ```
     📌 InfoJobs (ID: {fonte_id})
     📅 Publicada: {data_publicacao}
     ⏳ Válida até: {data_validade}
     📍 Local: {localizacao}
     📋 Tipo: {tipo_contrato}
     🏢 Empresa: {setor} | {porte} | {matriz}
     📊 Adequação: {adequacao_media}
     ```
2. Atualizar o `Output` do callback para incluir `nova-vaga-data-publicacao.date`
3. Atualizar os `State` e parâmetros do callback `salvar_vaga` para incluir `nova-vaga-data-publicacao.date` como state
4. No callback `salvar_vaga`, passar `data_publicacao` e `fonte_id` para `criar_vaga()`

**Resultado Esperado**: Ao buscar vaga 11701447, formulário preenche:
- Nome: "Desenvolvedor Web - Loja Virtual Chatbot"
- Salário min: 2000, Salário max: 20000
- Data encontrada: hoje
- Data publicação: 2026-06-09
- Notas: enxutas (sem duplicação)

**Dependências**: Fase 1, Fase 3, Fase 4

---

### Fase 6 — Rebuild Docker + Teste

**Objetivo**: Aplicar mudanças no container e validar

**Tarefas**:

1. `docker compose build`
2. `docker compose up -d`
3. Testar com ID 11701447:
   - Nome correto
   - Faixa salarial correta
   - Data encontrada = hoje
   - Data publicação = 2026-06-09
   - Notas sem duplicação
   - Modalidade preenchida
4. Testar com ID 11616056 (regressão — sem salário):
   - Nome: "Desenvolvedor de Software"
   - Salário: "Salário a combinar" (sem inputs)
   - Data encontrada = hoje
5. Salvar vaga e verificar no banco

**Resultado Esperado**: Ambas as vagas funcionam sem erros no console do Dash

**Dependências**: Fase 5

---

## Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|:------------:|:-------:|-----------|
| `ALTER TABLE` falha silenciosamente em SQLite | Média | Baixo | Usar try/except com `OperationalError` |
| Regex do título quebra se InfoJobs mudar HTML | Baixa | Médio | Fallback para JSON-LD `title` existente |
| `_condicional_salario` sobrescreve `salario-valores.children` | Alta | Médio | Autofill não altera `salario-tipo`; escreve diretamente em children após o callback padrão |
| HTML entities não previstas (`&#x2B;` = `+`) | Média | Baixo | `html.unescape()` do stdlib lida com todas |
| Vaga sem `baseSalary` no JSON-LD | Média | Baixo | Fallback para regex no HTML (já existe) |

---

## Questões Abertas

1. **Data no DatePicker**: O formato de retorno do `dcc.DatePickerSingle` para o `date` property é string ISO (`YYYY-MM-DD`) ou objeto date? Confirmar comportamento do Dash 3.x.

2. **Ordenação das novas colunas**: O DatePicker `data_publicacao` deve aparecer antes ou depois de `data_encontrada`? Atualmente o layout tem: Portal → Data Encontrada → Data Envio. Sugestão: incluir Data Publicação entre Portal e Data Encontrada.

3. **`fonte_id` visível na UI?** O ID do InfoJobs será armazenado em `notas` (texto) e na coluna `fonte_id`. Deve ser exibido em algum lugar na página de detalhe da vaga, ou apenas interno?

---

## Estratégia de Testes

### Testes unitários

- `parse_vaga_infojobs_dict("11701447")` retorna título completo
- `parse_vaga_infojobs_dict("11701447")["salario"] == 2000.0`
- `parse_vaga_infojobs_dict("11701447")["salario_max"] == 20000.0`
- `html.unescape("H&#xED;brido") == "Híbrido"`
- `_extrair_titulo_html()` retorna string do `js_vacancyHeaderTitle`
- `baseSalary` parsing funciona com minValue+maxValue, só minValue, e ausente

### Testes de integração

- Fluxo completo: modal → colar ID → buscar → formulário preenchido → salvar → banco com dados corretos

### Testes de regressão

- Vaga sem salário (ID 11616056): nome "Desenvolvedor de Software", sem inputs de salário
- Vaga com salário fixo (ID 11713384): salário = 5000.0, sem salario_max
- Vaga com faixa (ID 11701447): salário = 2000.0, salario_max = 20000.0

---

## Estratégia de Rollback

Se algo quebrar:

1. **Banco**: Remover as colunas `data_publicacao` e `fonte_id` via `ALTER TABLE vagas DROP COLUMN` (SQLite 3.35+). Alternativa: restaurar backup do `vagas.db` do volume Docker.
2. **Parser**: Reverter `services/infojobs_parser.py` para a versão anterior (git checkout ou restaurar manualmente).
3. **Callbacks**: Reverter `pages/nova_vaga.py` para a versão anterior.
4. **Docker**: `docker compose down && docker compose up -d` com a imagem anterior.

Comandos:

```bash
# Rollback total
git checkout -- services/infojobs_parser.py pages/nova_vaga.py components/forms.py models.py database.py
docker compose build && docker compose up -d
```

---

## Critérios de Aceitação

- [ ] Vaga 11701447: nome = "Desenvolvedor Web - Loja Virtual Chatbot" ✅
- [ ] Vaga 11701447: modalidade = "Presencial" (ou valor correto do HTML) ✅
- [ ] Vaga 11701447: salario = 2000.0, salario_max = 20000.0 ✅
- [ ] Vaga 11701447: data_encontrada = data de hoje ✅
- [ ] Vaga 11701447: data_publicacao = "2026-06-09" ✅
- [ ] Vaga 11701447: notas sem salário, modalidade, descrição, requisitos, benefícios, habilidades ✅
- [ ] Vaga 11616056 (regressão): nome = "Desenvolvedor de Software" ✅
- [ ] Vaga 11616056: salario = None, sem inputs de salário ✅
- [ ] Vaga 11713384 (regressão): salario = 5000.0, salario_max = None ✅
- [ ] Nenhum erro no console do Dash (logs do container) ✅
- [ ] Salvar vaga com auto-preenchimento persiste todos os campos no banco ✅
- [ ] DatePicker "Data Publicação" visível no formulário ✅
- [ ] Colunas `data_publicacao` e `fonte_id` existem na tabela `vagas` ✅
- [ ] `html.unescape()` aplicado a todos os campos (sem `&#xED;` visível) ✅

---

## Arquivos Provavelmente Afetados

```
services/infojobs_parser.py     — Fase 1: título, baseSalary, html.unescape(), modalidade
database.py                     — Fase 2: migrar_schema(), SCHEMA_SQL atualizado
models.py                       — Fase 3: criar_vaga(), atualizar_vaga() + novos params
components/forms.py             — Fase 4: + DatePicker data_publicacao
pages/nova_vaga.py              — Fase 5: buscar_e_preencher(), salvar_vaga()
app.py                          — Fase 2: init_db() chama migrar_schema()
requirements.txt                — ✅ Nenhuma mudança (httpx já adicionado)
```

---

## Observações

### Decisões confirmadas

- **Título**: Prioridade `js_vacancyHeaderTitle` > JSON-LD `title`
- **Salário**: Prioridade `baseSalary` JSON-LD > regex HTML
- **Data encontrada**: `datetime.now()` (hoje)
- **Notas**: Só dados sem campo próprio; eliminar duplicação de salário, modalidade, descrição, requisitos, benefícios, habilidades
- **`salario-tipo`**: Não será alterado pelo autofill; evita conflito com `_condicional_salario`
- **html.unescape()**: Aplicar em TODOS os campos extraídos

### Suposições

- O `<h2 class="js_vacancyHeaderTitle">` SEMPRE contém o título completo no HTML (não depende de JavaScript)
- O bloco `VacancyHeader` no HTML está presente tanto na página principal quanto na aba "Empresa" (`about.aspx`)
- `html.unescape()` do stdlib cobre todas as entidades HTML usadas pelo InfoJobs

### Questões não resolvidas

- Ordem exata dos DatePickers no formulário (Data Publicação vs Data Encontrada)
- Exibição do `fonte_id` na UI de detalhe da vaga (fora do escopo deste plano)

---

## Validação Final

### 1. Planejador

- [x] Todas as 7 correções identificadas nos testes foram documentadas
- [x] As 2 novas colunas no banco foram incluídas (`data_publicacao`, `fonte_id`)
- [x] O DatePicker `data_publicacao` no frontend foi incluído
- [x] Os não-objetivos estão claros (sem refatoração além do necessário)
- [x] As 6 fases cobrem todas as mudanças necessárias
- [x] Risco de conflito com `_condicional_salario` documentado e mitigado

### 2. Revisor Técnico

- [x] **Consistência**: Fase 1 (parser) → Fase 2 (banco) → Fase 3 (models) → Fase 4 (form) → Fase 5 (callbacks) → Fase 6 (teste). Sequência lógica, cada fase depende da anterior.
- [x] **Banco**: `migrar_schema()` com try/except para colunas já existentes — SQLite não tem `IF NOT EXISTS` para `ALTER TABLE`
- [x] **Parser**: `_extrair_titulo_html` com fallback para JSON-LD — cobertura para casos sem `js_vacancyHeaderTitle`
- [x] **Salário**: `baseSalary` do JSON-LD tem `value.minValue`/`maxValue`. Confirmado que o JSON-LD da vaga 11701447 contém `baseSalary` com ambos.
- [x] **html.unescape()**: Módulo `html` é stdlib, sem dependência externa
- [x] **`salario-tipo`**: Decisão de NÃO alterar pelo autofill evita race condition com `_condicional_salario`. Confirmado que o callback `salvar_vaga` usa `State("salario", "value")` e `State("salario-max", "value")` — funciona independentemente do valor de `salario-tipo`.
- [x] **Data publication**: Import `datetime` já existe em `nova_vaga.py`? Não — será necessário adicionar `from datetime import datetime`
- [x] **Callback outputs**: O número de outputs no callback `buscar_e_preencher` aumentará em 1 (para incluir `nova-vaga-data-publicacao.date`). Ajustar retorno da função e os `no_update` tuples.

### 3. Implementador

- [x] Instruções suficientes para implementar cada fase sem adivinhar
- [x] Código SQL explícito para as migrações
- [x] Estrutura das notas enxutas definida
- [x] Lógica de faixa salarial (min + max → 2 inputs) clara
- [x] Todos os IDs de componentes mencionados existem ou estão sendo criados
- [x] Fallbacks documentados para cada extração (título, salário)
- [x] Estratégia de rollback com comandos exatos

**Validação final completa — documento pronto para apresentação.** ✅
