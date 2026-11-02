# Brainstorm: streamlit-dashboard

## Contexto

O repositório foi reduzido à base de dados do ShopAgent para virar um dashboard analítico de
e-commerce em Streamlit. Este é o primeiro ciclo SDD do projeto. Nada do Streamlit existe ainda.

Ideia original: dashboard de e-commerce com visão geral e páginas de vendas, produtos, clientes e
avaliações, com filtros por período e estado.

## Problema

Os dados da loja só podem ser consultados com SQL manual, sem uma visão única de vendas, produtos,
clientes e satisfação. Além disso, a base atual não sustenta o dashboard: ela não tem série
temporal, e as avaliações não se ligam aos pedidos.

## Usuários e decisões apoiadas

| Usuário | Decisão apoiada |
|---------|-----------------|
| Gestão comercial | Onde o faturamento cresce ou cai, por período e estado |
| Gestão de produto | Quais categorias e produtos priorizar ou rever |
| Marketing e CRM | Quais segmentos e estados merecem ação |
| Atendimento e qualidade | Quais problemas geram insatisfação |

Os dados são sintéticos: o dashboard demonstra o produto e não apoia decisões reais.

## Perguntas de negócio

**Visão geral**
1. Quanto faturamos no período, com quantos pedidos e qual ticket médio?
2. Qual é a taxa de cancelamento?
3. Como o período se compara ao período anterior?

**Vendas**
4. Como o faturamento evolui ao longo do tempo?
5. Quais estados vendem mais?
6. Como os pedidos se distribuem por status e forma de pagamento?

**Produtos**
7. Quais produtos e categorias mais faturam?
8. Quais categorias têm mais cancelamentos?

**Clientes**
9. Como faturamento e ticket médio variam por segmento e estado?
10. Quantos clientes compraram no período e com que frequência?

**Avaliações**
11. Qual é a nota média e a distribuição de sentimento?
12. Quais categorias têm as piores avaliações?
13. O que dizem os comentários negativos?

## Dados disponíveis e lacunas

Validado em 2026-11-02, com consultas de leitura no contêiner `gen-postgres-1` e leitura de
`gen/data/reviews/reviews.jsonl`.

| Tema | Encontrado | Impacto | Status |
|------|------------|---------|--------|
| Volume | 500 clientes, 200 produtos, 5000 pedidos; todos os clientes e produtos têm pedidos | Suficiente | OK |
| Integridade | Nenhum pedido órfão | Joins confiáveis | OK |
| Filtro por estado | 8 UFs, 51 a 69 clientes cada | Suficiente | OK |
| Status e pagamento | Distribuição próxima à configurada; 10,3% de cancelados | Suficiente | OK |
| `created_at` | `bigint` em epoch ms; todos os pedidos em 8 minutos de 2026-04-14 | Sem série temporal | Bloqueia |
| Avaliações | 203 linhas, **nenhuma** com `order_id` existente em `orders` | Sem cruzar avaliação com pedido | Bloqueia |
| Avaliações no banco | Não existe tabela `reviews` | Sem consulta SQL | Bloqueia |
| `category` | 118 valores para 200 produtos, em média menos de 2 por categoria | Rankings por categoria sem sentido | Bloqueia |
| `total` | Correlação de 0,036 com `qty * price`; nenhum pedido bate | Preço e faturamento não conversam | Corrigir |
| Tipos no banco | Colunas `text` e `double precision`, diferentes do `init.sql` | Dinheiro em ponto flutuante; casts em UUID | Corrigir |
| Restrições | Nenhuma PK, FK, CHECK ou índice no banco | Sem garantias; filtros por data sem índice | Corrigir |
| `city` | Cidades fictícias em inglês, sem relação com a UF | Sem análise por cidade | Fora do escopo |
| `brand` | 200 marcas em 200 produtos | Sem análise por marca | Fora do escopo |
| Clientes recorrentes | Média de 10 pedidos por cliente, em distribuição uniforme | Pergunta 10 pode dizer pouco | Risco |

Observações:

- O banco foi criado pelo ShadowTraffic, não pelo `init.sql`. Por isso há divergência em todos os
  tipos, não só em `created_at`.
- O `reviews.jsonl` não veio do `shadowtraffic.json` atual. No arquivo, nota e sentimento são
  coerentes (1-2 negativo, 3 neutro, 4-5 positivo) e há 203 comentários únicos. O gerador atual usa
  30 comentários fixos e sorteia o sentimento independentemente da nota.
- Sobre `reviews`: 203 avaliações cobrem cerca de 4% dos pedidos, volume bom para médias gerais,
  mas fraco com filtros combinados.

## Perguntas e respostas

| Pergunta | Resposta |
|----------|----------|
| Como corrigir a base? | Script Python sobre os dados atuais, sem regenerar com o ShadowTraffic |
| Cancelados entram no faturamento? | Não. Faturamento exclui `cancelled`; cancelamento aparece como taxa |
| Qual porta usar para o Postgres? | Manter 55432, configurável no `docker-compose.yml` e no `.env` |

Ficam para `/sdd:design`:

- Navegação com `pages/` ou `st.navigation`.
- Tamanho do período a simular nas datas.

## Abordagens

### A: Script de preparação + dashboard completo (selecionada)

Um script Python idempotente, com `.env` e transação, prepara a base atual:

- Cria tabelas tipadas conforme o `init.sql`, com chaves e índices.
- Converte `created_at` para `TIMESTAMPTZ` e redistribui as datas no período escolhido.
- Reduz as categorias a um conjunto pequeno e legível.
- Recalcula `total` como `qty * price`.
- Carrega `reviews.jsonl` em uma tabela `reviews`, associando cada avaliação a um pedido entregue.

Depois, o dashboard é construído sobre essa base: `src/` com conexão e queries, e `app/` com as
cinco páginas e filtros por período e estado.

**Prós:** dispensa licença, preserva os 5000 pedidos, cada correção é testável e não exige
recriar o contêiner.
**Contras:** o ShadowTraffic deixa de ser a fonte completa dos dados; regenerar a base exige
rodar o script de novo; e o `CLAUDE.md` precisa refletir a nova etapa na arquitetura.

### B: Regenerar com ShadowTraffic (não selecionada)

Ajustar o `shadowtraffic.json` e recriar tudo do zero, respeitando o `init.sql`.

**Prós:** mantém a arquitetura como está documentada.
**Contras:** exige licença, que hoje não existe em `gen/license.env`; apaga os dados atuais; e é
preciso confirmar que o gerador consegue expressar total calculado e avaliações ligadas a pedidos.

### C: Construir sobre a base atual (não selecionada)

Tratar as lacunas só nas queries e nas páginas.

**Prós:** entrega mais rápida.
**Contras:** sem série temporal, sem cruzar avaliações com pedidos e sem categorias úteis. Não
responde às perguntas 3, 4, 8, 12 e nem usa de verdade o filtro por período.

## YAGNI

- Agente de IA e chat sobre os dados.
- Atualização em tempo real e streaming de pedidos.
- Autenticação, perfis de acesso e deploy.
- Exportação de PDF ou Excel.
- Análises por cidade e por marca.
- NLP nos comentários: o `sentiment` já vem no dado.
- Metas, previsão e coorte de clientes.
- Testes de interface: `AppTest` só se o design justificar.

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Script altera a única cópia dos dados | Criar tabelas novas antes de trocar as antigas; transação; idempotência testada |
| Dados uniformes geram gráficos sem história | Incluir sazonalidade simples na distribuição de datas |
| Associação de avaliações é artificial | Documentar a decisão; ligar só a pedidos entregues |
| Recalcular `total` muda os valores deste documento | Definir os KPIs depois do script e validar neles |
| Poucas avaliações sob filtros combinados | Definir estado vazio e aviso de amostra pequena |
| `CLAUDE.md` e KBs presumem `created_at` em `bigint` | Atualizar no ship; KBs já tratam os dois tipos |
| Porta 55432 não está no `docker-compose.yml` | Parametrizar no design |

## Próximo passo

`/sdd:define streamlit-dashboard`
