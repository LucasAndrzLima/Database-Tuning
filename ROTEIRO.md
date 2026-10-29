# Apresentação - Equipe 10

**17/11/2026, 21h40 às 21h50.** Duração total: dez minutos, incluindo o dashboard.

| Tempo | Responsável | Conteúdo |
|---|---|---|
| 0:00 a 2:00 | Bárbara Tebaldi Franco | Problema gerencial, decisão apoiada, indicador e recorte utilizado. |
| 2:00 a 4:00 | Henrique Dias de Carvalho Junior | Modelo estrela, grão, embedding e etapas da ETL. Mostrar um documento no MongoDB. |
| 4:00 a 6:00 | Joao Vitor Lima Cecilio | Validação MySQL × MongoDB: quantidades, indicadores e inconsistências. |
| 6:00 a 10:00 | Lucas Andrzejewski de Lima | Dashboard regional, visualização por país, interpretação e conclusões. |

## Pontos principais

- Pergunta: como os fornecedores cadastrados se distribuem por regiões e países?
- Participação: fornecedores da região / total de fornecedores × 100.
- Grão: um fornecedor cadastrado; medida igual a 1; dimensões fornecedor e geografia.
- Origem: supplier → nation → region, no TPC-H SF=0,01.
- Validação: 100 fornecedores, 25 países e cinco regiões nas duas bases; documentos e indicadores correspondentes.
- Resultados: Ásia 27%, África 21%, América 20%, Europa 20%, Oriente Médio 12%.
- Detalhamento: Estados Unidos representa 40% dos fornecedores da América; Egito, 50% dos do Oriente Médio.
- Decisão: priorizar a investigação de alternativas conforme a necessidade de suprimentos, complementando o cadastro com capacidade, custo e prazos.

Na apresentação, abrir o dashboard Redash e demonstrar o gráfico regional e a tabela por país. As duas consultas já foram executadas e validadas; a captura e os resultados estão em evidencias/redash/.
