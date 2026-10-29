# Dashboard no Redash

**Título:** Equipe 10 - Distribuição geográfica dos fornecedores

**Descrição visível:** Participação no cadastro de fornecedores. Universo TPC-H SF=0,01 gerado por DuckDB e migrado de MySQL para MongoDB. Fotografia do cadastro, sem período de vendas. Contagem não representa gasto, capacidade ou risco financeiro.

## Fonte

MongoDB, banco `n2_equipe10`, coleção `fato_fornecedores`. As coleções `dim_regiao` e `dim_pais` são necessárias para que o pipeline preserve categorias sem fornecedores.

No ambiente nativo usado neste projeto, o MongoDB está em `127.0.0.1:27017`, acessível localmente. Um Redash em contêiner não alcança um MongoDB vinculado exclusivamente ao loopback do Windows via `host.docker.internal`. Para usar Docker, importe as três coleções para o MongoDB do mesmo Compose com `importar_mongo_redash.py`; a URI do Redash será `mongodb://mongodb:27017/n2_equipe10`. Esse script lê as coleções locais, preserva IDs e grava somente no banco dedicado de destino.

## Consultas e visuais

| Consulta | Visual | Campos e unidade |
|---|---|---|
| 01_participacao_regiao | Barras | X: `regiao`; Y: `participacao_pct`; eixo Y: Participação no cadastro (%). Rótulo `0.0`, sem multiplicar por 100 outra vez. |
| 02_distribuicao_pais | Barras ou tabela completa | País, região, fornecedores (unidades), participação (%). Manter os 25 países na tabela. |
| 03_resumo | Counter | Valor `totalFornecedores`; título Fornecedores cadastrados. Outros counters: países e regiões com fornecedor. |
| 04_concentracao_regional | Tabela complementar | Maior participação (%), HHI regional e referência uniforme. Sem faixas de risco presumidas. |

O gráfico regional e a visualização por país são o mínimo relacionado ao desafio. O restante complementa a análise.

## Execução

1. Na instância Redash do laboratório, criar fonte MongoDB e testar a conexão.
2. Criar uma query por JSON de `consultas/redash/`. Executar, salvar e conferir a tabela com `evidencias/indicadores.json`. O estágio `$sort` usa a lista de `name/direction` do conector legado, conforme L03, passo 8. Os arquivos de `consultas/mongodb/` usam a sintaxe nativa.
3. Adicionar as visualizações da tabela acima ao dashboard. Exibir o escopo na descrição e a data de atualização na legenda.
4. Validar `100` fornecedores, `25` países e `5` regiões no recorte fornecido. Barras regionais: 27, 21, 20, 20 e 12%. Se a origem for outra, refazer a validação e atualizar o relatório.
5. Capturar o dashboard e anexar em `evidencias/redash/`. Só registrar como concluída a Etapa 6 depois de executar os gráficos no Redash.

## Situação verificada

Consultas nativas MongoDB executadas e comparadas com MySQL. Gráficos estáticos no relatório e na apresentação usam os resultados reais dessas consultas. **Eles não são capturas do Redash.** A instância Redash não pôde ser iniciada nesta máquina porque o Docker Desktop falha na inicialização. A pasta inclui a infraestrutura do laboratório e instruções; não há comprovação de um dashboard Redash executado.
