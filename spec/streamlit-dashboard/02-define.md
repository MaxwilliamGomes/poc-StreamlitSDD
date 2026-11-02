# Define: streamlit-dashboard

## Problema

Os dados da loja só podem ser consultados com SQL manual, e a base atual não sustenta um dashboard:
não há série temporal, as avaliações não se ligam aos pedidos e as categorias estão fragmentadas.
A entrega tem duas partes: preparar a base com um script Python e construir um dashboard Streamlit
de cinco páginas, com filtros por período e estado.

## Usuários

| Usuário | Decisão apoiada | Páginas |
|---------|-----------------|---------|
| Gestão comercial | Onde o faturamento cresce ou cai | Visão geral, Vendas |
| Gestão de produto | Quais categorias e produtos priorizar | Produtos |
| Marketing e CRM | Quais segmentos e estados merecem ação | Clientes |
| Atendimento e qualidade | Quais problemas geram insatisfação | Avaliações |

Os usuários são perfis presumidos: os dados são sintéticos e o dashboard demonstra o produto.

## Requisitos funcionais

### Preparação da base

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-01 | Script Python idempotente cria `customers`, `products`, `orders` e `reviews` com tipos, chaves e índices do contrato de dados | Must |
| RF-02 | Preservar 500 clientes, 200 produtos, 5000 pedidos e os valores de `status` e `payment` | Must |
| RF-03 | Redistribuir `created_at` no período simulado, em `TIMESTAMPTZ`, com sazonalidade simples | Must |
| RF-04 | Recalcular `orders.total` como `qty * price` do produto | Must |
| RF-05 | Atribuir a cada produto uma macrocategoria pelo primeiro termo de `category`, conforme o mapeamento abaixo | Must |
| RF-06 | Carregar as 203 linhas de `reviews.jsonl` em `reviews`, ligando cada avaliação a um pedido `delivered` distinto | Must |

Mapeamento de macrocategorias, confirmado pelo usuário em 2026-11-02:

| Macrocategoria | Primeiro termo de `category` |
|----------------|------------------------------|
| Moda | Clothing, Shoes, Jewelry |
| Beleza e Saúde | Beauty, Health |
| Casa e Mercado | Home, Garden, Tools, Grocery |
| Tecnologia | Computers, Electronics |
| Entretenimento | Books, Games, Movies, Music |
| Infantil | Baby, Kids, Toys |
| Esporte e Lazer | Sports, Outdoors |
| Automotivo e Indústria | Automotive, Industrial |

### Dashboard

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-07 | Filtros de período e estado na barra lateral, aplicados a todas as páginas e mantidos na navegação | Must |
| RF-08 | Visão geral: faturamento, pedidos, ticket médio e taxa de cancelamento, cada um com variação | Must |
| RF-09 | Vendas: evolução do faturamento, faturamento por estado, pedidos por status e por pagamento | Must |
| RF-10 | Produtos: ranking de 10 produtos por faturamento, faturamento e taxa de cancelamento por macrocategoria | Must |
| RF-11 | Clientes: faturamento e ticket médio por segmento e estado; clientes ativos e frequência | Should |
| RF-12 | Avaliações: nota média, distribuição de sentimento, nota por macrocategoria e lista de comentários negativos | Must |
| RF-13 | Exibir aviso de amostra pequena em médias de avaliação com menos de 30 avaliações | Should |
| RF-14 | Exibir estado vazio quando o filtro não retorna dados, sem erro | Must |
| RF-15 | Exibir mensagem clara quando o banco está indisponível, sem stack trace | Must |

## Requisitos não funcionais

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RNF-01 | SQL só em `src/queries.py`, com queries parametrizadas | Must |
| RNF-02 | Leituras com `st.cache_data` e TTL explícito | Must |
| RNF-03 | `src/` sem dependência de Streamlit, para reuso futuro por um agente | Must |
| RNF-04 | Valores em pt-BR: R$, datas `dd/mm/aaaa`, separadores, rótulos de domínio traduzidos | Must |
| RNF-05 | Datas agrupadas no fuso `America/Sao_Paulo` | Must |
| RNF-06 | Configuração por variáveis de ambiente; Postgres na porta 55432, configurável em `docker-compose.yml` e `.env` | Must |
| RNF-07 | Página carrega em até 3 s, com cache vazio, na base local de 5000 pedidos | Should |
| RNF-08 | Dependências reduzidas à stack do dashboard | Should |
| RNF-09 | Testes do script e das queries com `pytest` | Must |

## Catálogo de KPIs

**Base de faturamento:** pedidos com `status <> 'cancelled'`, ou seja, `delivered`, `shipped` e
`processing`.

Salvo indicação, os filtros são período (`orders.created_at`) e estado (`customers.state`). Avaliações
herdam data e estado do pedido ligado.

| KPI | Fórmula | Filtros | Granularidade | Origem |
|-----|---------|---------|---------------|--------|
| Faturamento | `SUM(total)` da base de faturamento | Período, estado | Total, dia/semana/mês, estado, macrocategoria, segmento | `orders`, `customers`, `products` |
| Pedidos | `COUNT(*)` da base de faturamento | Período, estado | Total, estado | `orders`, `customers` |
| Ticket médio | Faturamento / Pedidos | Período, estado | Total, segmento, estado | `orders`, `customers` |
| Taxa de cancelamento | `cancelled` / todos os pedidos | Período, estado | Total, macrocategoria | `orders`, `customers`, `products` |
| Variação | (Atual − anterior) / anterior; período anterior tem a mesma duração e termina logo antes do início do filtro | Período, estado | Total | Mesmos do KPI |
| Pedidos por status | `COUNT(*)` por `status`, incluindo `cancelled` | Período, estado | Status | `orders`, `customers` |
| Pedidos por pagamento | `COUNT(*)` por `payment`, incluindo `cancelled` | Período, estado | Forma de pagamento | `orders`, `customers` |
| Clientes ativos | `COUNT(DISTINCT customer_id)` da base de faturamento | Período, estado | Total, segmento | `orders`, `customers` |
| Frequência | Pedidos / Clientes ativos | Período, estado | Total, segmento | `orders`, `customers` |
| Nota média | `AVG(rating)` | Período, estado | Total, macrocategoria | `reviews`, `orders`, `customers`, `products` |
| Distribuição de sentimento | `COUNT(*)` por `sentiment` e % do total | Período, estado | Sentimento | `reviews`, `orders`, `customers` |

Regras complementares:

- Variação sem base (anterior zero ou sem dados) é exibida como "—", nunca como 0% ou infinito.
- O filtro de período inclui as duas datas, no fuso `America/Sao_Paulo`.
- Pedidos cancelados continuam nos gráficos de status e pagamento, mas não no faturamento.

## Contrato de dados

Tipos conferidos no banco `gen-postgres-1` em 2026-11-02. O banco não tem PK, FK, CHECK nem índices.

| Tabela | Coluna | Tipo real | Tipo final | Uso |
|--------|--------|-----------|------------|-----|
| customers | customer_id | text | UUID, PK | Join |
| customers | name | text | VARCHAR(255) | Não exibido |
| customers | email | text | VARCHAR(255) | Não exibido |
| customers | city | text | VARCHAR(100) | Não usado: cidades fictícias |
| customers | state | text | CHAR(2) | Filtro, agrupamento |
| customers | segment | text | VARCHAR(20), CHECK | Agrupamento |
| products | product_id | text | UUID, PK | Join; chave do ranking, pois há 195 nomes em 200 produtos |
| products | name | text | VARCHAR(255) | Ranking |
| products | category | text | VARCHAR(100) | Origem da macrocategoria |
| products | macro_category | não existe | VARCHAR(50) NOT NULL | Agrupamento |
| products | price | double precision | DECIMAL(10,2), CHECK > 0 | Cálculo de `total` |
| products | brand | text | VARCHAR(100) | Não usado |
| orders | order_id | text | UUID, PK | Join |
| orders | customer_id | text | UUID, FK | Join |
| orders | product_id | text | UUID, FK | Join |
| orders | qty | double precision (inteiros de 1 a 9) | INTEGER, CHECK de 1 a 10 | Cálculo de `total` |
| orders | total | double precision | DECIMAL(10,2) NOT NULL | Faturamento; `qty * price` |
| orders | status | text | VARCHAR(20), CHECK | Filtro de faturamento, agrupamento |
| orders | payment | text | VARCHAR(20), CHECK | Agrupamento |
| orders | created_at | bigint (epoch ms) | TIMESTAMPTZ NOT NULL | Filtro, série temporal |
| reviews | review_id | só no JSONL | UUID, PK | Identificador |
| reviews | order_id | só no JSONL, sem pedido correspondente | UUID, FK, UNIQUE | Join, após nova ligação |
| reviews | rating | só no JSONL | SMALLINT, CHECK de 1 a 5 | Nota média |
| reviews | comment | só no JSONL | TEXT | Lista de comentários |
| reviews | sentiment | só no JSONL | VARCHAR(20), CHECK | Distribuição |

Perfil atual: sem nulos nas colunas usadas, sem IDs duplicados e sem pedidos órfãos. O `init.sql`
precisa ser alinhado ao tipo final, incluindo `reviews` e `macro_category`.

## Critérios de aceite

Valores globais valem após o script, sem filtros. Foram calculados sobre os dados atuais com
`qty * price` e dependem de os preços e as quantidades não mudarem.

| ID | Requisito | Como verificar | Resultado esperado |
|----|-----------|----------------|--------------------|
| CA-01 | RF-01 | Rodar o script duas vezes e comparar contagens e somas | Mesmo resultado nas duas execuções |
| CA-02 | RF-01 | Consultar `information_schema` e `pg_constraint` | Tipos, chaves, CHECKs e índices conforme o contrato |
| CA-03 | RF-02 | `COUNT(*)` por tabela e por `status` | 500, 200, 5000; delivered 2514, shipped 1011, processing 960, cancelled 515 |
| CA-04 | RF-03 | `MIN` e `MAX` de `created_at`, e pedidos por mês | Datas no período simulado, com todos os meses preenchidos |
| CA-05 | RF-04 | Pedidos com `total <> qty * price` | 0 pedidos |
| CA-06 | RF-05 | Macrocategorias distintas e nulas | Até 8 valores, 0 nulos |
| CA-07 | RF-06 | Contar `reviews` e juntar com `orders` | 203 linhas, 0 órfãs, todas em pedidos `delivered`, sem `order_id` repetido |
| CA-08 | RF-08 | Comparar a Visão geral sem filtro com SQL | Faturamento R$ 11.856.768,69; 4.485 pedidos; ticket R$ 2.643,65; cancelamento 10,3% |
| CA-09 | RF-08 | Filtrar um período com dados no período anterior e conferir à mão | Variações iguais à fórmula do catálogo |
| CA-10 | Regras de KPI | Filtrar o primeiro dia dos dados | Variação exibida como "—" |
| CA-11 | RF-07 | Trocar de página após filtrar | Filtros mantidos e aplicados |
| CA-12 | RF-07 | Filtrar por SP e comparar faturamento com SQL | Valores iguais |
| CA-13 | RF-09, RF-10, RF-11 | Comparar cada gráfico com a query correspondente | Valores iguais; soma por estado igual ao total |
| CA-14 | RF-12 | Abrir Avaliações sem filtro | Nota média 3,11; 71 positivas, 61 neutras, 71 negativas |
| CA-15 | RF-13 | Ver nota por macrocategoria com menos de 30 avaliações | Aviso visível ao lado do valor |
| CA-16 | RF-14 | Filtrar um período sem pedidos | Mensagem de estado vazio, sem erro |
| CA-17 | RF-15 | Parar o Postgres e abrir o dashboard | Mensagem clara, sem stack trace |
| CA-18 | RNF-01 | Buscar SQL em `app/` | Nenhuma ocorrência |
| CA-19 | RNF-03 | Buscar `streamlit` em `src/` | Nenhuma ocorrência |
| CA-20 | RNF-04 | Inspecionar valores na tela | R$ 1.234,56 e 31/12/2026; rótulos em português |
| CA-21 | RNF-09 | `python -m pytest -q` | Todos os testes passam |

## Fora de escopo

- Agente de IA e chat sobre os dados.
- Atualização em tempo real e streaming.
- Autenticação, perfis de acesso e deploy.
- Exportação de PDF ou Excel.
- Análises por cidade e por marca.
- NLP nos comentários.
- Metas, previsão e coortes.
- Regeneração dos dados com ShadowTraffic.

## Restrições

- Python 3.11+, Streamlit, Plotly, pandas e Postgres local em Docker.
- Porta 55432; o Postgres nativo do Windows não é alterado.
- Uso do `.env`, que ainda não existe e precisa ser criado a partir do `.env.example`.
- Convenções do `.claude/CLAUDE.md`.

## Premissas

- `processing` e `shipped` contam como faturamento, pois só `cancelled` foi excluído.
- O relacionamento entre avaliação e pedido é artificial: a ligação original não existe.
- Avaliações ficam só em pedidos `delivered`, pois presumem produto recebido.
- Sem seleção do usuário, os filtros cobrem todo o período e todos os estados. Revogada em
  `06-redesign.md`: o app abre em "Último trimestre", e CA-08 e CA-14 usam "Ano completo".
- O limite de 30 avaliações vale para médias por grupo, não para a média geral.

## Dúvidas abertas

Resolvidas na fase de design: período simulado de 12 meses e navegação com `st.navigation`.

| Dúvida | Quem resolve | Impacto |
|--------|--------------|---------|
| Manter o limite de 30? Com 203 avaliações em 8 grupos, a média é de 25 por grupo, e a maioria deve exibir aviso | Usuário, se incomodar no build | RF-13, CA-15 |

## Clarity score

| Critério | Nota | Justificativa |
|----------|------|---------------|
| Problema | 3 | Dor e decisões claras |
| Usuários | 2 | Perfis presumidos, sem usuários reais |
| Requisitos | 3 | Testáveis e priorizados |
| KPIs e dados | 2 | Fórmulas fechadas; faltam mapeamento e período simulado |
| Escopo | 3 | Fora de escopo e restrições explícitos |
| **Total** | **13/15** | Acima do mínimo de 12 |

## Próximo passo

`/sdd:design streamlit-dashboard`
