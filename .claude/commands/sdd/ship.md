---
name: ship
description: |
  Fase 5 do SDD: revalida a funcionalidade, atualiza documentação e KBs, registra aprendizados
  e encerra o ciclo em spec/<feature>/05-ship.md.
---

# Ship

Fase 5 de 5: brainstorm → define → design → build → **ship**.

## Uso

```bash
/sdd:ship <feature>
```

## Regras gerais

- Exige `spec/<feature>/04-build.md` sem critérios obrigatórios com falha.
- Critérios `não verificado` só passam com aceite explícito do usuário.
- Revalide agora; não reaproveite resultados antigos do build.
- Não faça commit, push, merge ou deploy sem pedido do usuário.

## Passos

1. Rode os testes e suba o app para uma verificação final.
2. Preencha o checklist.
3. Atualize `README.md`, `.env.example` e os requisitos, se a funcionalidade os mudou.
4. Atualize `.claude/CLAUDE.md`: mova o que foi feito de **Estrutura planejada** para
   **Estado atual** e remova os problemas resolvidos.
5. Registre nas KBs o que o build confirmou ou desmentiu, ajustando as notas de validação.
6. Escreva o documento e apresente o resultado.

## Checklist

- [ ] Testes passando
- [ ] Todas as páginas abrem e os filtros funcionam
- [ ] KPIs conferidos contra consulta SQL independente
- [ ] Estados de vazio e erro testados
- [ ] Valores em formato pt-BR
- [ ] Nenhuma credencial no código, e `.env` e `secrets.toml` ignorados pelo Git
- [ ] `.env.example` atualizado
- [ ] Requisitos atualizados
- [ ] `README.md` com instruções de execução

## Documento: `spec/<feature>/05-ship.md`

```markdown
# Ship: <feature>

## Resumo da entrega
## Checklist
## Critérios de aceite
## Documentação atualizada
## KBs atualizadas
## Lições aprendidas
## Pendências e dívidas técnicas
## Próximos passos
```

## Saída

Informe o resultado do checklist, o que foi atualizado e as pendências.
Se algo obrigatório falhar, a funcionalidade não está pronta para entrega: volte a `/sdd:build`.
