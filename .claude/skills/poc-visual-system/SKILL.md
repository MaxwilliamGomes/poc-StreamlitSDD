---
name: poc-visual-system
description: >
  Regras de composição, storytelling, interação e acessibilidade para páginas de dashboard em
  Streamlit + Plotly, adaptadas do design system PBIR. Use ao desenhar ou revisar uma página:
  arquétipo, hierarquia, títulos, faixa de KPIs, filtros, visões salvas, tooltips e checklist de
  página. Gatilhos: "monta a página", "layout do dashboard", "título do gráfico", "faixa de KPIs",
  "revisa a página".
---

# POC Visual System

Adaptada da skill `pbir` e do seu `visual-design-system.md`. O que era JSON PBIR, grid em pixels e
CLI do Power BI ficou de fora; ficaram as regras de composição, que valem em qualquer ferramenta.

Esta skill decide **o que vai na página e como se organiza**. A skill `dataviz` decide **como cada
gráfico é desenhado** (paleta validada, marcas, dois eixos, tooltip). Use as duas.

## 0. Decisões antes de montar

1. **Identidade visual:** existe em `docs/identidade/`? Se sim, os tokens do cliente substituem os
   de `app/theme.py`, e as cores de dados passam pelo validador da `dataviz` antes de entrar.
   Se não, use o tema atual e diga isso na entrega.
2. **Tema:** escuro ou claro. Cada modo tem seus passos validados contra a própria superfície.
3. **Chassi:** várias páginas percorridas o tempo todo → navegação no topo (`st.navigation`,
   `position="top"`). Página única → cabeçalho simples. Um chassi para o app inteiro.

## 1. Arquétipo por página

Cada página responde uma pergunta central para um público:

| Arquétipo | Pergunta | Composição |
|---|---|---|
| Executivo | "Está no trilho?" em até 10 s | 3 a 6 KPIs com variação + 1 gráfico principal + insights |
| Operacional | "Algo quebrou?" | Última atualização visível, limiares, lista de exceções |
| Analítico | "Por que aconteceu?" | Filtros, ranking, matriz, clique que filtra |
| Narrativo | "O que aconteceu?" | Tese no título, 1 gráfico âncora, anotações, sem filtros |
| Comparativo | "Em relação a quê?" | Escalas comuns, variação absoluta e %, barras divergentes |

Sinal ambíguo → Analítico. Duas páginas do mesmo arquétipo não repetem a mesma composição.

## 2. Estrutura da página

```text
Cabeçalho: título-insight + subtítulo com período e escopo
Faixa de filtros (uma linha, acima dos gráficos)
Faixa de KPIs: stat_tile com valor, variação e sparkline
Gráfico principal (largura maior)  |  Gráfico de apoio
Detalhe: tabela condicional ou ranking
Rodapé: fonte e regras ("Faturamento exclui cancelados")
```

- **Larguras:** `st.columns` com proporções, não pixels. Principal + apoio em `[2, 1]` ou
  `[7, 5]`; pares em `[1, 1]`. Um gráfico sozinho na linha ocupa a largura toda.
- **Espaçamento:** três níveis (relacionados, grupos, seções), tirados dos tokens de `theme.py`.
- **Até 6 gráficos por página.** Mais que isso é outra página.
- **Posição = importância:** o KPI principal fica no canto superior esquerdo.
- **Hero composto:** um número sozinho nunca é a maior região. KPI principal vem com variação,
  tendência e um gráfico que explica o número.
- **Todo KPI tem contexto:** período anterior, meta ou limiar. Número sem contexto é decoração.

## 3. Storytelling

- **Título-insight**, não rótulo: "SP lidera com 26% do faturamento", não "Faturamento por
  estado". Com dado dinâmico, gere a frase a partir dos dados (`src/insights.py`) e use o rótulo
  como alternativa quando a frase não se sustenta.
- **Subtítulo** só com informação: período, filtro, unidade ou base de comparação.
- **O quê → E daí → E agora:** KPIs mostram o número, gráficos dão o contexto, título ou insight
  indica a ação.
- **Cinza primeiro, uma cor de destaque:** referência e período anterior em neutro; cor forte só no
  que conta a história.
- **Um atributo pré-atentivo por gráfico:** cor, tamanho, posição ou orientação.
- **Rótulos de dados ou eixo de valores, nunca os dois.** Barras com rótulos escondem o eixo;
  linhas usam eixo e grade sutil.
- **Sem clutter:** sem título de eixo quando o título do gráfico já explica, sem bordas, sombras,
  3D ou gradiente decorativo; marcadores só em séries com menos de 12 pontos.
- **Escolha de forma:** colunas até 6 períodos, linha a partir de 7; barras horizontais para
  ranking e nomes longos; nunca rótulo diagonal; barras começam em zero.
- **Squint test:** apertando os olhos, um elemento salta. Se nada salta, a hierarquia está plana.

## 4. Interação

| Papel | Comportamento |
|---|---|
| KPIs | Refletem todos os filtros |
| Referência (meta, período anterior, média) | Não muda com a seleção |
| Gráficos analíticos | Clique filtra o painel (`on_select`), com indicação visível do filtro ativo |
| Tabela de detalhe | Segue os filtros |

- **Filtros** numa linha acima dos gráficos, iguais em todas as páginas e guardados em
  `st.session_state` para seguir o usuário na navegação.
- **Visões salvas** (equivalente aos bookmarks): no máximo 8, sempre com uma opção que restaura o
  padrão, e nomes que dizem o estado ("Último trimestre", "Black Friday").
- **Tooltips:** `hovertemplate` com valor formatado em pt-BR. Nenhum dado crítico só no hover.
- **Orçamento de cliques:** página executiva responde sem clique; analítica em até dois.
- **Zoom por roda desligado** (`scrollZoom: False`), para o gráfico não prender a rolagem.
- **Técnicas prontas** (troca de métrica e grão, TopN + Outros, linhas de meta, último ponto,
  drill para calendário, quadrantes, small multiples, tour guiado): Bloco E do catálogo da skill
  `poc-mockup`, com o equivalente no Power BI e o que o Streamlit não faz.

## 5. Acessibilidade

- Contraste 4,5:1 para texto normal e 3:1 para texto grande e marcas, no fundo real do cartão e da
  página.
- Cor nunca é o único canal: status com ícone, sinal (+/−) ou rótulo.
- Todo gráfico tem versão em tabela (aba Tabela do `components/ui.chart`).
- Texto mínimo de 12 px na tela; alvos de clique de pelo menos 24 × 24 px.
- Ordem de leitura do HTML segue a ordem visual; navegação por teclado alcança filtros e abas.
- Teste com a janela estreita: as colunas do Streamlit empilham abaixo de ~640 px.

## 6. Checklist de página

1. Arquétipo e pergunta central definidos.
2. Título-insight e subtítulo com período e escopo.
3. Filtros numa linha, com estado preservado entre páginas.
4. Faixa de KPIs com contexto em todos.
5. Gráfico principal com mais destaque que os de apoio.
6. Cada gráfico passa pela skill `dataviz` (paleta validada, sem dois eixos, tooltip).
7. Rótulos ou eixo, nunca ambos; cinza para contexto.
8. Interações anotadas: o que filtra o quê.
9. Estados de carregamento, vazio e erro.
10. Rodapé com fonte e regras.
11. Acessibilidade da seção 5.
12. Ver no navegador: sobreposição, texto cortado, rolagem dentro de cartões e janela estreita.

## Limites do Streamlit

Sem equivalente direto: cross-highlight entre gráficos (o clique filtra, não destaca), tooltip com
outro gráfico dentro, posicionamento livre em pixels e drill-through com botão voltar nativo.
Registre a alternativa adotada em vez de prometer o comportamento do Power BI.
