# ShopAgent Dashboard

## Visão geral

Dashboard analítico de e-commerce em Streamlit, com dados sintéticos do ShadowTraffic
armazenados em Postgres. Um agente de IA pode entrar no futuro, mas não faz parte do escopo atual.

O projeto nasceu da Semana AI Data Engineer 2026. O código original completo (agentes, RAG,
frontends e material do curso) está na tag `base-shopagent`:

```bash
git checkout base-shopagent -- caminho/do/arquivo
```

## Arquitetura

```
ShadowTraffic --> Postgres --> queries SQL --> Streamlit
```

A lógica de dados fica separada da interface. Assim, um futuro agente pode reutilizar as
mesmas queries como ferramentas, sem mexer no dashboard.

## Estado atual

O Streamlit ainda não foi implementado. Estrutura existente:

```
.env.example              # Template das variáveis do Postgres
gen/
  docker-compose.yml      # Postgres + ShadowTraffic
  shadowtraffic.json      # Geradores de dados
  init.sql                # Schema: customers, products, orders
  data/reviews/reviews.jsonl  # Avaliações em português
  license.env.example     # Template da licença do ShadowTraffic
src/
  conftest.py             # Configuração do pytest
  requirements.txt        # Desatualizado: ainda lista pacotes dos agentes
  day1/models.py          # Modelos Pydantic das 4 entidades
  day1/test_models.py     # Testes dos modelos
  day2/ledger_queries.py  # Conexão e 5 queries de negócio
spec/
  _exemplo-multi-agent/   # Exemplo de ciclo SDD (referência)
.claude/
  kb/                     # python, pydantic, shadowtraffic, supabase, testing
  agents/                 # Subagentes
  commands/               # Comandos customizados
  sdd/                    # Documentos SDD do dia 4 (referência)
  skills/                 # clarify, colorize, critique, distill, layout
```

## Estrutura planejada

```
src/
  models.py               # Vem de day1/models.py
  db.py                   # Conexão, vem de ledger_queries.py
  queries.py              # SQL dos KPIs
app/
  Home.py                 # Visão geral
  pages/                  # Vendas, produtos, clientes, avaliações
tests/
spec/streamlit-dashboard/ # Ciclo SDD do dashboard
```

## Modelo de dados

| Entidade | Armazenamento | Campos |
|----------|---------------|--------|
| customers | Postgres | customer_id, name, email, city, state, segment |
| products | Postgres | product_id, name, category, price, brand |
| orders | Postgres | order_id, customer_id (FK), product_id (FK), qty, total, status, payment, created_at |
| reviews | JSONL | review_id, order_id (FK), rating, comment, sentiment |

Valores de domínio:

- `segment`: premium, standard, basic
- `status`: delivered, shipped, processing, cancelled
- `payment`: pix, credit_card, boleto
- `sentiment`: positive, neutral, negative

## Problemas conhecidos

Resolver antes de construir as páginas que dependem deles:

- **`orders.created_at`:** o `init.sql` declara `TIMESTAMPTZ`, mas no banco atual a coluna é
  `bigint` (epoch em milissegundos). Confirme o tipo real antes de escrever filtros por data.
- **Período dos dados:** os pedidos atuais cobrem cerca de 8 minutos. Séries temporais exigem
  distribuir as datas em um período maior no `shadowtraffic.json`.
- **Avaliações:** ainda estão só no JSONL. Carregue em uma tabela `reviews` para cruzar com pedidos.
- **Porta 5432:** nesta máquina ela está ocupada por um Postgres nativo do Windows, o que impede
  o `docker compose up` com a porta padrão.
- **Dependências:** `src/requirements.txt` e `src/day2/requirements.txt` ainda precisam ser
  reduzidos à stack do dashboard.
- **Referências antigas:** `README.md` e `.claude/agents/domain/shopagent-builder.md` ainda
  descrevem o projeto original.

## Desenvolvimento local

```bash
cp .env.example .env
cd gen && cp license.env.example license.env
# Preencha a licença do ShadowTraffic em license.env
docker compose up -d
```

Para testes, na raiz do repositório:

```bash
python -m pytest src -q
```

## SDD

O ciclo tem cinco fases: brainstorm, define, design, build e ship.
Cada funcionalidade tem sua pasta em `spec/<nome>/`, com arquivos `01-brainstorm.md` a `05-ship.md`.

Os comandos `/brainstorm`, `/define`, `/design`, `/build` e `/ship` ainda não existem neste
repositório. Use `spec/_exemplo-multi-agent/` e `.claude/sdd/` como referência de formato.

## Agentes e comandos

| Agente | Uso |
|--------|-----|
| python-developer | Código Python |
| code-reviewer | Revisão de código |
| code-cleaner | Limpeza e refatoração |
| kb-architect | Criação de domínios de KB |
| meeting-analyst | Análise de reuniões, usado por `/meeting` |
| shopagent-builder | Ainda descreve o projeto original; adaptar antes de usar |

Comandos: `/meeting`, `/memory`, `/readme-maker`, `/sync-context`, `/create-kb`, `/review`.

## Convenções

- Python 3.11+ com type hints.
- SQL fica em `src/queries.py`, nunca nas páginas do Streamlit.
- Queries parametrizadas; nunca interpolar valores de filtros no SQL.
- Leituras do banco usam cache (`st.cache_data`) com TTL explícito.
- Valores exibidos em formato pt-BR (R$, datas e separadores).
- Código pronto para produção: imports reais e tratamento de erros.
- Configuração por variáveis de ambiente, sem URLs ou credenciais fixas no código.
- Módulos Python em snake_case; documentos de KB e spec em kebab-case.
- KB: concepts com menos de 150 linhas, patterns com menos de 200.
- Antes de atualizar uma KB, valide o conteúdo na documentação oficial, usando MCP quando disponível.
