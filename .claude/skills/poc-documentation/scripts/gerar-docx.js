#!/usr/bin/env node
/**
 * Gerador do .docx de documentação de um dashboard (adaptado da skill bi-documentation).
 * Textos de capa, cabeçalho e títulos das seções fixas vêm do bloco `documento` e do campo
 * `titulo` de cada seção, com padrões neutros.
 *
 * Implementa a spec de `references/template-spec.md` (capa, sumário, headers,
 * footer, tabelas, larguras de coluna e estrutura de seções).
 *
 * Uso:
 *   npm install docx jszip      # na pasta de trabalho (scratchpad)
 *   node gerar-docx.js dados.json [saida.docx]
 *
 * O contrato do JSON de entrada está em `references/dados-schema.md`
 * e um exemplo completo em `references/dados-exemplo.json`.
 *
 * Identidade visual: roxo padrão, sem logo; personalizável pelo bloco opcional `marca` do JSON (empresa, cores, fontes, logo).
 * A estrutura do documento nunca muda com a marca.
 */

const fs = require("fs");
const path = require("path");

/**
 * Resolve um pacote a partir do script ou da pasta de trabalho. O segundo caminho
 * importa: o script mora na skill e o `npm install docx` roda no scratchpad — e o
 * npm pode hoistar a instalação para um diretório acima, então a busca precisa
 * subir a árvore (é o que `require.resolve` com `paths` faz).
 */
function carregar(pacote) {
  try {
    return require(pacote);
  } catch {
    try {
      return require(require.resolve(pacote, { paths: [process.cwd()] }));
    } catch {
      console.error(`Pacote \`${pacote}\` não encontrado. Rode \`npm install docx jszip\` na pasta de trabalho antes de gerar.`);
      process.exit(1);
    }
  }
}

const carregarDocx = () => carregar("docx");

const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  TableOfContents, Header, Footer, PageNumber, AlignmentType, BorderStyle,
  WidthType, ShadingType, HeadingLevel, HorizontalPositionAlign,
  HorizontalPositionRelativeFrom, VerticalPositionRelativeFrom, TextWrappingType,
} = carregarDocx();

// ---------------------------------------------------------------------------
// Identidade visual — padrão do curso, sobrescrita pelo bloco `marca` do JSON
// ---------------------------------------------------------------------------

const COR = {
  primaria: "4A148C",     // H1, fundo do cabeçalho das tabelas, borda do header, título da capa
  secundaria: "7B1FA2",   // H2, subtítulo da capa
  destaque: "FFF3E0",     // preenchimento das linhas alternadas
  textoEscuro: "212121",  // texto corrido e células de dados (fixo)
  textoCinza: "616161",   // metadados da capa, notas, header e footer (fixo)
  branco: "FFFFFF",       // texto do cabeçalho das tabelas (fixo)
  cinzaClaro: "CCCCCC",   // bordas das células e borda superior do footer (fixo)
  ardosia: "37474F",      // caminho de arquivo (monoespaçado) (fixo)
};

const FONTE = {
  corpo: "Aptos",           // corpo, títulos e tabelas
  titulo: "Aptos Display",  // apenas o título da capa
  headerFooter: "Arial",    // header e footer
  mono: "Consolas",         // caminhos de arquivo (fixo)
};

const LOGO_PADRAO = null; // sem logo padrão: use marca.logoPath

/** Textos fixos do documento, sobrescritos pelo bloco `documento` do JSON. */
const TEXTO = {
  tituloCapa: "DOCUMENTAÇÃO COMPLETA",
  subtituloCapa: "Dashboard Analítico",
  rodapeCapa: "Gerado a partir do código e do banco do projeto",
  cabecalho: "Documentação do Dashboard",
};

function aplicarDocumento(doc) {
  if (!doc || typeof doc !== "object") return;
  for (const chave of Object.keys(TEXTO)) {
    if (typeof doc[chave] === "string" && doc[chave].trim()) TEXTO[chave] = doc[chave].trim();
  }
}
let LOGO_TIPO = "png"; // "png" ou "jpg", conforme a extensão do arquivo usado

/** Estado da marca aplicada (preenchido por aplicarMarca). */
const MARCA = { empresa: null, resumo: "identidade padrão" };

function corValida(valor) {
  return typeof valor === "string" && /^#?[0-9a-fA-F]{6}$/.test(valor.trim());
}

/**
 * Aplica o bloco `marca` do JSON sobre as constantes de cor e fonte.
 * Todo campo é opcional; campo ausente ou inválido mantém o padrão (com aviso).
 */
function aplicarMarca(marca) {
  if (!marca || typeof marca !== "object") return;
  const cores = { corPrimaria: "primaria", corSecundaria: "secundaria", corDestaque: "destaque" };
  const fontes = { fonteCorpo: "corpo", fonteTitulo: "titulo", fonteRodape: "headerFooter" };
  const aplicadas = [];

  for (const [campo, chave] of Object.entries(cores)) {
    if (marca[campo] === undefined) continue;
    if (corValida(marca[campo])) {
      COR[chave] = marca[campo].trim().replace(/^#/, "").toUpperCase();
      aplicadas.push(`${campo}=#${COR[chave]}`);
    } else {
      console.warn(`Aviso: marca.${campo} inválida (${JSON.stringify(marca[campo])}); mantido o padrão #${COR[chave]}.`);
    }
  }
  for (const [campo, chave] of Object.entries(fontes)) {
    if (typeof marca[campo] === "string" && marca[campo].trim()) {
      FONTE[chave] = marca[campo].trim();
      aplicadas.push(`${campo}=${FONTE[chave]}`);
    }
  }
  if (typeof marca.empresa === "string" && marca.empresa.trim()) MARCA.empresa = marca.empresa.trim();

  MARCA.resumo = aplicadas.length
    ? `marca${MARCA.empresa ? ` "${MARCA.empresa}"` : ""} (${aplicadas.join(", ")})`
    : `identidade padrão${MARCA.empresa ? ` para "${MARCA.empresa}"` : ""}`;
}

const SZ = { capaTitulo: 56, capaSubtitulo: 30, capaModelo: 26, h1: 28, h2: 24, corpo: 20, tabela: 18, pequeno: 16 };

const PAGINA = {
  size: { width: 12240, height: 15840 },
  margin: { top: 1100, right: 1200, bottom: 1100, left: 1200, header: 708, footer: 708, gutter: 0 },
};

const LARGURA_CONTEUDO = 9840;
const EMU_POR_PX = 9525;

/** Larguras de coluna padrão por seção (somam sempre 9840 DXA). */
const LARGURAS = {
  propriedades: [4000, 5840],
  arquitetura: [2200, 1600, 6040],
  colunas: [2400, 1200, 1100, 5140],
  relacionamentos: [3000, 3000, 2000, 1840],
  medidas: [1828, 4444, 1085, 2483],
  padroesDax: [2400, 3200, 4240],
  nomenclatura: [2200, 3800, 3840],
  fontesDados: [1800, 3000, 2200, 2840],
  paginas: [1400, 2400, 1200, 4840],
  visuaisCustomizados: [5000, 4840],
};

/** Distribui 9840 DXA entre N colunas quando não há largura padrão. */
function largurasGenericas(n) {
  const base = Math.floor(LARGURA_CONTEUDO / n);
  const larguras = new Array(n).fill(base);
  larguras[n - 1] = LARGURA_CONTEUDO - base * (n - 1);
  return larguras;
}

function resolveLarguras(chave, nColunas, override) {
  if (Array.isArray(override) && override.length === nColunas) return override;
  const padrao = LARGURAS[chave];
  if (padrao && padrao.length === nColunas) return padrao;
  return largurasGenericas(nColunas);
}

// ---------------------------------------------------------------------------
// Blocos de conteúdo
// ---------------------------------------------------------------------------

const BORDA_CELULA = {
  top: { style: BorderStyle.SINGLE, size: 1, color: COR.cinzaClaro },
  bottom: { style: BorderStyle.SINGLE, size: 1, color: COR.cinzaClaro },
  left: { style: BorderStyle.SINGLE, size: 1, color: COR.cinzaClaro },
  right: { style: BorderStyle.SINGLE, size: 1, color: COR.cinzaClaro },
};

const MARGEM_CELULA = { top: 60, bottom: 60, left: 100, right: 100 };

/**
 * Espaçador vertical. A altura de um parágrafo vazio vem da **marca de
 * parágrafo** (`run`), não de um TextRun vazio — um TextRun de texto "" não
 * altera a altura da linha e a capa sai comprimida. É assim que a referência
 * distribui os blocos da capa.
 */
function paragrafoVazio({ spacing, alignment, size = SZ.corpo } = {}) {
  return new Paragraph({ spacing, alignment, run: { size, font: FONTE.corpo } });
}

function paragrafoCorpo(texto) {
  return new Paragraph({
    spacing: { after: 100 },
    children: [new TextRun({ text: texto, color: COR.textoEscuro, size: SZ.corpo, font: FONTE.corpo })],
  });
}

function paragrafoNota(texto) {
  return new Paragraph({
    spacing: { after: 100 },
    children: [new TextRun({ text: texto, italics: true, color: COR.textoCinza, size: SZ.tabela, font: FONTE.corpo })],
  });
}

function paragrafoCaminho(texto) {
  return new Paragraph({
    spacing: { after: 60 },
    indent: { left: 300 },
    children: [new TextRun({ text: texto, color: COR.ardosia, size: SZ.pequeno, font: FONTE.mono })],
  });
}

/** H1. Toda seção numerada começa em página nova, como no template. */
function titulo1(texto, { quebraPagina = true } = {}) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    pageBreakBefore: quebraPagina,
    children: [new TextRun({ text: texto, font: FONTE.corpo })],
  });
}

function titulo2(texto) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: texto, font: FONTE.corpo })] });
}

function celula(texto, largura, { cabecalho = false, alternada = false } = {}) {
  return new TableCell({
    width: { size: largura, type: WidthType.DXA },
    borders: BORDA_CELULA,
    margins: MARGEM_CELULA,
    shading: cabecalho
      ? { fill: COR.primaria, type: ShadingType.CLEAR, color: "auto" }
      : alternada
        ? { fill: COR.destaque, type: ShadingType.CLEAR, color: "auto" }
        : undefined,
    children: [new Paragraph({
      children: [new TextRun({
        text: String(texto ?? ""),
        bold: cabecalho,
        color: cabecalho ? COR.branco : COR.textoEscuro,
        size: SZ.tabela,
        font: FONTE.corpo,
      })],
    })],
  });
}

/**
 * Monta uma tabela no padrão do template: cabeçalho roxo, linhas de dados
 * alternando branco / pêssego (a 2ª, 4ª, 6ª… linha de dados é pêssego).
 */
function tabela({ cabecalhos, linhas, chaveLargura, larguras }) {
  const nColunas = cabecalhos.length;
  const w = resolveLarguras(chaveLargura, nColunas, larguras);

  const rows = [
    new TableRow({
      tableHeader: true,
      children: cabecalhos.map((h, i) => celula(h, w[i], { cabecalho: true })),
    }),
    ...linhas.map((linha, idx) =>
      new TableRow({
        children: w.map((largura, i) => celula(linha[i], largura, { alternada: idx % 2 === 1 })),
      })
    ),
  ];

  return new Table({
    width: { size: LARGURA_CONTEUDO, type: WidthType.DXA },
    columnWidths: w,
    margins: { left: 10, right: 10 },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: "auto" },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: "auto" },
      left: { style: BorderStyle.SINGLE, size: 4, color: "auto" },
      right: { style: BorderStyle.SINGLE, size: 4, color: "auto" },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 4, color: "auto" },
      insideVertical: { style: BorderStyle.SINGLE, size: 4, color: "auto" },
    },
    rows,
  });
}

// ---------------------------------------------------------------------------
// Logo / headers / footer
// ---------------------------------------------------------------------------

function logoFlutuante(logo, { larguraEmu, alturaEmu, alinhamento, offsetVertical }) {
  return new ImageRun({
    type: LOGO_TIPO,
    data: logo,
    transformation: { width: larguraEmu / EMU_POR_PX, height: alturaEmu / EMU_POR_PX },
    floating: {
      horizontalPosition: { relative: HorizontalPositionRelativeFrom.MARGIN, align: alinhamento },
      verticalPosition: { relative: VerticalPositionRelativeFrom.PARAGRAPH, offset: offsetVertical },
      wrap: { type: TextWrappingType.NONE },
      allowOverlap: true,
      behindDocument: false,
      lockAnchor: false,
    },
  });
}

/** Header da capa: logo grande, centralizado, sem texto nem borda. Sem logo, fica vazio. */
function headerCapa(logo) {
  return new Header({
    children: [
      new Paragraph({
        children: logo ? [logoFlutuante(logo, {
          larguraEmu: 787400, alturaEmu: 442592,
          alinhamento: HorizontalPositionAlign.CENTER, offsetVertical: -284480,
        })] : [],
      }),
      new Paragraph({}),
    ],
  });
}

/** Header do miolo: logo pequeno à esquerda (se houver), texto à direita, borda inferior na cor primária. */
function headerConteudo(logo, nomeModelo) {
  return new Header({
    children: [
      new Paragraph({
        alignment: AlignmentType.RIGHT,
        border: { bottom: { style: BorderStyle.SINGLE, size: 6, space: 4, color: COR.primaria } },
        children: [
          ...(logo ? [logoFlutuante(logo, {
            larguraEmu: 474476, alturaEmu: 266700,
            alinhamento: HorizontalPositionAlign.LEFT, offsetVertical: -136102,
          })] : []),
          new TextRun({
            text: `${nomeModelo}  |  ${TEXTO.cabecalho}`,
            italics: true, color: COR.textoCinza, size: SZ.pequeno, font: FONTE.headerFooter,
          }),
        ],
      }),
    ],
  });
}

function footerConteudo() {
  return new Footer({
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        border: { top: { style: BorderStyle.SINGLE, size: 1, space: 4, color: COR.cinzaClaro } },
        children: [
          new TextRun({ text: "Página ", color: COR.textoCinza, size: SZ.pequeno, font: FONTE.headerFooter }),
          new TextRun({ children: [PageNumber.CURRENT], color: COR.textoCinza, size: SZ.pequeno, font: FONTE.headerFooter }),
        ],
      }),
    ],
  });
}

// ---------------------------------------------------------------------------
// Capa
// ---------------------------------------------------------------------------

function repetir(n, fabrica) {
  return Array.from({ length: n }, fabrica);
}

function capa({ nome, versao, data }) {
  // Cada bloco de espaçadores herda o corpo de fonte do texto que vem a seguir —
  // é a altura dessas linhas vazias que posiciona os blocos na página.
  return [
    ...repetir(6, () => paragrafoVazio({ spacing: { after: 60 } })),
    ...repetir(3, () => paragrafoVazio({ spacing: { after: 200 }, alignment: AlignmentType.CENTER, size: 44 })),
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 200 },
      children: [new TextRun({ text: TEXTO.tituloCapa, bold: true, color: COR.primaria, size: SZ.capaTitulo, font: FONTE.titulo })],
    }),
    ...repetir(2, () => paragrafoVazio({ spacing: { after: 100 }, alignment: AlignmentType.CENTER, size: SZ.capaSubtitulo })),
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 100 },
      children: [new TextRun({ text: TEXTO.subtituloCapa, bold: true, color: COR.secundaria, size: SZ.capaSubtitulo, font: FONTE.corpo })],
    }),
    ...repetir(3, () => paragrafoVazio({ spacing: { after: 400 }, alignment: AlignmentType.CENTER, size: SZ.capaModelo })),
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 400 },
      children: [new TextRun({ text: nome, italics: true, color: COR.textoCinza, size: SZ.capaModelo, font: FONTE.corpo })],
    }),
    ...repetir(2, () => paragrafoVazio({ spacing: { after: 60 } })),
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 60 },
      children: [new TextRun({ text: `Versão ${versao}  |  ${data}`, color: COR.textoCinza, font: FONTE.corpo })],
    }),
    ...repetir(9, () => paragrafoVazio({ alignment: AlignmentType.CENTER, size: SZ.tabela })),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({
        text: TEXTO.rodapeCapa,
        italics: true, color: COR.textoCinza, size: SZ.tabela, font: FONTE.corpo,
      })],
    }),
  ];
}

// ---------------------------------------------------------------------------
// Miolo
// ---------------------------------------------------------------------------

function miolo(dados) {
  const filhos = [
    titulo1("Sumário", { quebraPagina: false }),
    new TableOfContents("Sumário", { hyperlink: true, headingStyleRange: "1-2" }),
  ];
  let n = 0;
  const proximo = () => ++n;

  // 1. Visão Geral do Modelo
  if (dados.visaoGeral) {
    const s = proximo();
    filhos.push(titulo1(`${s}. ${dados.visaoGeral.titulo || "Visão Geral do Modelo"}`));
    if (dados.visaoGeral.intro) filhos.push(paragrafoCorpo(dados.visaoGeral.intro));
    filhos.push(tabela({
      cabecalhos: dados.visaoGeral.cabecalhos || ["Propriedade", "Valor"],
      linhas: dados.visaoGeral.linhas,
      chaveLargura: "propriedades",
      larguras: dados.visaoGeral.larguras,
    }));
  }

  // 2. Arquitetura do Modelo (Star Schema)
  if (dados.arquitetura) {
    const s = proximo();
    filhos.push(titulo1(`${s}. ${dados.arquitetura.titulo || "Arquitetura do Modelo (Star Schema)"}`));
    if (dados.arquitetura.intro) filhos.push(paragrafoCorpo(dados.arquitetura.intro));
    filhos.push(tabela({
      cabecalhos: dados.arquitetura.cabecalhos || ["Tabela", "Tipo", "Descrição"],
      linhas: dados.arquitetura.linhas,
      chaveLargura: "arquitetura",
      larguras: dados.arquitetura.larguras,
    }));
  }

  // 3..N. Uma seção por tabela do modelo
  for (const t of dados.tabelas || []) {
    const s = proximo();
    filhos.push(titulo1(`${s}. Tabela ${t.nome} (${t.tipo})`));
    if (t.descricao) filhos.push(paragrafoCorpo(t.descricao));

    let sub = 0;
    if (t.colunas) {
      filhos.push(titulo2(`${s}.${++sub} Colunas`));
      filhos.push(tabela({
        cabecalhos: t.colunas.cabecalhos || ["Coluna", "Tipo", "Sumarizar", "Descrição"],
        linhas: t.colunas.linhas,
        chaveLargura: "colunas",
        larguras: t.colunas.larguras,
      }));
    }
    if (t.fonteDados) {
      filhos.push(titulo2(`${s}.${++sub} ${t.fonteDados.titulo || "Fonte de Dados"}`));
      if (t.fonteDados.texto) filhos.push(paragrafoCorpo(t.fonteDados.texto));
    }
  }

  // Relacionamentos
  if (dados.relacionamentos) {
    const s = proximo();
    filhos.push(titulo1(`${s}. ${dados.relacionamentos.titulo || "Relacionamentos"}`));
    if (dados.relacionamentos.intro) filhos.push(paragrafoCorpo(dados.relacionamentos.intro));
    filhos.push(tabela({
      cabecalhos: dados.relacionamentos.cabecalhos || ["Origem (N)", "Destino (1)", "Tipo", "Filtragem"],
      linhas: dados.relacionamentos.linhas,
      chaveLargura: "relacionamentos",
      larguras: dados.relacionamentos.larguras,
    }));
    if (dados.relacionamentos.observacoes) {
      filhos.push(titulo2(`${s}.1 Observações`));
      for (const obs of [].concat(dados.relacionamentos.observacoes)) filhos.push(paragrafoCorpo(obs));
    }
  }

  // Catálogo de Medidas DAX
  if (dados.medidas) {
    const s = proximo();
    filhos.push(titulo1(`${s}. ${dados.medidas.titulo || "Catálogo de Medidas DAX"}`));
    if (dados.medidas.intro) filhos.push(paragrafoCorpo(dados.medidas.intro));
    filhos.push(tabela({
      cabecalhos: dados.medidas.cabecalhos || ["Medida", "Expressão DAX", "Formato", "Descrição"],
      linhas: dados.medidas.linhas,
      chaveLargura: "medidas",
      larguras: dados.medidas.larguras,
    }));
  }

  // Padrões DAX Utilizados
  if (dados.padroesDax) {
    const s = proximo();
    filhos.push(titulo1(`${s}. ${dados.padroesDax.titulo || "Padrões DAX Utilizados"}`));
    if (dados.padroesDax.intro) filhos.push(paragrafoCorpo(dados.padroesDax.intro));
    filhos.push(tabela({
      cabecalhos: dados.padroesDax.cabecalhos || ["Padrão", "Medidas que Utilizam", "Descrição"],
      linhas: dados.padroesDax.linhas,
      chaveLargura: "padroesDax",
      larguras: dados.padroesDax.larguras,
    }));
  }

  // Convenções de Nomenclatura
  if (dados.nomenclatura) {
    const s = proximo();
    filhos.push(titulo1(`${s}. ${dados.nomenclatura.titulo || "Convenções de Nomenclatura"}`));
    if (dados.nomenclatura.intro) filhos.push(paragrafoCorpo(dados.nomenclatura.intro));
    filhos.push(tabela({
      cabecalhos: dados.nomenclatura.cabecalhos || ["Elemento", "Convenção", "Exemplos"],
      linhas: dados.nomenclatura.linhas,
      chaveLargura: "nomenclatura",
      larguras: dados.nomenclatura.larguras,
    }));
  }

  // Fontes de Dados
  if (dados.fontesDados) {
    const s = proximo();
    filhos.push(titulo1(`${s}. ${dados.fontesDados.titulo || "Fontes de Dados"}`));
    if (dados.fontesDados.intro) filhos.push(paragrafoCorpo(dados.fontesDados.intro));
    filhos.push(tabela({
      cabecalhos: dados.fontesDados.cabecalhos || ["Tabela", "Fonte", "Sheet/Tabela", "Observações"],
      linhas: dados.fontesDados.linhas,
      chaveLargura: "fontesDados",
      larguras: dados.fontesDados.larguras,
    }));
    if (dados.fontesDados.caminho) {
      filhos.push(titulo2(`${s}.1 Caminho do Arquivo`));
      for (const linha of [].concat(dados.fontesDados.caminho)) filhos.push(paragrafoCaminho(linha));
      if (dados.fontesDados.nota) filhos.push(paragrafoNota(dados.fontesDados.nota));
    }
  }

  // Páginas do Relatório
  if (dados.paginas) {
    const s = proximo();
    filhos.push(titulo1(`${s}. ${dados.paginas.titulo || "Páginas do Relatório"}`));
    if (dados.paginas.intro) filhos.push(paragrafoCorpo(dados.paginas.intro));
    filhos.push(tabela({
      cabecalhos: dados.paginas.cabecalhos || ["Página", "Nome", "Visuais", "Descrição"],
      linhas: dados.paginas.linhas,
      chaveLargura: "paginas",
      larguras: dados.paginas.larguras,
    }));
    let sub = 0;
    if (dados.paginas.visuaisCustomizados) {
      filhos.push(titulo2(`${s}.${++sub} Visuais Customizados`));
      filhos.push(tabela({
        cabecalhos: dados.paginas.visuaisCustomizados.cabecalhos || ["Visual", "Tipo"],
        linhas: dados.paginas.visuaisCustomizados.linhas,
        chaveLargura: "visuaisCustomizados",
        larguras: dados.paginas.visuaisCustomizados.larguras,
      }));
    }
    if (dados.paginas.bookmarks) {
      filhos.push(titulo2(`${s}.${++sub} Bookmarks`));
      filhos.push(paragrafoCorpo(dados.paginas.bookmarks));
    }
  }

  // Seções extras opcionais, na mesma formatação
  for (const extra of dados.secoesExtras || []) {
    const s = proximo();
    filhos.push(titulo1(`${s}. ${extra.titulo}`));
    if (extra.intro) filhos.push(paragrafoCorpo(extra.intro));
    if (extra.linhas) {
      filhos.push(tabela({ cabecalhos: extra.cabecalhos, linhas: extra.linhas, larguras: extra.larguras }));
    }
    let sub = 0;
    for (const sec of extra.subsecoes || []) {
      filhos.push(titulo2(`${s}.${++sub} ${sec.titulo}`));
      if (sec.texto) filhos.push(paragrafoCorpo(sec.texto));
      if (sec.linhas) filhos.push(tabela({ cabecalhos: sec.cabecalhos, linhas: sec.linhas, larguras: sec.larguras }));
      if (sec.nota) filhos.push(paragrafoNota(sec.nota));
    }
  }

  return filhos;
}

// ---------------------------------------------------------------------------
// Documento
// ---------------------------------------------------------------------------

function construirDocumento(dados, logo) {
  const modelo = dados.modelo || {};
  const nome = modelo.nome || "Dashboard";

  return new Document({
    creator: modelo.autor || MARCA.empresa || "Documentação do modelo semântico",
    title: `Documentação Completa — ${nome}`,
    description: TEXTO.subtituloCapa,
    features: { updateFields: true }, // faz o Word recalcular o Sumário ao abrir
    styles: {
      // Os títulos precisam ser redefinidos em `default` (e não em paragraphStyles):
      // declarar id "Heading1" ali geraria um styleId duplicado e o Word aplicaria
      // o built-in azul de 16 pt em vez do roxo do template.
      default: {
        document: { run: { font: FONTE.corpo, size: SZ.corpo, color: COR.textoEscuro } },
        heading1: {
          run: { size: SZ.h1, bold: true, color: COR.primaria, font: FONTE.corpo },
          paragraph: { spacing: { before: 300, after: 200 }, outlineLevel: 0 },
        },
        heading2: {
          run: { size: SZ.h2, bold: true, color: COR.secundaria, font: FONTE.corpo },
          paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 1 },
        },
      },
      paragraphStyles: [
        { id: "Normal", name: "Normal", quickFormat: true, run: { font: FONTE.corpo, size: SZ.corpo, color: COR.textoEscuro } },
        { id: "TOC1", name: "toc 1", basedOn: "Normal", next: "Normal", paragraph: { spacing: { after: 100 } } },
        { id: "TOC2", name: "toc 2", basedOn: "Normal", next: "Normal", paragraph: { spacing: { after: 100 }, indent: { left: 200 } } },
      ],
    },
    sections: [
      {
        properties: { page: PAGINA },
        headers: { default: headerCapa(logo) },
        children: capa({ nome, versao: modelo.versao || "1.0", data: modelo.data || "" }),
      },
      {
        properties: { page: PAGINA },
        headers: { default: headerConteudo(logo, nome) },
        footers: { default: footerConteudo() },
        children: miolo(dados),
      },
    ],
  });
}

// ---------------------------------------------------------------------------
// Pós-processamento
// ---------------------------------------------------------------------------

/**
 * Marca o estilo Normal como padrão do documento (`w:default="1"`), como no
 * template de referência. O docx-js não expõe essa flag; sem ela o pacote fica
 * sem estilo de parágrafo padrão — o Word cai no docDefaults, mas validadores
 * e leitores OOXML (python-docx, por exemplo) falham ao resolver o estilo.
 */
async function marcarNormalComoPadrao(buffer) {
  const JSZip = carregar("jszip");
  const zip = await JSZip.loadAsync(buffer);
  const arquivo = zip.file("word/styles.xml");
  if (!arquivo) return buffer;

  const xml = await arquivo.async("string");
  const alvo = '<w:style w:type="paragraph" w:styleId="Normal">';
  if (!xml.includes(alvo)) return buffer;

  zip.file("word/styles.xml", xml.replace(alvo, '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'));
  return zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

async function main() {
  const [entrada, saidaArg] = process.argv.slice(2);
  if (!entrada) {
    console.error("Uso: node gerar-docx.js <dados.json> [saida.docx]");
    process.exit(1);
  }

  const dados = JSON.parse(fs.readFileSync(entrada, "utf8"));
  aplicarMarca(dados.marca);
  aplicarDocumento(dados.documento);

  // Logo: `marca.logoPath` (relativo ao diretório do JSON), `logo` na raiz (formato antigo)
  // ou o padrão da skill. Logo ausente gera aviso e documento sem logo — não interrompe.
  const dirEntrada = path.dirname(path.resolve(entrada));
  const logoInformado = dados.marca?.logoPath || dados.logo;
  const logoPath = logoInformado ? path.resolve(dirEntrada, logoInformado) : LOGO_PADRAO;
  let logo = null;
  if (!logoPath) {
    // sem logo informado: documento sem logo, sem aviso
  } else if (fs.existsSync(logoPath)) {
    logo = fs.readFileSync(logoPath);
    LOGO_TIPO = /\.jpe?g$/i.test(logoPath) ? "jpg" : "png";
  } else {
    console.warn(`Aviso: logo não encontrado em ${logoPath}; o documento será gerado sem logo.`);
  }

  const nomeArquivo = (dados.modelo?.nome || "Modelo").replace(/[^\wÀ-ÿ]+/g, "");
  const saida = saidaArg || `Documentacao_${nomeArquivo}.docx`;

  const buffer = await marcarNormalComoPadrao(await Packer.toBuffer(construirDocumento(dados, logo)));
  fs.writeFileSync(saida, buffer);

  const kb = (fs.statSync(saida).size / 1024).toFixed(1);
  console.log(`OK: ${saida} (${kb} KB) — ${MARCA.resumo}${logo ? "" : ", sem logo"}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
