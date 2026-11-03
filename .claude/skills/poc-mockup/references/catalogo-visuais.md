# Catálogo de visuais para Streamlit + Plotly

Referência da skill `poc-mockup`. Composição e storytelling estão em `poc-visual-system`; forma,
cor e marcas de cada gráfico, na skill `dataviz`.

## Bloco A: visuais permitidos

Só o que o projeto consegue construir. A coluna "No código" aponta para o que já existe neste repo;
um visual novo entra no mapa com a função planejada.

| Visual | Quando usar | No código |
|---|---|---|
| Faixa de KPIs | Valor com contexto (variação e tendência) | `html.stat_tile` + `html.sparkline` |
| Insights | Frases geradas dos dados | `html.insights` + `src/insights.py` |
| Linha | Tendência com 7 pontos ou mais | `charts.revenue_trend` |
| Atual vs. anterior | Comparar o período com o anterior | `charts.revenue_comparison` |
| Colunas | Até 6 períodos ou categorias | `charts.frequency_columns`, `charts.rating_columns` |
| Barras horizontais | Ranking, nomes longos | `charts.state_bars`, `charts.segment_bars` |
| Barras clicáveis | Ranking que filtra o painel | `ui.clickable_state_chart` |
| Barras divergentes | Desvio em relação a zero, meta ou período | `charts.revenue_change`, `charts.sentiment_diverging` |
| Lollipop | Ranking com muitos itens e pouca tinta | `charts.category_lollipop` |
| Barra segmentada | Parte do todo com até 5 partes | `html.segmented_bar`, `charts.payment_mix` |
| Mapa de calor | Duas dimensões discretas (dia × hora, categoria × estado) | `charts.orders_heatmap`, `charts.category_matrix` |
| Tabela condicional | Detalhe com barras de dados, tendência e cor por limiar | `html.conditional_table` |
| Anel | Nota única em escala fechada | `html.rating_ring` |
| Cartão de comentário | Texto livre do cliente | `html.comment_card` |
| Filtros | Período, dimensões e visões salvas | `components/filters.py` |
| Abas Gráfico/Tabela | Versão acessível de todo gráfico | `ui.chart` |
| Linha com meta e faixa | Real contra meta, com a área entre as duas | nova: duas séries + `fill="tonexty"`; exige meta na fonte |
| Calendário do mês | Valor diário com intensidade e variação contra o dia anterior | nova: grade em `components/html.py` + query diária |
| Dispersão em quadrantes | Duas métricas com referências e cor por quadrante | nova: `scatter` + `add_hline`/`add_vline` |
| Small multiples | Mesma métrica quebrada por categoria | nova: `make_subplots` ou `facet_col`, eixo Y comum por padrão |
| Barra com restante | Parte de um total, com o restante em cinza atrás | nova: duas barras sobrepostas (`barmode="overlay"`) |

## Bloco B: pergunta → visual

| Pergunta | Visual | Regra |
|---|---|---|
| Qual o valor de X? | KPI | Sempre com variação ou meta |
| Quem são os maiores ou menores? | Barras horizontais ou lollipop | Ordenado por valor, nunca alfabético |
| Qual a tendência? | Linha | 7 pontos ou mais; menos que isso, colunas |
| Como se compara com o período anterior? | Atual vs. anterior ou barras divergentes | Mesma escala; anterior em neutro |
| Qual a composição? | Barra segmentada | Até 5 partes, com % rotulado |
| Como se distribui? | Colunas por faixa | Faixas definidas na query |
| Onde se concentra? | Mapa de calor | Escala sequencial de um matiz |
| Há relação entre X e Y? | Dispersão | Nunca dois eixos |
| Quais os detalhes? | Tabela condicional | Com versão para download se o cliente pedir |
| Geografia como ranking? | Barras por estado | Mapa só quando a pergunta é "onde" |
| Está acima da meta? | Linha com meta e faixa | Meta em neutro tracejado; status com sinal, não só cor |
| Como foi cada dia do mês? | Calendário do mês | Aberto pelo clique no mês da linha mensal |
| Quem está em cada combinação de X e Y? | Dispersão em quadrantes | Referências na média, na meta ou escolhidas pelo usuário |
| A mesma tendência vale para cada grupo? | Small multiples | Até 9 painéis; escala comum, salvo escolha explícita |

## Bloco C: proibidos

| Visual | Motivo e substituto |
|---|---|
| Pizza e rosca para parte do todo | Ângulo é a pior codificação; barra segmentada |
| Gauge | Pouca informação por área; KPI com variação |
| Dois eixos Y | Engana a comparação; dois gráficos ou índice comum |
| Radar | Leitura difícil; barras |
| 3D, gradiente ou sombra decorativa | Ruído |
| Arco-íris como escala | Sequencial de um matiz ou divergente com centro neutro |
| Rótulo de eixo na diagonal | Barras horizontais ou abreviação |

Pedido de visual proibido: registre como nota no mapa, proponha o equivalente do Bloco B e decida
com o cliente na apresentação do mockup.

## Bloco E: técnicas de interação e destaque

Levantadas dos desafios "Data visualization // workout" (Gustaw Dudek, Power BI) e de capturas de
referência. A coluna "Power BI" ajuda a reconhecer o pedido quando o cliente usa esses termos.

| Técnica | Power BI | No Streamlit + Plotly | Status |
|---|---|---|---|
| Trocar a métrica do gráfico | Parâmetro de campo | `st.segmented_control` no cartão; título, eixo e formato seguem a escolha | nova |
| Trocar o grão de tempo | Parâmetro de campo de data | Seletor dia/semana/mês; o grão automático vira o padrão | parcial: `filters.comparison_grain` |
| Título e subtítulo dinâmicos | Medida de texto | Frase gerada dos dados; subtítulo com unidade, período e grão | parcial: `src/insights.py` |
| Linha de média, mediana ou meta | Linha constante | `add_hline` com rótulo à direita, em neutro | nova |
| Destaque do último ponto, mín. e máx. | Marcador por medida | Marcador e anotação só nesses pontos; cor do rótulo pelo status | nova |
| Folga no topo do eixo | Máximo do eixo × 1,1 | `range=[0, max * 1.1]` para os rótulos não cortarem | nova |
| Rótulos liga/desliga | Bookmark | `st.toggle` que muda `textposition` | nova |
| Alternar visões (linha, dispersão, tabela) | Navegador de bookmarks | `st.segmented_control` ou `st.tabs` | parcial: abas Gráfico/Tabela |
| Mostrar e esconder painel de filtros | Bookmark | `st.expander` ou `st.popover` "Filtros" | nova |
| Visões salvas | Bookmark de estado | Botões que aplicam período e filtros | existe: `filters.BOOKMARKS` |
| TopN escolhido pelo usuário | Parâmetro numérico | `st.slider` passado à query como parâmetro | nova |
| TopN + "Outros", incluir ou excluir | Tabela auxiliar + medida | Agrupamento no SQL, com opção de esconder "Outros" | nova |
| Ranking por métrica escolhida | Medida de ranking | `RANK()` no SQL sobre a métrica selecionada | nova |
| Cor condicional por limiar ou grupo | Formatação condicional (fx) | Lista de cores por ponto, sempre com sinal ou rótulo | existe: `html.conditional_table`, `charts.revenue_change` |
| Data bars na tabela, cor igual à do gráfico | Data bars | Barra em HTML com o token da métrica | existe: `html.data_bar` |
| Estrelas como rótulo | Ícone ou unichar | Rótulos "★★★★☆" no eixo | nova |
| Eixo Y comum ou independente | Escala compartilhada | `matches="y"` ligado ou desligado, com aviso quando independente | nova |
| Drill de mês para dias | Drill-through ou tooltip page | Clique no mês (`on_select`) abre o calendário em `st.dialog` | nova |
| Destacar um quadrante | Formatação + interação | Clique ou seletor; os demais pontos em neutro | nova |
| Ícone "i" com explicação | Tooltip page | `st.popover` ou `help=` no título | nova |
| Tooltip com tabela ou gráfico | Tooltip page | Não existe; use texto no `hovertemplate` ou detalhe abaixo do gráfico | limite |
| Destaque cruzado entre gráficos | Interação de destaque | Não existe; o clique filtra o painel | limite |

### Elementos de página

| Elemento | No Streamlit | Status |
|---|---|---|
| "Atualizado em" visível | Data da última carga no cabeçalho | nova |
| Alerta com ação ("Assinantes em risco" → ver lista) | Cartão com botão `st.page_link` para a página certa | nova |
| Página futura marcada com cadeado | Item de navegação desabilitado com rótulo | nova |
| Tour guiado em passos | `st.dialog` com passos, guardando em `session_state` que já foi visto | nova |
| Assistente com perguntas sugeridas e fonte citada | Painel de chat ligado às mesmas queries de `src/` | futuro: depende do agente |
| Banner com foto e saudação | `st.image` com imagem própria ou licenciada | opcional |

Regras para usar o Bloco E:

1. Cada troca de métrica ou visão mantém título, subtítulo, eixo, formato e tabela coerentes com a
   escolha. Gráfico que muda e título que não muda é erro.
2. Técnica "nova" entra no mapa marcada como nova, com a função planejada.
3. Técnica "limite" não entra no mockup como se existisse; registre a alternativa.
4. Destaques (último ponto, quadrante, meta) usam um único atributo pré-atentivo por gráfico.

## Bloco D: formato do `mapa-construcao.md`

```markdown
# Mapa de construção: <projeto>

> Tema: escuro. Tom: corporativo sóbrio. Largura de referência: 1440 px.

## Página 1: "Visão geral" · Faturamento estável, com queda em 3 estados
- **Arquétipo:** Executivo. Justificativa: diretoria, revisão semanal.
- **Filtros:** visões salvas + período + estados (iguais em todas as páginas).

| # | Visual | Pergunta | Query | Função | Colunas | Cor | Interação | Nota |
|---|---|---|---|---|---|---|---|---|
| 1 | Faixa de 4 KPIs | Qual o valor? | `overview_kpis`, `kpi_series` | `html.stat_tile` | 4 × 1/4 | semântica na variação | Segue filtros | Hero: faturamento |
| 2 | Atual vs. anterior | Está acima do anterior? | `revenue_over_time` | `charts.revenue_comparison` | 2/3 | atual em destaque, anterior neutro | — | Gráfico principal |
| 3 | Barras por estado | Onde vende mais? | `revenue_by_state` | `ui.clickable_state_chart` | 1/3 | mesma cor do faturamento | Clique filtra o painel | Top 10 |
```

Regras:

1. Toda linha cita query e função, existentes ou planejadas (marque "nova").
2. Colunas em frações de `st.columns`; a soma da linha é 1.
3. Mapa e mockup correspondem 1:1.
4. **Cor:** `mesma-medida` (a mesma medida tem a mesma cor em todo o app), `sequencial` (valor
   contínuo) ou `semântica` (bom ou ruim, sempre com sinal ou ícone).
5. **Interação:** o que filtra o quê. Interação não anotada não existe.
