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
- Carregue as skills `poc-visual-system` e `dataviz` antes de definir páginas e gráficos.
  Não escolha forma nem cor de gráfico sem elas.
- Cumpra o nível de ambição visual do define. Não troque uma técnica exigida por uma mais simples
  sem registrar o motivo e obter o aceite do usuário.

## Passos

1. Leia o define, `.claude/CLAUDE.md` e as KBs `streamlit`, `plotly`, `pandas` e `testing`.
   Quando existirem, abra também `docs/referencias-visuais/` e a identidade visual em `docs/`.
2. Carregue a skill `poc-visual-system` e o catálogo
   `.claude/skills/poc-mockup/references/catalogo-visuais.md`.
3. Liste o que pode ser reaproveitado do código atual.
4. Para cada página, defina o arquétipo, a pergunta respondida, os filtros, os KPIs, os gráficos,
   as interações e os estados de carregamento, vazio e erro. Use o catálogo: visual permitido,
   técnica com status (existe, parcial, nova) e o que o Streamlit não faz.
   Declare também:
   - **Destaque:** o elemento que deve impressionar e a pergunta que ele responde.
   - **Técnicas do Bloco E:** as escolhidas, com status, no mínimo exigido pelo nível de ambição.
     Abaixo do mínimo, justifique por que a página não precisa delas.
   - **Critérios visuais:** quais `CA-V` do define a página atende.
5. Carregue a skill `dataviz`, escolha a forma de cada gráfico e valide a paleta com o
   `validate_palette.js` nos modos que o app oferece. Registre o resultado.
6. Associe cada KPI a uma query de `src/queries.py`. Decida o que agrega no SQL e o que fica no
   pandas.
7. No nível vitrine, o mockup é obrigatório. Nos demais, pergunte ao usuário se o cliente precisa
   aprovar um mockup antes do build. Se sim, rode a skill `poc-mockup` e use
   `spec/<feature>/mockup/mapa-construcao.md` como contrato das páginas. Se não, registre a
   decisão.
8. Registre as decisões técnicas com alternativas e motivo.
9. Monte o manifesto de arquivos, indicando dependências e agente responsável.
10. Associe cada critério de aceite, inclusive os visuais (`CA-V`), a um teste ou verificação
    manual no navegador.
11. Apresente as decisões para revisão.

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
Arquétipo, pergunta, destaque, técnicas do Bloco E (com status), critérios visuais atendidos,
filtros, KPIs, gráficos, interações, estados
## Visual
Nível de ambição, tema, paleta validada (resultado do validador), técnicas do catálogo e limites
aceitos
## Mockup
Link para `mockup/mapa-construcao.md` e status da aprovação, ou o motivo de não haver mockup
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
