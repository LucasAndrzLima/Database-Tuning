# Apresentação da Equipe 10 - 17/11/2026, 21h40 a 21h50

Distribuição sugerida para ensaio, ajustável pela equipe. As falas se apoiam nos números executados. O Redash ainda precisa ser executado no ambiente da turma antes da apresentação.

## Bárbara Tebaldi Franco - 0:00 a 2:10

**Slide 1, 0:00 a 0:40:** “Nosso desafio é a distribuição geográfica dos fornecedores. Queremos apoiar o planejamento de suprimentos identificando onde o cadastro oferece mais ou menos alternativas.” Apresentar os integrantes.

**Slide 2, 0:40 a 1:25:** “Definimos participação como a porcentagem de fornecedores cadastrados em cada região. O denominador é o total de fornecedores do mesmo recorte. Esse indicador mede cobertura cadastral, não gasto ou capacidade.”

**Slide 3, 1:25 a 2:10:** “Usamos o processo de geração de TPC-H SF=0,01 ensinado no laboratório L02. Carregamos as três tabelas necessárias no MySQL: 100 fornecedores, 25 países e cinco regiões. Selecionamos todos os fornecedores dessa base reduzida, sem LIMIT.”

## Henrique Dias de Carvalho Junior - 2:10 a 4:10

**Slide 4, 2:10 a 3:10:** “O grão é um fornecedor cadastrado. A medida vale um para cada registro e as dimensões são fornecedor e geografia. Incorporamos esses atributos no documento MongoDB. Países e regiões auxiliares permitem mostrar categorias sem fornecedores. Não juntamos vendas, porque isso repetiria os cadastros.” Mostrar o diagrama e um documento real com `db.fato_fornecedores.findOne()`.

**Slide 5, 3:10 a 4:10:** “A ETL usa um snapshot somente leitura no MySQL, integra as chaves, rejeita geografia inválida e grava primeiro em coleções temporárias. Conferimos o conteúdo antes de publicar. Guardamos a versão anterior em backup.” Explicar que a publicação de três coleções ocorre em janela sem leitores, pois não é uma transação única no standalone.

## Joao Vitor Lima Cecilio - 4:10 a 6:10

**Slide 6, 4:10 a 5:05:** Abrir `evidencias/validacao.json`. “As contagens das duas bases correspondem e todos os campos projetados dos fornecedores foram comparados. Não houve IDs extras ou divergências. As consultas independentes por região e país retornaram os mesmos indicadores.” Mostrar também os testes de região vazia, duplicata, órfão e denominador zero, se houver tempo.

**Slide 7, 5:05 a 6:10:** “A Ásia concentra 27% dos fornecedores, a África 21%, a América e a Europa 20% cada, e o Oriente Médio 12%. Entre os extremos são 15 pontos percentuais. A distribuição indica onde investigar alternativas, sem impor a mesma quantidade para todas as regiões.”

## Lucas Andrzejewski de Lima - 6:10 a 10:00

**Slide 8, 6:10 a 7:15:** “Por país, Estados Unidos tem oito cadastros, seguido de Moçambique e China com sete cada. Os seis países com pelo menos seis fornecedores somam 40% do total. Dentro das regiões, Estados Unidos representa 40% da América e Egito, 50% do Oriente Médio. Essa decomposição evita interpretar apenas a visão regional.”

**Slide 9, 7:15 a 8:15:** “Recomendamos investigar alternativas no Oriente Médio se houver necessidade operacional e revisar a concentração dentro das regiões. Antes de definir compras, precisamos cruzar o cadastro com peças, custos e prazos.”

**Slide 10, 8:15 a 9:20:** Mostrar o dashboard no Redash **após executá-lo e validá-lo no ambiente da turma**. Apresentar as barras regionais e a visualização por país, títulos, unidades e denominador. Se o Redash continuar indisponível, informar essa limitação e mostrar os gráficos estáticos como evidências auxiliares, sem afirmar que substituem a Etapa 6.

**Slide 11, 9:20 a 10:00:** “Os resultados descrevem o cadastro da escala SF=0,01 gerada neste projeto. Não os generalizamos para a base SF=1 nem para uma empresa real. O próximo passo é complementar a cobertura com dados operacionais para fundamentar a seleção de fornecedores.”

## Respostas curtas para perguntas

- **Por que não usar lineitem?** O objeto da demanda é o cadastro de fornecedores por região. Juntar itens repetiria fornecedores e excluiria os que não têm vendas, a menos que a consulta fosse redesenhada.
- **Por que só três tabelas?** O enunciado permite recorte justificado. Supplier, nation e region contêm todas as chaves e atributos necessários à pergunta definida. Migramos integralmente essas três tabelas da escala gerada.
- **Por que embedding?** A geografia é pequena, lida junto ao cadastro e estável no snapshot. A desnormalização simplifica as agregações. Não armazenamos arrays ilimitados.
- **Essa participação mede risco?** Mede distribuição de cadastros. O risco de suprimentos exige contexto como gasto, peças críticas, capacidade e prazo.
- **O índice melhorou?** No filtro regional, a leitura coberta examinou 21 chaves e zero documentos, contra 100 documentos na varredura. Na base pequena, os tempos não comprovaram ganho de latência.
- **Qual rubrica foi seguida?** As sete etapas do enunciado atualizado. O documento também contém uma rubrica anexada divergente; registramos o conflito e incluímos evidências auxiliares de desempenho.
