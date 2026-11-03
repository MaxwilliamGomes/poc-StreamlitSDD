---
name: poc-mockup
description: >
  Desenha o mockup de um dashboard Streamlit no Figma (ou em texto, sem Figma) a partir dos KPIs do
  define, para o cliente aprovar antes do build. Monta primeiro o mapa de construção, com cada
  visual ligado a uma query e a uma função de gráfico. Gatilhos: "mockup", "desenha as telas",
  "wireframe do dashboard", "preview antes de construir".
---

# POC Mockup

Adaptada de `figma-mockup` (Power BI). O mockup é um preview fiel do que o Streamlit consegue
construir: mesmos componentes, mesma ordem, mesmas larguras relativas.

## Quando usar

Durante o `/sdd:design`, depois que o `02-define.md` fechou KPIs e critérios, e **antes** do
`/sdd:build`. Construir sem aprovação do cliente costuma gerar retrabalho.

## Princípio: mapa primeiro, desenho depois

O mockup renderiza o mapa; não é criação livre. Monte `spec/<feature>/mockup/mapa-construcao.md`
antes de desenhar qualquer frame.

## Referências obrigatórias

1. Skill `poc-visual-system`: arquétipos, estrutura da página, storytelling, interação.
2. `references/catalogo-visuais.md`: visuais permitidos, pergunta → visual, proibidos, técnicas de
   interação e destaque (Bloco E) e formato do mapa.
3. Skill `dataviz`: forma e cor de cada gráfico.
4. `docs/identidade/` e `docs/referencias-visuais/`, quando existirem.

## Entrada

- KPIs do `02-define.md`, cada um com a query prevista em `src/queries.py` (existente ou planejada).
  KPI sem query prevista fica fora e vira pendência.
- Perguntas de negócio e público de cada página.
- Tokens da identidade do cliente, se houver; senão, os de `app/theme.py`.

## Pré-condição: Figma

Os nomes das ferramentas variam por instalação. Procure a ferramenta `whoami` do servidor Figma
(carregue por ToolSearch se estiver adiada) e chame-a.

- **Autenticado:** siga para o desenho. Carregue antes as skills `figma:figma-use` e
  `figma:figma-generate-design`, que são pré-requisito das ferramentas de escrita.
- **Sem servidor ou sem login:** oriente o usuário (`/mcp` → autenticar) e use o fallback textual,
  `spec/<feature>/mockup/mockup-textual.md`, com uma seção por página e o mesmo checklist.

## Processo

1. Leia as referências e pergunte só o que falta: tema (escuro ou claro) e tokens do cliente.
2. Confira que cada KPI tem query prevista.
3. **Escolha o tom** em uma linha (corporativo sóbrio, operacional denso ou editorial) e mantenha
   em todas as páginas.
4. **Escolha o arquétipo de cada página** (`poc-visual-system`, seção 1). Duas páginas do mesmo
   arquétipo não repetem a composição. Entre 3 e 6 páginas.
5. **Monte o mapa** no formato do catálogo (Bloco D): título-insight, visual por linha, query,
   função de gráfico, largura em colunas, cor e interação.
6. **Desenhe** um frame por página em **1440 px de largura** (desktop), altura livre, com tema e
   tipografia do mapa. Opcional: um frame de 390 px mostrando o empilhamento no celular.
7. Exporte a imagem de cada frame e grave `spec/<feature>/mockup/figma-url.md` e
   `spec/<feature>/mockup/screenshots/p01-<slug>.png`.
8. Registre no `03-design.md` o link do mapa e as decisões que o mockup fixou.

## Checklist de fidelidade

- [ ] Mapa e mockup correspondem 1:1.
- [ ] Toda linha cita uma query existente ou planejada e uma função de gráfico ou componente.
- [ ] Nenhum visual fora do Bloco A nem dentro do Bloco C.
- [ ] Cada página declara arquétipo e justificativa; composições não se repetem.
- [ ] Títulos são frases-insight; tom único.
- [ ] Larguras em proporções de `st.columns` que o Streamlit consegue reproduzir.
- [ ] **Squint test:** na miniatura, um elemento salta.
- [ ] **Sibling test:** as miniaturas lado a lado parecem da mesma família.

## Saída

- `spec/<feature>/mockup/mapa-construcao.md`: contrato do build.
- `spec/<feature>/mockup/figma-url.md`: URL, tema, tom, paleta e tabela
  `Página | Arquétipo | KPIs | Screenshot`.
- `spec/<feature>/mockup/screenshots/*.png`.

## Anti-padrões

- Desenhar antes do mapa.
- Desenhar o que o Streamlit não faz: posição livre em pixels, sobreposição, cross-highlight,
  tooltip com gráfico dentro, animações.
- Visual proibido no Bloco C, como pizza, gauge, 3D ou dois eixos.
- Páginas todas com o mesmo arquétipo.
- Título-rótulo ("Vendas") em vez de frase-insight.
- Paleta diferente dos tokens do cliente, ou cor de dados sem passar pelo validador da `dataviz`.
- Nome de ferramenta do Figma fixo sem conferir o prefixo real.
