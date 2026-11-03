---
name: build
description: |
  Fase 4 do SDD: implementa o manifesto do design por dependências, testa, abre o dashboard para
  validar e registra o resultado em spec/<feature>/04-build.md.
---

# Build

Fase 4 de 5: brainstorm → define → design → **build** → ship.

## Uso

```bash
/sdd:build <feature>
```

## Regras gerais

- Exige `spec/<feature>/03-design.md`.
- Siga o manifesto. Se algo precisar mudar, registre o desvio e o motivo.
- Pare e consulte o usuário antes de mudanças destrutivas, como migrar ou recriar tabelas.
- Não faça commit sem pedido do usuário.
- Se um critério de aceite falhar, informe. Não altere o critério para fazê-lo passar.

## Passos

1. Leia o design e confirme que Postgres, `.env` e dependências estão disponíveis.
2. Ordene o manifesto por dependências: dados, queries, formatação, gráficos e páginas.
3. Implemente cada arquivo com o agente indicado, ou diretamente quando for mais simples.
   Use as KBs como referência e confirme na prática o que elas marcam como não verificado.
4. Depois de cada etapa, rode:

   ```bash
   python -m pytest -q
   ```

5. Confira os KPIs contra uma consulta SQL independente.
6. Suba o app a partir da raiz e valide no navegador:

   ```bash
   python -m streamlit run app/Home.py
   ```

   Percorra todas as páginas, aplique filtros, teste um filtro sem resultados e verifique o
   console e os logs.
7. Rode o agente `code-reviewer` nas mudanças e trate o que for relevante.
8. Escreva o relatório.

## Documento: `spec/<feature>/04-build.md`

```markdown
# Build: <feature>

## Resumo
## Manifesto
| Arquivo | Status | Observações |
## Desvios do design
## Verificação
| Comando ou ação | Resultado |
## Critérios de aceite
| ID | Status | Evidência |
## Problemas encontrados
## Como executar
## Próximo passo
```

Use apenas `aprovado`, `falhou` ou `não verificado` em cada critério.

## Saída

Informe o que foi implementado, os resultados reais dos testes e o que falhou ou não foi verificado.
Próximos passos, somente se todos os critérios obrigatórios passarem: skill `poc-qa`, que grava
`spec/<feature>/qa.md`, e depois `/sdd:ship <feature>`.
