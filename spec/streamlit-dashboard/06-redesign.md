# Redesign: streamlit-dashboard

Pedido do usuário em 2026-11-02, com 27 referências em `Bi-Referencias/DesigneTelas`.

## O que mudou

| Área | Mudança |
|------|---------|
| Tema | Escuro navy, cards de vidro, navegação no topo; `.streamlit/config.toml` e `app/theme.py` |
| Bookmarks | Visões salvas: Último mês, Último trimestre, Ano completo, Black Friday, Natal, Sudeste, Sul e Nordeste |
| Interação | Clique em uma barra de estado filtra o painel; segundo clique limpa |
| Tooltips | Cards mostram atual e anterior, no hover e no foco do teclado; gráficos usam crosshair e leitura unificada |
| Formatação condicional | Tabelas com data bars, setas, células de calor e chips |
| Narrativa | `src/insights.py` gera frases só a partir dos dados |
| Novos visuais | Sparklines, atual vs. anterior, heatmap dia × hora, barras divergentes, matriz macrocategoria × estado, pirulito com média, barra segmentada, anel da nota e sentimento centrado no neutro |

## Decisões

| Decisão | Motivo |
|---------|--------|
| Abre em "Último trimestre" | Revoga a premissa de abrir no período completo, que mostrava variação "—" em todos os cards. CA-08 e CA-14 valem com a visão "Ano completo" |
| Barra segmentada em vez de rosquinhas | Skill `dataviz`: rosquinha compara mal; o anel fica só na nota, razão contra um limite |
| Barras divergentes em vez de cascata | A cascata esmagava as variações, e truncar o eixo distorceria as barras |
| Uma escala por gráfico | Sem dois eixos |
| Aba Tabela nos gráficos principais | Valores não dependem do hover. Heatmaps, barras por estado e pagamento e sentimento não têm a aba |
| Paleta validada em `#101827` | Modo escuro, `validate_palette.js`: todos os checks passaram |
| SVG como imagem em data URI | `st.html` remove `<svg>` inline |
| Comentários em HTML escapado | Substitui a decisão anterior de usar `st.dataframe`; dados passam por `escape`, com teste |

## Referências não reproduzidas

Fotos de produto, mapas e tile maps exigem ativos ou dados externos. Drill-through por produto ou
macrocategoria exige novos filtros em todas as queries. Temas de cor e bookmarks salvos pelo usuário
também ficaram fora.

## Verificação

| Ação | Resultado |
|------|-----------|
| `python -m pytest -q` | 79 passed |
| Ano completo na tela vs. SQL | R$ 11.856.768,69; 4.485; R$ 2.643,65; 10,3%; 203 avaliações |
| Último trimestre vs. SQL | R$ 2.882.996,19; anterior R$ 2.891.326,72; Moda 15,1% |
| Black Friday vs. SQL | R$ 610.914,88; 242 pedidos |
| Variação por estado vs. SQL | SC +R$ 57 mil; RJ −R$ 100 mil |
| Clique na barra PR | Filtro aplicado a todo o painel |
| Tooltip, troca de página pelo menu, console | Funcionam, sem erros após a carga |

Validado em janela de 2400 px. Telas menores, teclado, leitor de tela e a aba Tabela não foram
testados no navegador. O estado vazio e o erro de banco não foram repetidos depois do redesign.
Um clique em Black Friday se perdeu antes de a sessão estabilizar; não se repetiu em sessão limpa.
