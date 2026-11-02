# ShopAgent Dashboard

## Visão geral

Dashboard analítico de e-commerce em Streamlit, com dados sintéticos em Postgres. Um agente de IA pode entrar no futuro, mas não faz parte do escopo atual.

O projeto nasceu da Semana AI Data Engineer 2026. O código original completo (agentes, RAG,
frontends e material do curso) está na tag `base-shopagent`:

```bash
git checkout base-shopagent -- caminho/do/arquivo
```

## Arquitetura

```
raw_dump.sql + reviews.jsonl --> prepare_data --> Postgres --> queries SQL --> cache --> Streamlit
```

A lógica de dados fica separada da interface. Assim, um futuro agente pode reutilizar as
mesmas queries como ferramentas, sem mexer no dashboard.

## Estado atual

Primeiro ciclo SDD entregue em `spec/streamlit-dashboard/`.

```
.env.example              # Template das variáveis do Postgres
requirements.txt          # Stack do dashboard e testes
pytest.ini
app/
  Home.py                 # Roteador st.navigation, tema e erros de banco
  data.py                 # Cache e engine
  theme.py                # Tokens e CSS
  charts.py               # Figuras Plotly
  components/             # filters.py (visões salvas), ui.py, html.py
  pages/                  # visao_geral, vendas, produtos, clientes, avaliacoes
src/
  db.py                   # Engine por variáveis de ambiente
  models.py               # Modelos Pydantic
  formatting.py           # Formatos e rótulos pt-BR
  prepare_data.py         # Preparação da base
  queries.py              # SQL dos KPIs
  metrics.py              # Cálculos derivados
  insights.py             # Frases geradas dos dados
tests/
gen/
  docker-compose.yml      # Postgres (porta 55432) + ShadowTraffic
  init.sql                # Schema final
  shadowtraffic.json      # Geradores originais, sem uso no fluxo atual
  data/raw_dump.sql       # Tabelas originais
  data/reviews/reviews.jsonl  # Avaliações em português
  license.env.example     # Template da licença do ShadowTraffic
spec/
  streamlit-dashboard/    # Ciclo SDD do dashboard
  _exemplo-multi-agent/   # Exemplo de ciclo SDD (referência)
.claude/
  kb/                     # python, pydantic, shadowtraffic, supabase, testing, streamlit, plotly, pandas
  agents/                 # Subagentes
  commands/               # Comandos customizados
  sdd/                    # Documentos SDD do dia 4 (referência)
  skills/                 # clarify, colorize, critique, distill, layout
```

## Modelo de dados

| Entidade | Armazenamento | Campos |
|----------|---------------|--------|
| customers | Postgres | customer_id, name, email, city, state, segment |
| products | Postgres | product_id, name, category, macro_category, price, brand |
| orders | Postgres | order_id, customer_id (FK), product_id (FK), qty, total, status, payment, created_at |
| reviews | Postgres, origem em JSONL | review_id, order_id (FK), rating, comment, sentiment |

Valores de domínio:

- `segment`: premium, standard, basic
- `status`: delivered, shipped, processing, cancelled
- `payment`: pix, credit_card, boleto
- `sentiment`: positive, neutral, negative

## Regras de negócio

- Faturamento, pedidos e ticket médio excluem `cancelled`; status e pagamento incluem.
- A variação compara com o período imediatamente anterior, de mesma duração.
- `total` é `qty * price`. `macro_category` vem do primeiro termo de `category`.
- Médias de avaliação por grupo com menos de 30 avaliações exibem aviso.
- O painel abre na visão "Último trimestre". Valores de referência usam "Ano completo".
- Datas são agrupadas em `America/Sao_Paulo`, e `created_at` é `TIMESTAMPTZ`.

## Problemas conhecidos

- **Porta 5432:** nesta máquina ela está ocupada por um Postgres nativo do Windows. O projeto usa a
  55432.
- **ShadowTraffic:** o `init.sql` atual exige `macro_category`, então regenerar os dados exige
  adaptar o gerador. Em uma base criada pelo `init.sql` antigo, os índices de `raw_*` conflitariam
  com os nomes finais.
- **Dados sintéticos:** nomes de produto e categoria são aleatórios, e a ligação entre avaliações e
  pedidos é artificial. Em 6 de 8 macrocategorias há menos de 30 avaliações.
- **Referências antigas:** `.claude/agents/domain/shopagent-builder.md` ainda descreve o projeto
  original.

## Desenvolvimento local

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
cp .env.example .env
docker compose -f gen/docker-compose.yml up -d postgres
python -m src.prepare_data
python -m streamlit run app/Home.py
```

Rode a partir da raiz, com `python -m`: `streamlit run` direto não encontra o pacote `src`.
Reinicie o servidor ao alterar módulos importados, como `theme.py` e `charts.py`.

Para testes, na raiz do repositório:

```bash
python -m pytest -q
```

## SDD

O ciclo tem cinco fases: brainstorm, define, design, build e ship.
Cada funcionalidade tem sua pasta em `spec/<nome>/`, com arquivos `01-brainstorm.md` a `05-ship.md`.

Comandos: `/sdd:brainstorm`, `/sdd:define`, `/sdd:design`, `/sdd:build` e `/sdd:ship`, definidos em
`.claude/commands/sdd/`. Use `spec/_exemplo-multi-agent/` e `.claude/sdd/` como referência de formato.

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
- SQL de leitura fica em `src/queries.py`, nunca nas páginas do Streamlit. `app/data.py` é o único
  módulo do app que chama as queries.
- Queries parametrizadas; nunca interpolar valores de filtros no SQL.
- Leituras do banco usam cache (`st.cache_data`) com TTL explícito.
- HTML gerado passa por `components/html.py`, com `escape` em todo dado. `st.html` remove `<svg>`.
- Gráficos seguem a skill `dataviz`: paleta validada, sem dois eixos, barras até 24 px.
- Valores exibidos em formato pt-BR (R$, datas e separadores).
- Código pronto para produção: imports reais e tratamento de erros.
- Configuração por variáveis de ambiente, sem URLs ou credenciais fixas no código.
- Módulos Python em snake_case; documentos de KB e spec em kebab-case.
- KB: concepts com menos de 150 linhas, patterns com menos de 200.
- Antes de atualizar uma KB, valide o conteúdo na documentação oficial, usando MCP quando disponível.
