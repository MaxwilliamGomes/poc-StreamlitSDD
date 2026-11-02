# Design: streamlit-dashboard

> A camada visual foi revista em `06-redesign.md`.

## Arquitetura

```
raw_dump.sql --> raw_* (cópia intocada)
                   |
reviews.jsonl --> src/prepare_data.py --> customers, products, orders, reviews
                                                     |
                                              src/queries.py (SQL)
                                                     |
                                              app/data.py (cache)
                                                     |
                     app/Home.py (roteador, filtros) --> app/pages/*
```

| Camada | Pode importar | Não pode |
|--------|---------------|----------|
| `src/` | pandas, SQLAlchemy | Importar Streamlit |
| `app/data.py` | `src`, Streamlit | Conter SQL |
| `app/pages/*` | `data`, `charts`, `components`, `src.formatting` | Conter SQL ou chamar `src.queries` |

Reaproveitamento:

| Origem | Destino | Mudança |
|--------|---------|---------|
| `src/day1/models.py` | `src/models.py` | Inclui `macro_category` |
| `src/day1/test_models.py` | `tests/test_models.py` | Ajusta imports |
| `get_connection()` de `ledger_queries.py` | `src/db.py` | Vira engine SQLAlchemy |
| Queries de `ledger_queries.py` | `src/queries.py` | Reescritas com filtros e regra de faturamento |
| KBs `streamlit`, `plotly`, `pandas` | `app/`, `src/` | Padrões de cache, filtros e pt-BR; datas usam `TIMESTAMPTZ`, não o exemplo em epoch |

## Páginas

Todas compartilham os filtros de período e estado, desenhados uma vez em `app/Home.py`.

Estados comuns:

- **Carregando:** spinner "Consultando o banco...".
- **Vazio:** `st.info("Nenhum dado para os filtros selecionados.")`, sem desenhar os gráficos.
- **Período incompleto:** aviso para escolher a data final, antes de renderizar a página.
- **Erro de banco:** mensagem única tratada no roteador, conforme **Tratamento de erros**.

### Visão geral

- **Pergunta:** como está o negócio no período, em comparação com o período anterior?
- **KPIs:** faturamento, pedidos, ticket médio e taxa de cancelamento, com variação.
- **Gráficos:** faturamento mensal em barras, como resumo.
- **Estado específico:** variação "—" sem base de comparação. Isso ocorre ao abrir o app, pois o
  filtro padrão cobre todo o período.

### Vendas

- **Pergunta:** quando e onde vendemos, e como os pedidos se distribuem?
- **Controle extra:** granularidade dia, semana ou mês, com mês como padrão.
- **Gráficos:** linha de faturamento, barras horizontais por estado, barras por status e por
  pagamento.

### Produtos

- **Pergunta:** quais produtos e macrocategorias sustentam o faturamento, e onde há cancelamento?
- **Gráficos:** top 10 produtos em barras horizontais; faturamento e taxa de cancelamento por
  macrocategoria em dois gráficos de barras.

### Clientes

- **Pergunta:** quais segmentos e estados valem mais?
- **KPIs:** clientes ativos e frequência.
- **Gráficos:** faturamento e ticket médio por segmento; faturamento e ticket médio por estado.

### Avaliações

- **Pergunta:** os clientes estão satisfeitos, e com o quê não estão?
- **KPIs:** nota média e quantidade de avaliações.
- **Gráficos:** sentimento em barras e nota média por macrocategoria.
- **Tabela:** últimos 50 comentários negativos.
- **Estado específico:** aviso de amostra pequena abaixo de 30 avaliações por grupo.

Gráficos seguem a skill `dataviz` e o helper de layout da KB `plotly`. Cores de status e sentimento
são fixas por valor.

## Queries

Todas ficam em `src/queries.py`. Salvo indicação, recebem `engine, start, end, states`.
`start` e `end` são datas inclusivas, convertidas para limites semiabertos em `America/Sao_Paulo`.
Agregação é feita no SQL; o pandas só preenche lacunas da série e calcula a variação.

| Query | KPIs | Parâmetros | Colunas retornadas |
|-------|------|------------|--------------------|
| `filter_options` | Limites dos filtros | `engine` | `states`, `min_date`, `max_date` |
| `overview_kpis` | Faturamento, Pedidos, Ticket médio, Taxa de cancelamento | Padrão | `faturamento`, `pedidos`, `ticket_medio`, `cancelados`, `total_pedidos`, `taxa_cancelamento` |
| `revenue_over_time` | Faturamento por tempo | Padrão + `grain` | `periodo`, `faturamento`, `pedidos` |
| `revenue_by_state` | Faturamento e Pedidos por estado | Padrão | `estado`, `faturamento`, `pedidos` |
| `orders_by_status` | Pedidos por status | Padrão | `status`, `pedidos` |
| `orders_by_payment` | Pedidos por pagamento | Padrão | `pagamento`, `pedidos` |
| `top_products` | Ranking de faturamento | Padrão + `limit=10` | `product_id`, `produto`, `macro_categoria`, `faturamento`, `pedidos` |
| `category_summary` | Faturamento e Taxa de cancelamento por macrocategoria | Padrão | `macro_categoria`, `faturamento`, `pedidos`, `cancelados`, `taxa_cancelamento` |
| `customers_by_segment` | Faturamento, Ticket, Clientes ativos e Frequência por segmento | Padrão | `segmento`, `faturamento`, `pedidos`, `ticket_medio`, `clientes_ativos`, `frequencia` |
| `customers_by_state` | Faturamento e Ticket por estado | Padrão | `estado`, `faturamento`, `ticket_medio` |
| `review_summary` | Nota média | Padrão | `avaliacoes`, `nota_media` |
| `sentiment_distribution` | Distribuição de sentimento | Padrão | `sentimento`, `avaliacoes`, `pct` |
| `rating_by_category` | Nota média por macrocategoria | Padrão | `macro_categoria`, `avaliacoes`, `nota_media` |
| `negative_comments` | Comentários negativos | Padrão + `limit=50` | `data`, `produto`, `macro_categoria`, `nota`, `comentario` |

Funções puras no mesmo módulo:

- `previous_period(start, end)`: devolve o intervalo de mesma duração, imediatamente anterior.
- `safe_growth(current, previous)`: devolve `None` sem base de comparação.

`grain` só aceita `day`, `week` ou `month`, validado por lista fixa antes de chegar ao SQL.
Clientes ativos no total são a soma de `clientes_ativos`, pois cada cliente tem um só segmento.

## Decisões

### Decisão 1: `st.navigation`

**Contexto:** cinco páginas compartilham filtros.
**Escolha:** `app/Home.py` é o roteador e desenha os filtros uma vez. A Visão geral vai para
`app/pages/visao_geral.py`, e os títulos ficam em `st.Page`.
**Alternativas:** pasta `pages/` automática, que redesenha filtros e depende de `persist_state`.
**Consequências:** o `CLAUDE.md` precisa ser atualizado. Não misturar com o modo automático.

### Decisão 2: tabelas `raw_*` como fonte do script

**Contexto:** o script altera a única cópia dos dados e precisa ser idempotente.
**Escolha:** na primeira execução, renomeia as tabelas originais para `raw_customers`,
`raw_products` e `raw_orders`. Toda execução apaga e recria as tabelas finais a partir delas.
**Alternativas:** `ALTER TABLE` no lugar, que não é idempotente nem reversível.
**Consequências:** cada execução produz o mesmo resultado, e a origem continua disponível.

### Decisão 3: dump versionado das tabelas originais

**Contexto:** sem licença do ShadowTraffic, os dados só existem no volume Docker. Um
`docker compose down -v` os perderia, e um clone novo ficaria sem base.
**Escolha:** gerar `gen/data/raw_dump.sql` uma vez, antes de qualquer alteração, com `pg_dump`
somente de dados e schema das três tabelas. O script restaura esse dump se não houver origem.
**Alternativas:** depender do volume, ou obter a licença.
**Consequências:** arquivo de alguns MB no repositório, sem dados pessoais reais. O caminho precisa
estar fora do `.gitignore`.

### Decisão 4: `gen/init.sql` como schema único

**Contexto:** o tipo final precisa existir em um só lugar.
**Escolha:** `prepare_data.py` executa `init.sql` depois de apagar as tabelas finais. Os testes
usam o mesmo arquivo.
**Alternativas:** DDL dentro do script, duplicando o schema.
**Consequências:** o `init.sql` deixa de ser compatível com as inserções do `shadowtraffic.json`,
pois `macro_category` é obrigatória. Regenerar com ShadowTraffic exigirá adaptação futura. O SQL do
script fica nele, pois `src/queries.py` é reservado às leituras do dashboard.

### Decisão 5: datas simuladas determinísticas

**Contexto:** o resultado precisa ser reproduzível e ter sazonalidade.
**Escolha:** período de 01/11/2025 a 31/10/2026, com `random.Random` de semente fixa e pedidos
ordenados por `order_id`. Pesos diários: 3,0 de 24 a 30/11/2025, 1,6 de 01 a 23/12/2025, 0,8 em
janeiro e fevereiro de 2026 e 1,0 no restante, multiplicados por 0,85 em fins de semana. Horário
uniforme entre 08:00 e 23:59 em `America/Sao_Paulo`.
**Alternativas:** distribuição uniforme, sem história no gráfico.
**Consequências:** a soma total não muda, e CA-08 continua válido. Valores por data são sintéticos.

### Decisão 6: ligação de avaliações

**Contexto:** nenhum `order_id` do JSONL existe em `orders`.
**Escolha:** ordenar avaliações por `review_id` e pedidos `delivered` por `order_id`, e sortear 203
pedidos distintos com a mesma semente. Os demais campos do JSONL não mudam.
**Alternativas:** escolher pedidos pela coerência entre nota e produto, sem ganho real.
**Consequências:** a relação é artificial, conforme premissa do define.

### Decisão 7: SQLAlchemy com psycopg2

**Contexto:** `pd.read_sql` precisa de engine, e o Streamlit precisa de conexão compartilhável.
**Escolha:** engine em `src/db.py`, criada por `st.cache_resource` em `app/data.py`, com
`pool_pre_ping=True` e `connect_timeout=3`. Queries usam `text()` com parâmetros nomeados.
**Alternativas:** `st.connection`, que colocaria Streamlit na camada de dados.
**Consequências:** um futuro agente pode chamar `src/queries.py` só com uma engine.

### Decisão 8: TTLs

**Contexto:** dados estáticos depois do script.
**Escolha:** KPIs com `ttl="5m"` e `max_entries=256`; opções de filtro com `ttl="1h"`.
**Alternativas:** cache sem TTL, proibido pelas convenções.
**Consequências:** depois de rodar o script, valores podem demorar até 5 minutos para mudar, salvo
reinício do app.

## Plano de migração

Executado por `python -m src.prepare_data`, em uma única transação:

1. Antes da primeira execução, gerar `gen/data/raw_dump.sql` e conferir que ele restaura.
2. Se `raw_*` não existir, renomear as tabelas atuais ou, sem elas, restaurar o dump.
3. Apagar `reviews`, `orders`, `products` e `customers` finais.
4. Executar `gen/init.sql`.
5. Inserir clientes e produtos com tipos convertidos e `macro_category`.
6. Inserir pedidos com novas datas e `total = qty * price`.
7. Carregar avaliações ligadas a pedidos `delivered`.
8. Validar contagens; qualquer divergência faz rollback.

**Reversão:** apagar as tabelas finais e renomear `raw_*` de volta. A transação cobre falhas durante
a execução.

## Manifesto de arquivos

Total: 25 arquivos criados, 3 alterados e 9 removidos. `CLAUDE.md`, KBs e `README.md` ficam para o
ship. O `.env` local é criado no build e não é versionado.

| Arquivo | Ação | Propósito | Depende de | Agente |
|---------|------|-----------|------------|--------|
| `requirements.txt` | Criar | Stack do dashboard e testes | - | python-developer |
| `pytest.ini` | Criar | `testpaths=tests`, `pythonpath=.`, marcador `integration` | - | python-developer |
| `.env.example` | Alterar | Porta 55432 | - | python-developer |
| `gen/docker-compose.yml` | Alterar | Porta com `${POSTGRES_PORT:-55432}` | - | python-developer |
| `gen/data/raw_dump.sql` | Criar | Cópia das tabelas originais | Contêiner atual | python-developer |
| `gen/init.sql` | Alterar | Schema final, com `reviews` e `macro_category` | Define | python-developer |
| `src/__init__.py` | Criar | Pacote | - | python-developer |
| `src/models.py` | Criar | Modelos, a partir de `day1/models.py` | - | python-developer |
| `src/db.py` | Criar | Engine por variáveis de ambiente | - | python-developer |
| `src/formatting.py` | Criar | Moeda, número, data, percentual e rótulos pt-BR | - | python-developer |
| `src/prepare_data.py` | Criar | Preparação da base | `db`, `init.sql`, `raw_dump.sql` | python-developer |
| `src/queries.py` | Criar | 14 queries e funções de período | `db`, `prepare_data` executado | python-developer |
| `app/data.py` | Criar | Cache e engine | `queries` | python-developer |
| `app/charts.py` | Criar | Figuras Plotly | `formatting` | python-developer |
| `app/components/filters.py` | Criar | Filtros compartilhados | `data` | python-developer |
| `app/components/ui.py` | Criar | Cards, estado vazio e aviso de amostra | `formatting` | python-developer |
| `app/Home.py` | Criar | Roteador, filtros e erro de banco | `filters` | python-developer |
| `app/pages/visao_geral.py` | Criar | Página | `data`, `charts`, `ui` | python-developer |
| `app/pages/vendas.py` | Criar | Página | `data`, `charts`, `ui` | python-developer |
| `app/pages/produtos.py` | Criar | Página | `data`, `charts`, `ui` | python-developer |
| `app/pages/clientes.py` | Criar | Página | `data`, `charts`, `ui` | python-developer |
| `app/pages/avaliacoes.py` | Criar | Página | `data`, `charts`, `ui` | python-developer |
| `tests/conftest.py` | Criar | Schema temporário e dados de teste | `init.sql` | python-developer |
| `tests/test_models.py` | Criar | Testes movidos de `day1` | `models` | python-developer |
| `tests/test_formatting.py` | Criar | Formatos pt-BR | `formatting` | python-developer |
| `tests/test_prepare_data.py` | Criar | Funções puras e resultado do script | `prepare_data` | python-developer |
| `tests/test_queries.py` | Criar | KPIs com resultado conhecido | `queries` | python-developer |
| `tests/test_architecture.py` | Criar | Limites entre camadas | - | python-developer |
| `src/conftest.py` | Remover | Substituído por `tests/conftest.py` | `tests/conftest.py` | python-developer |
| `src/requirements.txt` | Remover | Substituído pelo da raiz | `requirements.txt` | python-developer |
| `src/day1/` (4 arquivos) | Remover | Movido para `src/` e `tests/` | `src/models.py` | python-developer |
| `src/day2/` (3 arquivos) | Remover | Substituído por `db` e `queries` | `src/queries.py` | python-developer |

Ordem do build: configuração → dump → `init.sql` e `prepare_data` → `db`, `formatting`, `queries` →
testes → `app/` → remoções → revisão com code-reviewer.

## Estratégia de testes

Os testes de integração usam um schema temporário, criado com `gen/init.sql` e apagado ao final,
sem tocar em `public`. Sem banco disponível, são pulados, e o build não fecha até rodarem.

| Critério | Verificação |
|----------|-------------|
| CA-01 | `test_prepare_data`: duas execuções em schema temporário, comparando contagens e somas |
| CA-02 | `test_prepare_data`: `information_schema` e `pg_constraint` |
| CA-03 | `test_prepare_data` para contagens; SQL de conferência na base real |
| CA-04 | `test_prepare_data` para limites e pesos; SQL mensal na base real |
| CA-05 | SQL de conferência na base real |
| CA-06 | `test_prepare_data`: todos os 22 termos e categorias compostas |
| CA-07 | `test_prepare_data` e SQL de conferência na base real |
| CA-08 | `test_queries` com dados conhecidos; comparação manual da tela com os valores do define |
| CA-09 | `test_queries`: `previous_period`, `safe_growth`, `overview_kpis` |
| CA-10 | `test_queries` e verificação manual |
| CA-11 | Manual no navegador |
| CA-12 | `test_queries`: filtro de estado; manual com SP |
| CA-13 | `test_queries`: soma por grupo igual ao total |
| CA-14 | Manual no navegador, comparando com o define |
| CA-15 | `test_queries` para contagens; manual para o aviso |
| CA-16 | Manual no navegador |
| CA-17 | Manual, parando `gen-postgres-1` |
| CA-18 | `test_architecture`: `text(`, `SELECT` e `src.queries` em `app/pages` e `Home.py` |
| CA-19 | `test_architecture`: `streamlit` em `src/` |
| CA-20 | `test_formatting`; inspeção manual |
| CA-21 | `python -m pytest -q` |

`test_queries` também cobre a borda de fuso: pedido às 23:30 do último dia entra no filtro, e pedido
às 00:30 do dia seguinte não entra. RNF-07 é medido manualmente, com o cache vazio.

## Tratamento de erros

| Situação | Comportamento |
|----------|---------------|
| Banco indisponível | `Home.py` captura `sqlalchemy.exc.OperationalError`, mostra "Não foi possível conectar ao banco. Verifique se o Postgres está rodando." e interrompe a página |
| Tabelas não preparadas | `ProgrammingError` mostra a orientação de rodar `python -m src.prepare_data` |
| Variável de ambiente ausente | `src/db.py` levanta erro com o nome da variável; `Home.py` mostra a mensagem |
| Filtro sem resultado | Estado vazio em cada página |
| Falha no script | Rollback, mensagem com a etapa que falhou, saída com código diferente de zero |
| JSONL inválido | Falha antes de alterar o banco, indicando a linha |

Erros não são cacheados pelo `st.cache_data`, então a página volta a funcionar quando o banco volta.

## Configuração e dependências

Variáveis, em `.env`: `POSTGRES_HOST`, `POSTGRES_PORT=55432`, `POSTGRES_DB`, `POSTGRES_USER` e
`POSTGRES_PASSWORD`.

`requirements.txt`, com versões mínimas confirmadas na instalação:

`streamlit`, `plotly`, `pandas`, `sqlalchemy`, `psycopg2-binary`, `pydantic`, `python-dotenv`,
`tzdata` (necessário para `zoneinfo` no Windows) e `pytest`.

O ambiente global não tem Streamlit, Plotly nem SQLAlchemy, então o build usa um `.venv` na raiz.

```bash
docker compose -f gen/docker-compose.yml up -d postgres
python -m src.prepare_data
python -m streamlit run app/Home.py
```

O serviço `shadowtraffic` não é necessário e continua exigindo licença.

## Segurança

- Credenciais só no `.env`, ignorado pelo git; `src/db.py` não tem senha padrão.
- Filtros sempre como parâmetros; `grain` validado por lista fixa.
- Nome e e-mail de clientes não são lidos pelas queries do dashboard.
- Comentários são exibidos como dados em `st.dataframe`, sem Markdown nem HTML.
- App local, sem autenticação, conforme fora de escopo.

## Próximo passo

`/sdd:build streamlit-dashboard`
