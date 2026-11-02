# Build: streamlit-dashboard

## Resumo

Base do `public` migrada e dashboard de cinco páginas implementado, com filtros de período e estado.
Todos os 21 critérios de aceite foram aprovados. Nada foi commitado.

A migração e a remoção dos arquivos antigos foram autorizadas pelo usuário em 2026-11-02. As tabelas
originais continuam em `raw_*` e em `gen/data/raw_dump.sql`.

## Manifesto

| Arquivo | Status | Observações |
|---------|--------|-------------|
| `requirements.txt` | Criado | Versões confirmadas na instalação |
| `pytest.ini` | Criado | |
| `.env.example` | Alterado | Porta 55432 |
| `gen/docker-compose.yml` | Alterado | Porta parametrizada |
| `gen/data/raw_dump.sql` | Criado | 1,1 MB; restauração testada em banco descartável |
| `gen/init.sql` | Alterado | Schema final |
| `src/__init__.py`, `src/models.py`, `src/db.py`, `src/formatting.py` | Criados | |
| `src/prepare_data.py` | Criado | Executado duas vezes no `public` |
| `src/queries.py` | Criado | 14 queries e 3 funções puras |
| `app/data.py`, `app/charts.py`, `app/Home.py` | Criados | |
| `app/components/filters.py`, `app/components/ui.py` | Criados | |
| `app/pages/*.py` (5) | Criados | |
| `tests/*.py` (6) | Criados | |
| `src/conftest.py`, `src/requirements.txt`, `src/day1/`, `src/day2/` | Removidos | 9 arquivos, disponíveis na tag `base-shopagent` |

## Desvios do design

| Desvio | Motivo |
|--------|--------|
| Incluída `fill_time_gaps` em `src/queries.py` | Mantém o preenchimento de lacunas fora da camada de páginas |
| Incluída `load_overview_comparison` em `app/data.py` | Páginas não podem chamar `src.queries` |
| Cores de status e sentimento usam a paleta da skill `dataviz` | Validada pelo script; aviso de contraste atendido por rótulos visíveis |
| Sem helper separado `charts_base.py` | Layout compartilhado cabe em `app/charts.py` |

## Verificação

| Comando ou ação | Resultado |
|-----------------|-----------|
| `python -m pytest -q` | 62 passed |
| `python -m src.prepare_data`, duas vezes | Mesmas contagens, somas e hashes de datas e avaliações |
| SQL independente, KPIs globais | Iguais ao define |
| SQL independente, 7 agrupamentos dos gráficos | Todos iguais |
| Filtro SP + março/2026 no navegador | KPIs e variações iguais ao SQL |
| Navegador, 5 páginas | Sem erro no console |
| Postgres parado com instância sem cache | Mensagem clara; a página voltou após religar o banco |
| `EXPLAIN` de filtro por data | Usa `idx_orders_created_at` |
| `validate_palette.js` | Passa; contraste com WARN, atendido por rótulos |
| Tempo das queries por página, sem cache | De 13 a 40 ms |
| `code-reviewer` | Sem defeito nas regras de negócio; achados abaixo |

RNF-07: o tempo de 3 s não foi cronometrado no navegador. As páginas apareceram dentro das esperas
de 3 s usadas na validação, e as queries somam no máximo 40 ms.

## Critérios de aceite

| ID | Status | Evidência |
|----|--------|-----------|
| CA-01 | aprovado | Duas execuções no `public` com hashes iguais; teste em schema temporário |
| CA-02 | aprovado | `information_schema`: uuid, numeric, integer, timestamptz; 4 PK, 3 FK, 1 UNIQUE, 8 CHECK; 6 índices |
| CA-03 | aprovado | 500, 200, 5000; 2514, 1011, 960, 515 |
| CA-04 | aprovado | Dados de 01/11/2025 a 31/10/2026 no fuso local, 12 meses com 313 a 581 pedidos |
| CA-05 | aprovado | 0 divergências |
| CA-06 | aprovado | 8 macrocategorias, 0 nulos |
| CA-07 | aprovado | 203 linhas, 203 pedidos distintos, todas em `delivered` |
| CA-08 | aprovado | R$ 11.856.768,69; 4.485; R$ 2.643,65; 10,3% na tela e no SQL |
| CA-09 | aprovado | SP em março: -4,9%, +48,1%, -35,8%, -81,0%, iguais ao SQL |
| CA-10 | aprovado | "—" ao abrir com início no primeiro dia dos dados |
| CA-11 | aprovado | Filtro SP mantido de Avaliações para Visão geral |
| CA-12 | aprovado | SP: R$ 1.181.597,69 na tela e no SQL |
| CA-13 | aprovado | 7 agrupamentos iguais ao SQL; testes de soma por grupo |
| CA-14 | aprovado | Nota 3,11; 71, 61 e 71 no SQL e no gráfico |
| CA-15 | aprovado | ⚠ ao lado do valor em 6 de 8 macrocategorias |
| CA-16 | aprovado | Período de 2030 exibe estado vazio |
| CA-17 | aprovado | Mensagem de erro, sem stack trace |
| CA-18 | aprovado | `test_architecture` |
| CA-19 | aprovado | `test_architecture` |
| CA-20 | aprovado | R$ e datas pt-BR na tela; `test_formatting` |
| CA-21 | aprovado | 62 passed |

## Problemas encontrados

Corrigidos:

| Problema | Correção |
|----------|----------|
| Dump esvaziava o `search_path` da sessão | Valor restaurado depois do dump; teste adicionado |
| Eixos de contagem sem separador de milhar | `tickformat=",d"` |
| `ProgrammingError` era sempre tratado como tabela ausente | Só `UndefinedTable`; o resto aparece como erro real |
| Mensagem de conexão ignorava credenciais | Texto cita o `.env` |

Conhecidos, sem correção neste ciclo:

| Problema | Impacto |
|----------|---------|
| Com banco criado pelo `init.sql` antigo, os índices de `raw_*` manteriam os nomes, e `IF NOT EXISTS` não criaria os finais | Não ocorre na base atual nem a partir do dump; só em base antiga |
| Filtros ficam em cache por 1 hora | Depois de rodar o script, reinicie o app se o período mudar |
| `fill_time_gaps` só preenche entre o primeiro e o último período com dados | Zeros nas bordas do filtro não aparecem |
| `POSTGRES_PORT` não numérica mostra traceback | Erro de configuração local |
| Macrocategoria usa o primeiro termo de uma categoria sintética | Produtos como "Synergistic Silk Pants" caem em Entretenimento |
| 6 de 8 macrocategorias exibem aviso de amostra pequena | Consequência do limite de 30 |
| Regenerar com ShadowTraffic exige adaptar o `init.sql` | Decisão 4 do design |
| Tela segue o tema do navegador; paleta validada só no modo claro | Validação visual feita no modo escuro |

## Como executar

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
cp .env.example .env
docker compose -f gen/docker-compose.yml up -d postgres
python -m src.prepare_data
python -m streamlit run app/Home.py
```

Use `python -m streamlit`, na raiz: `streamlit run` direto não encontra o pacote `src`.

## Correção no ship

O caminho de clone novo falhava, porque o `init.sql` montado no contêiner criava tabelas vazias.
O `init.sql` saiu da inicialização do Postgres, e `ensure_raw_tables` agora restaura o dump quando a
origem está vazia e recusa origem parcial. Com dois testes novos, o total passou de 62 para 64.
Detalhes em `05-ship.md`.

## Próximo passo

`/sdd:ship streamlit-dashboard`
