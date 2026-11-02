# Ship: streamlit-dashboard

## Resumo da entrega

Dashboard Streamlit de cinco páginas sobre uma base Postgres preparada por script, com filtros de
período e estado, valores em pt-BR e testes automatizados. O ciclo fica pronto para entrega local.
Nada foi commitado, enviado ou publicado.

A revalidação deste ship encontrou e corrigiu dois problemas que o build não pegou: o passo a passo
do README falhava em um clone novo, e o `secrets.toml` não estava ignorado pelo Git.

## Checklist

- [x] Testes passando: 64 passed
- [x] Todas as páginas abrem e os filtros funcionam: 5 páginas, filtros de período e RJ
- [x] KPIs conferidos contra consulta SQL independente: globais e RJ (R$ 1.416.436,90)
- [x] Estados de vazio e erro testados: período de 2030; Postgres parado, com recuperação
- [x] Valores em formato pt-BR
- [x] Nenhuma credencial no código, e `.env` e `secrets.toml` ignorados pelo Git
- [x] `.env.example` atualizado
- [x] Requisitos atualizados
- [x] `README.md` com instruções de execução, testadas em um Postgres novo

## Critérios de aceite

Todos os 21 critérios do build seguem aprovados, sem `falhou` nem `não verificado`.

| Revalidado neste ship | Resultado |
|-----------------------|-----------|
| CA-01, CA-03, CA-05 a CA-07 | Script em um Postgres novo e na base principal, com hashes iguais |
| CA-08, CA-14 | R$ 11.856.768,69; 4.485; R$ 2.643,65; 10,3%; nota 3,11; 203 avaliações |
| CA-10 | "—" na abertura |
| CA-11, CA-12 | RJ na Visão geral igual ao SQL, após aplicar em Vendas |
| CA-16, CA-17 | Estado vazio e mensagem de erro, com recuperação |
| CA-18, CA-19, CA-21 | 64 passed |

CA-02, CA-04, CA-09, CA-13, CA-15 e CA-20 têm a evidência principal no build. Parte deles é coberta
pelos testes repetidos ou pelas telas revistas agora. Depois da última correção, `app/` não mudou e
os dados ficaram idênticos.

O código do app também não mudou depois da passagem pelo navegador; após a correção do script, a
checagem final do app foi só uma resposta HTTP 200.

## Documentação atualizada

| Arquivo | Mudança |
|---------|---------|
| `README.md` | Reescrito para o dashboard, com execução, preparação e testes |
| `.claude/CLAUDE.md` | Estado atual, arquitetura, regras de negócio e problemas conhecidos |
| `.env.example` | Porta 55432 e cabeçalho atualizados |
| `.gitignore` | Inclui `.streamlit/secrets.toml` |
| `gen/docker-compose.yml` | Porta parametrizada; `init.sql` fora da inicialização do contêiner |
| `requirements.txt` | Stack do dashboard, com versões confirmadas |

## KBs atualizadas

| KB | O que o build confirmou ou desmentiu |
|----|--------------------------------------|
| `streamlit` | Filtros no roteador `st.navigation` se mantêm entre páginas, e esse passa a ser o padrão do repo; `st.metric` aceita `delta_arrow`; `persist_state` não é usado |
| `streamlit`, `pandas`, `plotly` | `created_at` agora é `TIMESTAMPTZ`; o formato em epoch e os 8 minutos ficam só em `raw_orders` |
| `plotly` | `separators` e locale pt-BR confirmados no navegador; eixo de contagem precisa de `tickformat=",d"` |

As mudanças registram comportamento observado com Streamlit 1.66.1, Plotly 7.1.0 e pandas 3.1.0, sem
nova consulta à documentação oficial. Exemplos antigos em epoch continuam nas KBs de pandas, como
referência para o formato de origem.

## Lições aprendidas

- **Perfilar antes de especificar:** a validação no banco mostrou que nenhuma avaliação casava com
  um pedido, o que mudou a abordagem do projeto.
- **Testar o caminho de instalação:** schemas temporários não revelaram a falha de um volume novo;
  só um Postgres descartável revelou.
- **Conferir `.gitignore` por comando:** `git check-ignore` encontrou o que uma leitura deixaria
  passar.
- **O revisor precisa de contraprova:** o achado de índices não valia para a base real, e o
  `EXPLAIN` mostrou isso.
- **Automação de navegador tem falsos negativos:** digitar RJ logo após uma recarga não aplicou o
  filtro uma vez. A seleção direta funcionou, e a causa não foi investigada.

## Pendências e dívidas técnicas

| Item | Impacto |
|------|---------|
| Commit de todo o ciclo | Pendente de pedido do usuário; `gen/license.env.example` é alteração do usuário |
| Tempo de 3 s por página não cronometrado no navegador | Queries levam até 40 ms, e as páginas apareceram dentro das esperas |
| Causa da falha única ao digitar no filtro de estado | Não reproduzida; pode ser da automação ou uma corrida com a recarga |
| Filtros em cache por 1 hora | Reiniciar o app depois de rodar o script |
| `fill_time_gaps` não preenche as bordas do filtro | Zeros nas pontas não aparecem |
| `POSTGRES_PORT` não numérica mostra traceback | Erro de configuração local |
| Paleta validada só no modo claro | Tela vista no modo escuro, sem validação numérica |
| 6 de 8 macrocategorias com aviso de amostra | Consequência do limite de 30 |
| Produtos com categoria incoerente com o nome | Dados sintéticos |
| Regenerar com ShadowTraffic exige adaptação | `macro_category` obrigatória no `init.sql` |
| `shopagent-builder` descreve o projeto original | Adaptar antes de usar |

## Próximos passos

1. Revisar e commitar o ciclo na branch `chore/limpeza-dashboard`.
2. Definir o tratamento de `shadowtraffic.json`: adaptar ou aposentar.
3. Adaptar ou remover o agente `shopagent-builder`.
