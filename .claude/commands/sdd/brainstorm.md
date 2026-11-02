---
name: brainstorm
description: |
  Fase 1 do SDD: explora o problema de uma funcionalidade do dashboard, compara abordagens
  e registra a escolhida em spec/<feature>/01-brainstorm.md.
---

# Brainstorm

Fase 1 de 5: **brainstorm** → define → design → build → ship.

## Uso

```bash
/sdd:brainstorm <feature> <descrição da ideia>
```

Exemplo: `/sdd:brainstorm streamlit-dashboard Visão geral de vendas com filtros por período e estado`

## Regras gerais

- `<feature>` usa kebab-case e define a pasta `spec/<feature>/`.
- Sem `<feature>` ou descrição, peça o que falta antes de continuar.
- Se `01-brainstorm.md` já existir, pergunte se deve revisar ou substituir.
- Não escreva código de aplicação nesta fase. Não faça commit.

## Passos

1. Leia `.claude/CLAUDE.md`, em especial **Problemas conhecidos**.
2. Consulte o que já existe: `gen/init.sql`, `gen/shadowtraffic.json`, os modelos, as queries e
   as KBs relevantes em `.claude/kb/`.
3. Confirme no banco, quando ele estiver disponível, se os dados sustentam a ideia. Use apenas
   consultas de leitura.
4. Identifique as perguntas de negócio que o dashboard deve responder.
5. Faça ao usuário apenas as perguntas cuja resposta mude a solução, no máximo 5.
6. Compare de 2 a 3 abordagens e recomende uma.
7. Corte o que não é necessário agora e registre em **YAGNI**.
8. Escreva o documento e apresente um resumo.

## Documento: `spec/<feature>/01-brainstorm.md`

```markdown
# Brainstorm: <feature>

## Contexto
## Problema
## Usuários e decisões apoiadas
## Perguntas de negócio
## Dados disponíveis e lacunas
## Perguntas e respostas
## Abordagens
### A: <nome> (selecionada)
### B: <nome> (não selecionada)
## YAGNI
## Riscos
## Próximo passo
```

## Saída

Informe o caminho do documento, a abordagem escolhida e as dúvidas abertas.
Próximo comando: `/sdd:define <feature>`.
