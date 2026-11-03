---
name: define
description: |
  Fase 2 do SDD: transforma o brainstorm em requisitos testáveis, catálogo de KPIs e contrato
  de dados em spec/<feature>/02-define.md, com clarity score mínimo de 12/15.
---

# Define

Fase 2 de 5: brainstorm → **define** → design → build → ship.

## Uso

```bash
/sdd:define <feature>
```

## Regras gerais

- Exige `spec/<feature>/01-brainstorm.md`. Se não existir, pare e indique `/sdd:brainstorm`.
- Não escreva código de aplicação nesta fase. Não faça commit.
- Não invente regra de negócio. Pergunte ao usuário ou registre em **Dúvidas abertas**.
- Não invente o nível de ambição visual: leia em `docs/visao-projeto.md` ou pergunte ao usuário.

## Nível de ambição visual

| Nível | Quando usar | O que passa a ser exigido |
|-------|-------------|---------------------------|
| Sóbrio | Uso interno, operação, painel de conferência | Títulos-insight e clareza; técnicas do catálogo são opcionais |
| Profissional (padrão) | Gestão e entrega ao cliente | Por página: 1 destaque declarado e pelo menos 1 técnica do Bloco E do catálogo. No define: pelo menos 2 critérios de aceite visuais |
| Vitrine | Demonstração comercial, diretoria, "uau" | Por página: 1 destaque e pelo menos 2 técnicas do Bloco E, sendo 1 com status nova ou parcial. Mockup obrigatório. No define: pelo menos 1 critério de aceite visual por página |

O catálogo fica em `.claude/skills/poc-mockup/references/catalogo-visuais.md`.

## Passos

1. Leia o brainstorm e `.claude/CLAUDE.md`.
2. Escreva requisitos funcionais (`RF-01`) e não funcionais (`RNF-01`), com prioridade MoSCoW.
3. Defina cada KPI com fórmula, filtros, granularidade e origem. Deixe explícitas regras como
   a inclusão ou não de pedidos cancelados no faturamento.
4. Confira o contrato de dados com o schema real, não apenas com `init.sql`.
5. Escreva critérios de aceite (`CA-01`) verificáveis, com valor esperado ou consulta de
   conferência quando possível.
6. Registre o nível de ambição visual e escreva os critérios de aceite visuais (`CA-V01`) que o
   nível exige. Cada um descreve um comportamento observável no app, não um gosto. Exemplos: "o
   usuário troca a métrica sem sair do cartão e título, eixo e tabela acompanham"; "o clique no
   mês abre o detalhe diário"; "o diretor identifica em 10 s a região com maior queda".
7. Calcule o clarity score. Abaixo de 12/15, resolva as lacunas com o usuário antes de concluir.

## Clarity score

Avalie cada critério de 0 a 3:

| Critério | 3 significa |
|----------|-------------|
| Problema | Dor e decisão apoiada são claras |
| Usuários | Quem usa e como é conhecido |
| Requisitos | Todos são testáveis e priorizados |
| KPIs e dados | Fórmulas e origem estão fechadas |
| Escopo | Fora de escopo e restrições estão explícitos |

## Documento: `spec/<feature>/02-define.md`

```markdown
# Define: <feature>

## Problema
## Usuários
## Requisitos funcionais
| ID | Requisito | Prioridade |
## Requisitos não funcionais
## Catálogo de KPIs
| KPI | Fórmula | Filtros | Granularidade | Origem |
## Contrato de dados
| Tabela | Coluna | Tipo real | Uso |
## Ambição visual
Nível, motivo e o que ele exige
## Critérios de aceite
| ID | Requisito | Como verificar | Resultado esperado |
## Critérios de aceite visuais
| ID | Página | Comportamento esperado | Como verificar |
## Fora de escopo
## Restrições
## Premissas
## Dúvidas abertas
## Clarity score
## Próximo passo
```

## Saída

Informe o caminho do documento, o clarity score e as dúvidas abertas.
Próximo comando: `/sdd:design <feature>`.
