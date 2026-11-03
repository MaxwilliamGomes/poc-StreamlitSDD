---
name: design
description: |
  Fase 3 do SDD: define arquitetura, páginas, queries, decisões técnicas e manifesto de arquivos
  da funcionalidade do dashboard em spec/<feature>/03-design.md.
---

# Design

Fase 3 de 5: brainstorm → define → **design** → build → ship.

## Uso

```bash
/sdd:design <feature>
```

## Regras gerais

- Exige `spec/<feature>/02-define.md` com clarity score de pelo menos 12/15.
- Não escreva código de aplicação nesta fase. Não faça commit.
- Dúvidas abertas que afetem o design precisam ser resolvidas com o usuário antes.

## Passos

1. Leia o define, `.claude/CLAUDE.md` e as KBs `streamlit`, `plotly`, `pandas` e `testing`.
   Quando existirem, abra também `docs/referencias-visuais/` e a identidade visual em `docs/`.
2. Liste o que pode ser reaproveitado do código atual.
3. Para cada página, defina a pergunta respondida, os filtros, os KPIs, os gráficos e os estados
   de carregamento, vazio e erro.
4. Associe cada KPI a uma query de `src/queries.py`. Decida o que agrega no SQL e o que fica no
   pandas.
5. Registre as decisões técnicas com alternativas e motivo.
6. Monte o manifesto de arquivos, indicando dependências e agente responsável.
7. Associe cada critério de aceite a um teste ou verificação manual.
8. Apresente as decisões para revisão.

## Regras de arquitetura

- SQL fica em `src/queries.py`, nunca nas páginas.
- Filtros chegam às queries como parâmetros.
- Leituras usam `st.cache_data` com TTL explícito.
- `src/` não importa Streamlit, para continuar reutilizável por um futuro agente.
- Mudanças de schema são listadas como etapa própria, com plano de migração.

## Documento: `spec/<feature>/03-design.md`

```markdown
# Design: <feature>

## Arquitetura
## Páginas
### <página>
Pergunta, filtros, KPIs, gráficos, estados
## Queries
| Query | KPIs | Parâmetros | Colunas retornadas |
## Decisões
### Decisão 1: <título>
Contexto, escolha, alternativas, consequências
## Manifesto de arquivos
| Arquivo | Ação | Propósito | Depende de | Agente |
## Estratégia de testes
| Critério | Verificação |
## Tratamento de erros
## Configuração e dependências
## Segurança
## Próximo passo
```

## Saída

Informe o caminho do documento, as principais decisões e a quantidade de arquivos previstos.
Próximo comando: `/sdd:build <feature>`.
