---
name: poc-documentation
description: >
  Gera a documentação formal (.docx) de um dashboard Streamlit para entregar ao cliente: visão
  geral, arquitetura, tabelas e colunas do banco, relacionamentos, catálogo de KPIs e queries,
  regras de negócio, fontes de dados e páginas. Gatilhos: "documenta o dashboard", "gera a
  documentação", "dicionário de dados", "documento .docx do projeto".
---

# POC Documentation

Adaptada de `bi-documentation` (Power BI). Usa uma cópia ajustada do gerador, em
`scripts/gerar-docx.js`, cujos textos de capa e títulos de seção são configuráveis; a versão
original fala em "Modelo Semântico Power BI" e PBIR/TMDL.

## Regras fixas

1. **O entregável é `.docx`.** O README e os documentos de `spec/` continuam como documentação
   versionada; o `.docx` é o documento formal do cliente.
2. **Marca:** sem configuração, sai com o roxo padrão e sem logo. Para usar a marca do cliente,
   preencha o bloco `marca` com o que estiver em `docs/identidade/` ou o que o usuário informou.
   Nunca invente cores ou logo do cliente.
3. **Nada inventado:** seção sem dados é omitida e a numeração se ajusta. Sem descrição de coluna
   no banco nem no código, informe a lacuna em vez de preencher com suposição.
4. **Sem segredos:** nunca inclua senha, token, host interno ou string de conexão. Use os nomes
   das variáveis de ambiente.

## Fluxo

1. Leia `references/dados-schema.md`: o contrato do JSON e de onde vem cada dado neste projeto.
2. **Colete** do banco (só leitura) e do código. Consultas úteis no Postgres:

   ```sql
   SELECT table_name, column_name, data_type, col_description(
            (quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass, ordinal_position)
     FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name NOT LIKE 'raw\_%'
    ORDER BY table_name, ordinal_position;

   SELECT tc.table_name, kcu.column_name, ccu.table_name AS ref_table, ccu.column_name AS ref_column
     FROM information_schema.table_constraints tc
     JOIN information_schema.key_column_usage kcu USING (constraint_name, table_schema)
     JOIN information_schema.constraint_column_usage ccu USING (constraint_name, table_schema)
    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public';
   ```

   Para API, use a documentação e as amostras de `docs/amostras/`.
3. **Monte o JSON** no scratchpad da sessão, não no repositório.
4. **Gere:**

   ```bash
   cd <scratchpad>
   npm install docx jszip    # o docx 9.x não instala o jszip junto
   node <raiz-do-repo>/.claude/skills/poc-documentation/scripts/gerar-docx.js dados.json "Documentacao_<Projeto>.docx"
   ```

   O script imprime `OK: <arquivo> (<KB>) — <marca aplicada>`.
5. **Valide** e mova o `.docx` para `docs/documentacao/`, informando o caminho.

## Validação

1. Tamanho não trivial (normalmente acima de 20 KB).
2. Número de títulos de nível 1 igual ao esperado (Sumário + uma por bloco + uma por tabela + uma
   por seção extra):

   ```bash
   node -e "require('jszip').loadAsync(require('fs').readFileSync('<arquivo>')).then(z=>z.file('word/document.xml').async('string')).then(x=>console.log((x.match(/w:val=\"Heading1\"/g)||[]).length))"
   ```

3. Nenhuma ocorrência de "Power BI", "DAX", "PBIR" ou "TMDL", salvo se o projeto usar:

   ```bash
   node -e "require('jszip').loadAsync(require('fs').readFileSync('<arquivo>')).then(z=>z.file('word/document.xml').async('string')).then(x=>console.log(/Power BI|DAX|PBIR|TMDL/.test(x)))"
   ```

4. Ao abrir no Word: sumário preenchido, títulos na cor primária (azul indica erro de estilo) e
   cada seção numerada em página nova.

## Saída

`docs/documentacao/Documentacao_<Projeto>.docx`, em pt-BR. Em repositório público, confirme com o
usuário antes de versionar o documento.
