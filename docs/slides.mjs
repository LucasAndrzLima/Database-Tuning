// Fonte da apresentação editável. Executada pelo Artifact Session do Codex.
export async function criarSlidesN2(artifactSession) {
  return artifactSession.run(async ({presentation}) => {
    const ink='#183547',teal='#176B73',muted='#506575';
    function txt(s,text,x,y,w,h,size=30,bold=false,color=ink){
      const sh=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
      sh.text=text;sh.text.style={fontFamily:'Arial',fontSize:size,bold,color};return sh;
    }
    function slide(title,notes){const s=presentation.slides.add();s.background.fill='#F7F8FA';txt(s,title,64,55,1152,100,43,true);s.speakerNotes.text=notes;return s;}
    if(presentation.slides.items.length!==1)throw new Error('Esta fonte pressupõe apenas a capa inicial.');
    const cover=presentation.slides.items[0];
    txt(cover,'Equipe 10 · Data Analytics e BI',70,322,1100,55,32,false,teal);
    txt(cover,'Bárbara Tebaldi Franco\nHenrique Dias de Carvalho Junior\nJoao Vitor Lima Cecilio\nLucas Andrzejewski de Lima',70,410,1100,155,23,false,muted);
    txt(cover,'17 de novembro de 2026 · 21h40 a 21h50',70,620,1100,40,24,false,muted);

    let s=slide('Planejamento de suprimentos','0:40 a 1:25. Pergunta: como os fornecedores cadastrados se distribuem entre regiões e países? Indicador: participação por contagem, sobre todos os fornecedores da mesma fotografia. A contagem não mede gasto ou capacidade. Fonte: Avaliação N2 atualizada, páginas 2, 4 a 6.');
    txt(s,'A distribuição do cadastro revela onde a empresa dispõe de mais alternativas de fornecedores.',70,180,1120,140,36);
    txt(s,'Participação regional = fornecedores da região ÷ fornecedores totais × 100',70,365,1120,100,33,true,teal);
    txt(s,'Decisão apoiada: priorização da investigação e da qualificação de alternativas de suprimento.',70,520,1120,110,30,false,muted);

    s=slide('Origem e escopo dos dados','1:25 a 2:10. Geração TPC-H SF=0,01 conforme L02, passo 9, com DuckDB. Todas as linhas de supplier, nation e region foram carregadas no MySQL isolado. Não é a imagem SF=1/PT-BR da turma. Sem LIMIT e sem filtro de vendas. Fontes: cont/DB L02 Modelagem e criação de bancos NoSQL/9.pdf; dados/origem.json.');
    txt(s,'TPC-H SF=0,01 gerado com DuckDB\nTabelas supplier, nation e region carregadas no MySQL',70,178,1120,130,34);
    for(const [x,num,label]of [[70,'100','fornecedores'],[465,'25','países'],[860,'5','regiões']]){txt(s,num,x,370,300,100,76,true,teal);txt(s,label,x,480,300,50,29);}
    txt(s,'Censo do recorte gerado. Resultados restritos a essa base de benchmark.',70,610,1120,45,25,false,muted);

    s=slide('Modelo dimensional e MongoDB','2:10 a 3:10. Grão: fornecedor no snapshot atual, medida quantidadeFornecedores=1. Dimensões Fornecedor e Geografia. A data da carga é técnica. Embedding incorpora atributos pequenos e lidos juntos. Dimensões geográficas auxiliares preservam categorias com zero fornecedores. Não se juntam vendas para evitar repetição. Fontes: Aula 04; L02 passos 2 a 8; Diagrama TPCH; modelo_estrela.mmd.');
    txt(s,'Grão: um fornecedor no cadastro atual',70,178,1120,65,38,true,teal);
    txt(s,'Fato: quantidadeFornecedores = 1\nDimensão Fornecedor: ID e nome\nDimensão Geografia: país e região',70,290,1120,190,34);
    txt(s,'MongoDB: atributos incorporados no documento do fornecedor.\nDimensões auxiliares preservam países e regiões sem cadastros.',70,540,1120,100,28,false,muted);

    s=slide('ETL reproduzível','3:10 a 4:10. MySQL em snapshot consistente e somente leitura. LEFT JOIN revela órfãos. A transformação rejeita nomes vazios e geografia inválida. IDs únicos e conteúdo conferido em staging. Coleções anteriores ficam em backup. A publicação sequencial de três coleções exige janela sem leitores, sem transação entre renames no standalone. Fontes: projeto.py; L03 passos 4 a 6; L02 passos 4 e 6.');
    txt(s,'1  Extração do MySQL pelas chaves do TPC-H\n2  Tratamento de campos e verificação da geografia\n3  Gravação em coleções temporárias no MongoDB\n4  Conferência dos registros e dos indicadores\n5  Publicação do snapshot e preservação de backup',70,185,1120,370,31);
    txt(s,'Chave do documento = s_suppkey. Cada fornecedor aparece uma vez.',70,600,1120,50,25,false,teal);

    s=slide('Validação aprovada em bancos reais','4:10 a 5:05. Mostrar evidencias/validacao.json. Todos os campos projetados dos fornecedores e IDs extras/ausentes foram comparados. Consultas SQL independentes por região e país equivalentes aos pipelines. Testes em banco temporário real: categoria vazia, duplicação, órfão e denominador zero. Fontes: evidencias/validacao.json e testes_integridade.json.');
    txt(s,'MySQL',70,180,500,50,30,true,muted);
    txt(s,'MongoDB',700,180,500,50,30,true,muted);
    txt(s,'100 fornecedores\n25 países\n5 regiões',70,265,500,190,34);
    txt(s,'100 fornecedores\n25 países\n5 regiões',700,265,500,190,34);
    txt(s,'0 divergências por fornecedor\nIndicadores por região e país equivalentes\nParticipações regionais somam 100%',70,490,1120,155,30,true,teal);

    s=slide('Ásia reúne 27% dos fornecedores','5:05 a 6:10. Ásia 27%, África 21%, América 20%, Europa 20%, Oriente Médio 12%. Amplitude: 15 pontos percentuais. HHI=2114, referência uniforme=2000 para cinco regiões. A uniformidade é referência matemática, sem meta comercial. Fonte: evidencias/indicadores.json, consulta 01. Gráfico dos resultados reais, não captura de Redash.');
    s.charts.add('bar',{position:{left:65,top:180,width:835,height:445},categories:['ASIA','AFRICA','AMERICA','EUROPE','MIDDLE EAST'],series:[{name:'Participação no cadastro',values:[.27,.21,.20,.20,.12],fill:teal}],hasLegend:false,barOptions:{direction:'bar',grouping:'clustered'},xAxis:{numberFormatCode:'0%',textStyle:{fontSize:20}},yAxis:{min:0,max:.35,majorUnit:.1,numberFormatCode:'0%',textStyle:{fontSize:20}},dataLabels:{showValue:true,numberFormatCode:'0%',position:'outEnd',textStyle:{fontSize:21}}});
    txt(s,'15 p.p.',940,250,280,100,58,true,teal);txt(s,'entre a maior\ne a menor\nparticipação',940,365,275,160,29);
    txt(s,'Fornecedores cadastrados por região (%) · TPC-H SF=0,01 · n = 100',70,655,1130,35,22,false,muted);

    s=slide('A distribuição por país muda a leitura','6:10 a 7:15. Todos os seis países com pelo menos seis fornecedores somam 40% do total. EUA tem 8 dos 20 fornecedores da América (40% da região). Egito tem 6 dos 12 do Oriente Médio (50%). A tabela completa dos 25 países está no relatório. Fonte: evidencias/indicadores.json, consulta 02. Gráfico dos resultados reais, não captura de Redash.');
    s.charts.add('bar',{position:{left:65,top:170,width:830,height:460},categories:['UNITED STATES','MOZAMBIQUE','CHINA','EGYPT','KENYA','VIETNAM'],series:[{name:'Fornecedores',values:[8,7,7,6,6,6],fill:teal}],hasLegend:false,barOptions:{direction:'bar',grouping:'clustered'},xAxis:{numberFormatCode:'0',textStyle:{fontSize:20}},yAxis:{textStyle:{fontSize:20}},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:21}}});
    txt(s,'40%',950,235,250,90,58,true,teal);txt(s,'do total nos\nseis países\nmostrados',950,340,250,155,29);
    txt(s,'Países com pelo menos 6 fornecedores · Contagem de cadastros · n = 100',70,655,1130,35,22,false,muted);

    s=slide('Decisões apoiadas pelos resultados','7:15 a 8:15. Investigar alternativas no Oriente Médio se houver demanda e viabilidade operacional, sem quotas uniformes presumidas. Detalhar a concentração interna nos EUA e Egito. A decisão de compra precisa de peças, custos e prazos. Fonte: cálculos sobre consulta 02, resultados reais.');
    txt(s,'12% no Oriente Médio\nInvestigar alternativas diante da demanda de suprimentos.',70,180,1120,130,32);
    txt(s,'40% da América nos EUA e 50% do Oriente Médio no Egito\nDetalhar a cobertura dentro de cada região.',70,350,1120,130,32);
    txt(s,'Custos, peças e prazos completam a decisão de compra.\nO cadastro indica onde aprofundar a investigação.',70,530,1120,105,30,true,teal);

    s=slide('Dashboard no Redash','8:15 a 9:20. O enunciado exige Redash. Queries nativas executadas; Redash pendente por erro de inicialização do Docker Desktop. Os gráficos anteriores usam dados reais, mas não são capturas do Redash. Seguir dashboard/LEIA-ME.md para configurar a fonte, importar o snapshot no Mongo do Compose, executar queries e conferir visuais. Não declarar concluída a Etapa 6 sem demonstração real.');
    txt(s,'Gráfico principal\nParticipação de fornecedores por região (%)',70,180,1120,120,34);
    txt(s,'Visualização complementar\nFornecedores por país, com região e participação (%)',70,350,1120,120,34);
    txt(s,'Consultas e configuração prontas.\nExecução do Redash pendente nesta máquina.',70,540,1120,100,29,true,teal);

    s=slide('Alcance da análise e próximos passos','9:20 a 10:00. TPC-H SF=0,01 gerado conforme laboratório L02, não SF=1/PT-BR da turma. Não é empresa real. Recorte justificado nas três tabelas. Documento tem rubricas conflitantes: seção 6 versus rubrica anexada. Incluímos desempenho auxiliar e estrutura de repositório, mas GitLab não foi publicado e Redash não executou. Referências completas em docs/fontes.json e relatório.');
    txt(s,'Os resultados descrevem 100 fornecedores do TPC-H SF=0,01.',70,185,1120,110,36,true,teal);
    txt(s,'Contagens não medem gasto, capacidade ou risco financeiro.\nA distribuição uniforme serve como referência, sem meta presumida.',70,350,1120,140,31);
    txt(s,'Próximo passo: executar o dashboard no Redash e ampliar a análise com dados operacionais.',70,550,1120,110,31);
    return {slides:presentation.slides.items.length};
  },{artifactType:'presentation',artifactRef:'artifact_WDvFhdDHebH4oEpXxPCplywJ5woJa3CF'});
}
