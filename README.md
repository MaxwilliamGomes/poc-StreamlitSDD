# ShopAgent Dashboard

Dashboard analítico de e-commerce em Streamlit, com dados sintéticos em Postgres. Responde a
perguntas sobre vendas, produtos, clientes e avaliações, com filtros por período e estado.

O projeto nasceu da Semana AI Data Engineer 2026. O código original, com agentes e RAG, está na tag
`base-shopagent`.

## Páginas

| Página | Conteúdo |
|--------|----------|
| Visão geral | KPIs com sparkline, insights, atual vs. anterior, heatmap de horários e estados |
| Vendas | Evolução, variação por estado, mix de pagamento e painel condicional por estado |
| Produtos | Top e Bottom 10, cancelamento contra a média e matriz macrocategoria × estado |
| Clientes | Ativos, frequência de compra, segmentos e estados |
| Avaliações | Nota, sentimento, distribuição, sentimento por macrocategoria e comentários |

O faturamento exclui pedidos cancelados. A variação compara com o período imediatamente anterior, de
mesma duração, e aparece como "—" quando não há base de comparação.

As visões salvas aplicam período e estados de uma vez, e clicar em uma barra de estado filtra o
painel. O app abre em "Último trimestre".

## Arquitetura

```text
raw_dump.sql --> raw_* --> src/prepare_data.py --> customers, products, orders, reviews
reviews.jsonl ------------------^                              |
                                               src/queries.py --> app/data.py --> app/
```

O SQL fica em `src/queries.py`, sem dependência de Streamlit, para ser reutilizado por um futuro
agente. A camada `app/` adiciona cache e interface.

## Como executar

Pré-requisitos: Docker e Python 3.11+. Rode tudo na raiz do repositório.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Linux/macOS: .venv/bin/python
cp .env.example .env
docker compose -f gen/docker-compose.yml up -d postgres
python -m src.prepare_data
python -m streamlit run app/Home.py
```

Ative o `.venv` antes dos comandos `python`. O Postgres usa a porta 55432, configurável com
`POSTGRES_PORT` no `.env`. Use `python -m streamlit`: `streamlit run` direto não encontra o pacote
`src`. O ShadowTraffic não é necessário, e os dados de origem estão em `gen/data/raw_dump.sql`.

## Preparação dos dados

`python -m src.prepare_data` roda em uma transação e pode ser repetido com o mesmo resultado. O
script:

- preserva as tabelas originais como `raw_*`, restaurando o dump quando não existem;
- aplica o schema de `gen/init.sql`;
- distribui as datas de 01/11/2025 a 31/10/2026, com semente fixa e sazonalidade simples;
- calcula `total` como `qty * price`;
- agrupa as categorias em 8 macrocategorias;
- liga as 203 avaliações a pedidos entregues.

As ligações entre avaliações e pedidos são artificiais, pois o arquivo original não corresponde aos
pedidos. Depois de rodar o script, reinicie o app para atualizar os limites dos filtros.

## Testes

```bash
python -m pytest -q
```

Os testes de integração usam um schema temporário no Postgres local, sem tocar em `public`, e são
pulados se o banco estiver indisponível.

## Estrutura

```text
app/                 # Home.py (roteador), theme.py, data.py, charts.py, components/, pages/
src/                 # db, models, formatting, prepare_data, queries, metrics, insights
tests/
gen/                 # docker-compose, init.sql, dump e avaliações
spec/                # Ciclos SDD
.claude/             # Agentes, comandos e bases de conhecimento
```
