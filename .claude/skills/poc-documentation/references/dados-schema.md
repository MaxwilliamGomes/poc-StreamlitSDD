# Contrato do JSON de entrada

Mesmo contrato da skill `bi-documentation`, com duas extensões desta cópia do gerador:

- **Bloco `documento`:** textos fixos da capa e do cabeçalho.
- **Campo `titulo` em cada seção fixa:** troca o título padrão, que fala em DAX e Star Schema.

```text
node scripts/gerar-docx.js dados.json [saida.docx]
```

Regras gerais:

- Toda seção é opcional; a ausente é omitida e a numeração se ajusta.
- Tabelas aceitam `cabecalhos`, `linhas` (array de arrays) e `larguras` (inteiros DXA que somam
  **9840**; sem `larguras`, valem as do template para o número de colunas padrão).
- Texto vai para o documento sem transformação: escreva em pt-BR, já formatado.

## Estrutura

```jsonc
{
  "modelo": { "nome": "ShopAgent Dashboard", "versao": "1.0", "data": "2 de novembro de 2026", "autor": "Equipe de Dados" },

  "documento": {                                    // opcional
    "tituloCapa": "DOCUMENTAÇÃO COMPLETA",
    "subtituloCapa": "Dashboard Analítico em Streamlit",
    "rodapeCapa": "Gerado a partir do código e do banco do projeto",
    "cabecalho": "Documentação do Dashboard"
  },

  "marca": {                                        // opcional; só o que o cliente forneceu
    "empresa": "Cliente", "corPrimaria": "#0B3954", "corSecundaria": "#087E8B", "corDestaque": "#E3F2FD",
    "fonteTitulo": "Segoe UI", "fonteCorpo": "Segoe UI", "fonteRodape": "Segoe UI",
    "logoPath": "logo.png"                          // relativo ao diretório do JSON
  },

  "visaoGeral": {
    "titulo": "Visão Geral",
    "intro": "Objetivo do dashboard e público.",
    "linhas": [["Stack", "Streamlit 1.66, Plotly 7, Postgres 16"], ["Páginas", "5"], ["Período dos dados", "01/11/2025 a 31/10/2026"]]
  },

  "arquitetura": {
    "titulo": "Arquitetura",
    "intro": "Fluxo: fonte → preparação → Postgres → queries → cache → Streamlit.",
    "cabecalhos": ["Tabela", "Tipo", "Descrição"],
    "linhas": [["orders", "Fato", "Um registro por pedido"]]
  },

  "tabelas": [{
    "nome": "orders", "tipo": "Fato", "descricao": "…",
    "colunas": { "cabecalhos": ["Coluna", "Tipo", "Nulo", "Descrição"], "linhas": [["total", "numeric", "não", "qty × price"]] },
    "fonteDados": { "titulo": "Origem", "texto": "raw_orders, preparado por src/prepare_data.py" }
  }],

  "relacionamentos": {
    "cabecalhos": ["Origem (N)", "Destino (1)", "Tipo", "Uso"],
    "linhas": [["orders.customer_id", "customers.customer_id", "Muitos-para-um", "Clientes e estados"]],
    "observacoes": "Avaliações ligadas a pedidos entregues."
  },

  "medidas": {
    "titulo": "Catálogo de KPIs",
    "cabecalhos": ["KPI", "Regra", "Formato", "Query"],
    "linhas": [["Faturamento", "Soma de total, sem cancelados", "R$ 1.234,56", "overview_kpis"]]
  },

  "padroesDax": {
    "titulo": "Regras de Negócio",
    "cabecalhos": ["Regra", "Onde se aplica", "Descrição"],
    "linhas": [["Comparação", "Todos os KPIs", "Período imediatamente anterior, de mesma duração"]]
  },

  "nomenclatura": { "titulo": "Convenções", "linhas": [["Módulos Python", "snake_case", "prepare_data.py"]] },

  "fontesDados": {
    "cabecalhos": ["Tabela", "Fonte", "Origem", "Observações"],
    "linhas": [["orders", "Postgres", "gen/data/raw_dump.sql", "Datas redistribuídas com semente fixa"]],
    "caminho": ["Variáveis: POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB"],
    "nota": "Credenciais ficam no .env, fora do Git."
  },

  "paginas": {
    "titulo": "Páginas do Dashboard",
    "cabecalhos": ["Página", "Nome", "Gráficos", "Pergunta respondida"],
    "linhas": [["1", "Visão geral", "6", "O negócio está no trilho?"]],
    "bookmarks": "Visões salvas: Último trimestre (padrão), Ano completo, Black Friday."
  },

  "secoesExtras": [
    { "titulo": "Queries", "cabecalhos": ["Função", "Parâmetros", "Retorno"], "linhas": [["overview_kpis", "start, end, states", "1 linha"]] },
    { "titulo": "Execução", "intro": "Comandos do README.", "subsecoes": [{ "titulo": "Testes", "texto": "python -m pytest -q" }] }
  ]
}
```

`medidas` e `padroesDax` mantêm os nomes do contrato original, mas aqui carregam KPIs e regras de
negócio; sempre passe `titulo` e `cabecalhos` neles, senão o documento sai com "DAX".

## Onde buscar cada dado neste projeto

| Campo | Origem |
|---|---|
| `modelo`, `visaoGeral` | `README.md`, `requirements.txt`, contagens no banco |
| `arquitetura` | `.claude/CLAUDE.md` (Arquitetura e Modelo de dados) |
| `tabelas` | `information_schema.columns` + `col_description`; `gen/init.sql` |
| `tabelas[].fonteDados` | `src/prepare_data.py`, `gen/data/` |
| `relacionamentos` | chaves estrangeiras em `information_schema` |
| `medidas` (KPIs) | `spec/<feature>/02-define.md` (catálogo de KPIs) e `src/queries.py` |
| `padroesDax` (regras) | Regras de negócio do `.claude/CLAUDE.md` |
| `nomenclatura` | Convenções do `.claude/CLAUDE.md` |
| `fontesDados` | `.env.example` (só nomes de variáveis), `docs/fontes-de-dados.md` |
| `paginas` | `app/pages/` e `spec/<feature>/03-design.md` |
| `marca` | `docs/identidade/` ou o usuário; nunca inferir |
