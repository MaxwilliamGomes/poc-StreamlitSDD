---
name: poc-qa
description: >
  Valida um dashboard Streamlit antes do /sdd:ship ou de entregar ao cliente: rastreabilidade
  de dor a critério de aceite, testes, arquitetura, KPIs contra SQL independente, páginas no
  navegador, acessibilidade e segurança. Grava spec/<feature>/qa.md. Gatilhos: "valida o
  dashboard", "QA final", "checklist antes de entregar", "confere se está tudo consistente".
---

# POC QA

Adaptada de `qa-validation` (Power BI). Objetivo: provar com comandos, não com impressão, que
requisitos, queries, gráficos, páginas e documentação contam a mesma história.

Valide agora; não reaproveite resultados de rodadas anteriores.

## Rastreabilidade

Cada linha da matriz (`docs/levantamento-requisitos/matriz-rastreabilidade.md`, ou os critérios do
`02-define.md` quando não houver matriz) precisa fechar a cadeia:

```text
Dor → Pergunta → KPI → Query (src/queries.py) → Loader (app/data.py) → Gráfico → Página → Critério de aceite
```

Elo vazio é pendência. Confira por busca no código, não pela memória:

```bash
grep -n "def <query>" src/queries.py
grep -n "<query>" app/data.py
grep -rn "<loader>" app/pages/
```

## Validação mecânica

Rode da raiz, nesta ordem. Falha aqui interrompe o QA.

1. **Ambiente:** a fonte responde; `.env` existe e não está no Git
   (`git check-ignore .env .streamlit/secrets.toml`).
2. **Testes:** `python -m pytest -q`. Testes pulados contam como não verificados; com o banco
   desligado os testes de integração são pulados.
3. **Arquitetura:** `tests/test_architecture.py` passa (sem SQL nas páginas, `src/` sem
   Streamlit, só `app/data.py` chama queries).
4. **KPIs:** cada KPI principal conferido contra uma consulta SQL escrita à parte, sem usar
   `src/queries.py`, com o mesmo filtro. Registre os dois valores.
5. **App sobe:** `python -m streamlit run app/Home.py --server.headless true` e
   `curl -s http://localhost:8501/_stcore/health` responde `ok`.
6. **Páginas:** abra cada página no navegador e verifique o console. Aplique filtros, uma visão
   salva, um clique que filtra e um filtro sem resultado (estado vazio).
7. **Erro:** com a fonte desligada, o app mostra mensagem clara, sem traceback.
8. **Paleta:** cores de dados passam pelo `validate_palette.js` da skill `dataviz`, nos dois
   modos que o app oferece.
9. **Visual:** sobreposição, texto cortado, rolagem dentro de cartões, janela estreita (~640 px).
10. **Desempenho:** tempo de cada página com cache frio e quente, comparado à meta do define.

## Checklist de requisitos

- Todas as dores prioritárias foram tratadas?
- Todos os KPIs aprovados foram implementados?
- Há requisito sem dono ou pendência do cliente aberta?

## Checklist de dados e queries

- Queries parametrizadas; nenhum valor de filtro interpolado no SQL.
- Regras de negócio aplicadas como no define (cancelados, fuso, período de comparação).
- Cache com TTL explícito, coerente com a frequência de atualização da fonte.
- Joins sem duplicar linhas; contagens conferidas.
- API: paginação completa, limite de requisições respeitado, erro tratado.

## Checklist de interface

- Título-insight e subtítulo com período em todas as páginas.
- Valores em pt-BR (R$, datas e separadores).
- Rótulos ou eixo, nunca ambos; sem dois eixos; cinza para contexto.
- Visões salvas aplicam o que prometem; existe a opção de restaurar o padrão.
- Todo gráfico tem versão em tabela.
- Estados de carregamento, vazio e erro.

## Checklist de acessibilidade

- Contraste 4,5:1 em texto e 3:1 em marcas, no fundo real.
- Nenhum status só por cor.
- Teclado alcança filtros, abas e navegação.
- Nenhum dado crítico só no tooltip.

## Checklist de entrega

- Nenhuma credencial no código; `.env.example` atualizado.
- `requirements.txt` atualizado.
- `README.md` com instruções de execução.
- Material confidencial do cliente fora do Git em repositório público.
- Documentação final criada (skill `poc-documentation`), se fizer parte da entrega.

## Saída obrigatória

Grave `spec/<feature>/qa.md`. O `/sdd:ship` usa este arquivo como evidência.

```markdown
# QA: <feature>

## Resultado geral
Aprovado / Aprovado com ressalvas / Reprovado

## Validação mecânica
| Passo | Comando ou ação | Resultado |

## Rastreabilidade
| Pergunta | KPI | Query | Gráfico | Página | Critério | Status |

## KPIs conferidos
| KPI | Filtro | App | SQL independente | Confere |

## Itens críticos
## Itens importantes
## Melhorias futuras
## Pendências
| ID | Descrição | Origem | Responsável | Prazo |
```

Item crítico aberto = **Reprovado**. Só itens importantes abertos = **Aprovado com ressalvas**.
Passo não executado é "não verificado", nunca "aprovado".
