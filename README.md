# Avaliação Somativa N2 - Equipe 10

## Distribuição geográfica dos fornecedores

**Demanda:** distribuição geográfica dos fornecedores. **Decisão apoiada:** planejar suprimentos. **Indicador principal:** participação dos fornecedores cadastrados por região.

**Equipe:** Bárbara Tebaldi Franco; Henrique Dias de Carvalho Junior; Joao Vitor Lima Cecilio; Lucas Andrzejewski de Lima.

**Apresentação:** 17/11/2026, terça-feira, das **21h40 às 21h50**, conforme a versão atualizada da avaliação fornecida em 28/10/2026. Duração total de dez minutos.

Esta pasta substitui o projeto provisório anterior de receita/clientes. O tema agora corresponde ao Desafio 10 confirmado pelo catálogo da avaliação.

## Resultado executado

Foi gerado o TPC-H **SF=0,01** com a extensão `tpch` do DuckDB, seguindo o processo do laboratório L02, passo 9. As tabelas completas `region` (5), `nation` (25) e `supplier` (100) dessa escala foram carregadas em uma instância **MySQL 8.0.46 real e isolada**, e transformadas em documentos no **MongoDB 9.0.4 real**. A versão exata do Mongo está em `evidencias/versoes.json`.

Não se trata da imagem SF=1/PT-BR da turma nem de dados de uma empresa real. As outras cinco tabelas do TPC-H foram geradas em memória pelo dbgen e não foram carregadas no MySQL: o recorte temático usa apenas as três tabelas que respondem à demanda. Não há amostragem dos primeiros N fornecedores nem filtro por data de venda.

| Região (nomes do benchmark) | Fornecedores | Participação no cadastro |
|---|---:|---:|
| ASIA | 27 | 27% |
| AFRICA | 21 | 21% |
| AMERICA | 20 | 20% |
| EUROPE | 20 | 20% |
| MIDDLE EAST | 12 | 12% |
| Total | 100 | 100% |

Validação SQL/MongoDB aprovada: **zero divergências** nos documentos dos fornecedores, sem IDs extras, indicadores por região e país equivalentes e dimensões com contagens correspondentes. Os testes adicionais com banco temporário real também passaram (região vazia, chave duplicada, órfão e denominador zero). Resultados e hashes estão em `evidencias/`.

## Arquivos da entrega

| Arquivo/pasta | Conteúdo |
|---|---|
| `output/relatorio_equipe10.pdf` | Problema, modelo, ETL, validação, gráficos, análise e limites |
| `modelo_estrela.mmd` | Modelo estrela editável em Mermaid |
| `apresentacao_10_minutos.md` | Falas e divisão de tempo para os integrantes |
| `sql/` | Extração, indicadores independentes e verificações de integridade |
| `projeto.py` | ETL, validação de todos os fornecedores e medição auxiliar |
| `consultas/mongodb/` | Pipelines nativos executados |
| `consultas/redash/` | Versões JSON para o conector do laboratório |
| `dashboard/` | Configuração, visuais e infraestrutura para Redash |
| `dados/` | CSVs das três tabelas de origem e manifesto com hashes |
| `evidencias/` | Carga, validação comparativa, indicadores, testes e planos reais |
| `docs/fontes.json` | Inventário de todos os PDFs da pasta cont e subpastas, com hashes e aplicação |

**Pendência material:** o Redash não pôde ser executado nesta máquina porque o Docker Desktop falha ao iniciar. Os gráficos do relatório e dos slides usam indicadores reais do MongoDB, mas **não são capturas do Redash**. Para concluir a Etapa 6 do enunciado, executar as consultas e criar as visualizações na instância Redash da turma, seguindo `dashboard/LEIA-ME.md`. Não há repositório GitLab publicado; os arquivos estão organizados para envio. Não se inventou histórico de commits.

## Reproduzir em uma base TPC-H já existente

No PowerShell, dentro desta pasta:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# Editar .env com as conexões reais. O destino Mongo deve ser dedicado, n2_...
.\.venv\Scripts\python.exe gerar_consultas.py
.\.venv\Scripts\python.exe projeto.py executar
.\.venv\Scripts\python.exe testar_integridade.py
.\.venv\Scripts\python.exe gerar_relatorio.py
```

`executar` extrai, carrega, valida e registra um experimento de desempenho. `validar`, `exportar` e `desempenho` permitem executar essas fases separadamente. MySQL recebe somente leitura na ETL. MongoDB recebe escrita apenas no banco dedicado configurado. A carga preserva os dados anteriores em coleções de backup. A publicação de três coleções é sequencial: executar sem leitores ou cargas concorrentes, pois o MongoDB standalone não oferece uma transação que englobe esses renames. A conexão `.env` usada localmente contém senha aleatória e não faz parte do pacote de entrega.

Para repetir a geração SF=0,01, configure um **schema novo** começando por `n2_` e execute `preparar_base.py` antes da ETL. O gerador interrompe se o schema existir. Requer permissão de criação nesse schema. Para reutilizar a base da turma, não execute o gerador: use diretamente a ETL. Se mudar a origem, refaça os gráficos, a apresentação e as conclusões, pois os números atuais não se aplicam automaticamente à nova escala.

## Modelo e regras

Grão: um fornecedor cadastrado na fotografia atual. A chave do documento é `s_suppkey`. A medida `quantidadeFornecedores` vale 1 por fornecedor. Dimensões conceituais: fornecedor (ID/nome) e geografia (país/região). No MongoDB esses atributos são incorporados no fato. As coleções `dim_pais` e `dim_regiao` permitem representar categorias sem fornecedor; elas não mudam o grão do fato.

Participação = quantidade da região / total de fornecedores do mesmo snapshot × 100. Todos os fornecedores são considerados, independentemente de possuírem vendas ou peças fornecidas. A região é a do fornecedor. Não há JOIN com customer, orders ou lineitem, o que evitaria confusão com geografia dos clientes e multiplicação de cadastros. Não há histórico de alterações: a data da carga é técnica, não uma data de ocorrência comercial. Se forem mantidos múltiplos snapshots, a contagem só é aditiva dentro de um mesmo snapshot.

HHI regional complementar = soma dos quadrados das participações expressas em pontos percentuais. Resultado: 2114. A referência matemática uniforme para cinco regiões é 2000; não foi definida uma meta comercial nem adotada faixa de risco concorrencial. A diferença entre a maior e menor participação é 15 pontos percentuais.

## Desempenho e rubricas

A seção 6 da avaliação atribui 3/4/3 pontos a ETL, dashboard e insights. A rubrica anexada nas páginas 7 e 8 descreve 5/3/2 pontos, migração, desempenho e GitLab, contrariando a orientação de que não se exige comparação de desempenho. O projeto segue as sete etapas da descrição atual e registra esse conflito. Inclui, de forma auxiliar, SQL equivalente, EXPLAIN estimado e executado, índice, execução MongoDB com caminho natural e com índice forçados e sete medições por consulta.

O índice foi útil para reduzir documentos examinados no filtro regional, mas **não houve melhoria comprovada de latência neste recorte pequeno**. Não há alegação de que MongoDB seja superior a MySQL. Hints forçam estratégias, tempos incluem driver/transmissão e não equivalem a benchmark controlado. Detalhes completos em `evidencias/desempenho.json`.

## Referências

Todos os conteúdos locais de `cont` e suas subpastas foram inventariados e usados conforme o propósito: diagnóstico SQL (Atividade, Aulas 01/02b e L01), fundamentos documentais (Aula 03), modelagem dimensional e embedding (Aula 04 e L02), geração SF=0,01 (L02/9), fluxo ETL-validação-dashboard (L03), chaves (Diagrama TPCH), instalação/CRUD (guia MongoDB/GitLab). A avaliação atualizada, fora de `cont`, determina o tema e o cronograma. O inventário `docs/fontes.json` preserva os caminhos completos e hashes dos PDFs consultados.

Fontes técnicas primárias consultadas: [DuckDB TPC-H](https://duckdb.org/docs/current/core_extensions/tpch), [MongoDB $unionWith](https://www.mongodb.com/docs/manual/reference/operator/aggregation/unionWith/), [Redash MongoDB](https://redash.io/help/data-sources/querying/mongodb/), [Redash API](https://redash.io/help/user-guide/integrations-and-api/api/). A infraestrutura em `dashboard/compose.yaml` adapta as portas do repositório didático do professor, cujo URL está no arquivo `dashboard/REFERENCIA.md`.
