"""Gera relatório e gráficos a partir das evidências reais da execução."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Image,Preformatted
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing,Rect,String,Line

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output';OUT.mkdir(exist_ok=True)
CHARTS=OUT/'graficos';CHARTS.mkdir(exist_ok=True)
def ler(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
ind=ler('evidencias/indicadores.json');val=ler('evidencias/validacao.json')
origem=ler('dados/origem.json');perf=ler('evidencias/desempenho.json');testes=ler('evidencias/testes_integridade.json')
reg=ind['01_participacao_regiao'];paises=ind['02_distribuicao_pais'];conc=ind['04_concentracao_regional'][0]
if not val['aprovado']:raise RuntimeError('O relatório exige uma validação aprovada')
trad={'ASIA':'Ásia','AFRICA':'África','AMERICA':'América','EUROPE':'Europa','MIDDLE EAST':'Oriente Médio'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False})
fig,ax=plt.subplots(figsize=(9.5,3.6),layout='constrained')
bars=ax.barh([trad[r['regiao']] for r in reg],[r['participacao_pct'] for r in reg],color='#176B73',height=.60)
ax.invert_yaxis();ax.set_xlim(0,32);ax.set_xlabel('Participação no cadastro de fornecedores (%)');ax.set_axisbelow(True);ax.grid(axis='x',alpha=.15)
for b,r in zip(bars,reg):ax.text(b.get_width()+.4,b.get_y()+b.get_height()/2,f"{r['participacao_pct']:.0f}%  ({r['fornecedores']})",va='center',fontsize=11)
fig.savefig(CHARTS/'participacao_regiao.png',dpi=200);plt.close(fig)
seis=[x for x in paises if x['fornecedores']>=6]
fig,ax=plt.subplots(figsize=(9.5,3.3),layout='constrained')
nomes={'UNITED STATES':'Estados Unidos','MOZAMBIQUE':'Moçambique','CHINA':'China','EGYPT':'Egito','KENYA':'Quênia','VIETNAM':'Vietnã'}
bars=ax.barh([nomes[x['pais']] for x in seis],[x['fornecedores'] for x in seis],color='#176B73',height=.6)
ax.invert_yaxis();ax.set_xlim(0,10);ax.set_xlabel('Fornecedores cadastrados (unidades)');ax.set_axisbelow(True);ax.grid(axis='x',alpha=.15)
for b,r in zip(bars,seis):ax.text(b.get_width()+.12,b.get_y()+b.get_height()/2,str(r['fornecedores']),va='center')
fig.savefig(CHARTS/'fornecedores_pais.png',dpi=200);plt.close(fig)

pdfmetrics.registerFont(TTFont('ArialN2','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialN2Bold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('ArialN2',normal='ArialN2',bold='ArialN2Bold',italic='ArialN2',boldItalic='ArialN2Bold')
styles=getSampleStyleSheet()
for name in ['Normal','BodyText','Heading1','Heading2','Heading3','Title']:
 styles[name].fontName='ArialN2Bold' if name.startswith('Heading') or name=='Title' else 'ArialN2'
styles['BodyText'].fontSize=10.2;styles['BodyText'].leading=14.5;styles['BodyText'].spaceAfter=9
styles['Heading1'].fontSize=20;styles['Heading1'].leading=24;styles['Heading1'].spaceAfter=14;styles['Heading1'].textColor=colors.HexColor('#183547')
styles['Heading2'].fontSize=13;styles['Heading2'].leading=17;styles['Heading2'].spaceBefore=10;styles['Heading2'].spaceAfter=8;styles['Heading2'].textColor=colors.HexColor('#176B73')
styles.add(ParagraphStyle(name='CapaN2',fontName='ArialN2Bold',fontSize=29,leading=34,textColor=colors.HexColor('#183547'),spaceAfter=18))
styles.add(ParagraphStyle(name='SmallN2',parent=styles['BodyText'],fontSize=8.5,leading=11,spaceAfter=5))
styles.add(ParagraphStyle(name='TableN2',parent=styles['BodyText'],fontSize=9,leading=12,spaceAfter=0))
story=[]
def p(t,sty='BodyText'):story.append(Paragraph(t,styles[sty]))
def h(t):p(t,'Heading2')
def title(n,t):p(f'{n}. {t}','Heading1')
def page():story.append(PageBreak())
def table(rows,widths,small=False):
 data=[[Paragraph(escape(str(v)),styles['SmallN2' if small else 'TableN2']) for v in row] for row in rows]
 t=Table(data,colWidths=widths,hAlign='LEFT',repeatRows=1)
 t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6eff2')),
  ('LINEBELOW',(0,0),(-1,0),.8,colors.HexColor('#176B73')),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#d8e0e4')),
  ('TOPPADDING',(0,0),(-1,-1),6 if not small else 3),('BOTTOMPADDING',(0,0),(-1,-1),6 if not small else 3)]))
 story.append(t)
def chart(f,w=500,h=195):story.append(Image(str(CHARTS/f),width=w,height=h,kind='proportional'))

p('Distribuição geográfica<br/>dos fornecedores','CapaN2')
p('Avaliação Somativa N2 - Equipe 10','Heading1')
p('Database Performance Tuning<br/>Sistemas de Informação - 4º A - Noite - 2026/2')
p('<b>Integrantes</b><br/>Bárbara Tebaldi Franco<br/>Henrique Dias de Carvalho Junior<br/>Joao Vitor Lima Cecilio<br/>Lucas Andrzejewski de Lima')
p('<b>Apresentação:</b> 17/11/2026, das 21h40 às 21h50.<br/><b>Data da elaboração:</b> 28/10/2026 (America/Sao_Paulo).')
h('Resumo executivo')
p('O projeto responde ao Desafio 10 do catálogo atualizado: analisar a distribuição geográfica dos fornecedores para apoiar o planejamento de suprimentos. O indicador principal é a participação de cada região na quantidade total de fornecedores cadastrados.')
p('A execução usa TPC-H SF=0,01 gerado com DuckDB, conforme o laboratório L02, passo 9. As três tabelas necessárias foram carregadas em MySQL e transformadas no MongoDB. Foram validados 100 fornecedores, 25 países e cinco regiões, sem divergências nos documentos dos fornecedores e nos indicadores regionais e nacionais.')
p('A Ásia concentra 27% dos fornecedores e o Oriente Médio, 12%, com diferença de 15 pontos percentuais. Os EUA reúnem 40% dos cadastros da América; o Egito, 50% dos do Oriente Médio. A contagem orienta a investigação de alternativas, mas não mede gasto, capacidade ou risco financeiro.')
h('Situação da entrega')
p('<b>Executado:</b> geração do recorte, carga MySQL, ETL MongoDB, validação, consultas, testes de integridade e gráficos deste relatório. <b>Pendente:</b> executar os gráficos na instância Redash, indisponível nesta máquina por falha de inicialização do Docker. Os gráficos aqui apresentados não são capturas do Redash. A estrutura de código está preparada para repositório, sem publicação GitLab.')
page()
title(1,'Problema, escopo e indicadores')
p('Pergunta gerencial: em quais regiões e países o cadastro concentra fornecedores e onde a empresa dispõe de menos alternativas cadastradas? A decisão apoiada é priorizar a investigação e a qualificação de opções de suprimento, considerando a necessidade operacional de cada localidade.')
h('Definição do universo')
p('O universo é a totalidade dos 100 fornecedores da escala TPC-H SF=0,01 gerada neste projeto. A consulta não usa LIMIT, não exige vendas e não filtra data. As cinco regiões e os 25 países são preservados, inclusive se alguma categoria não tiver fornecedores. A geografia sempre é a do fornecedor.')
p('A base foi gerada pela extensão tpch do DuckDB 2.0.0 e carregada em schema MySQL isolado. Não é a imagem SF=1/PT-BR dos exercícios de tuning. O recorte temático contém integralmente supplier, nation e region dessa escala. As outras tabelas não são necessárias à pergunta e não entram na carga relacional. Não se generalizam os resultados para a base completa da turma ou uma empresa real.')
table([['Medida/indicador','Regra e unidade'],['Fornecedores cadastrados','Um registro por s_suppkey; contagem de cadastros.'],['Participação regional','100 × fornecedores da região / fornecedores totais do mesmo snapshot. Unidade: %.'],['Distribuição por país','Contagem de fornecedores por país, com a respectiva região e participação no total.'],['Cobertura','Número de países e regiões com ao menos um fornecedor.'],['Amplitude regional','Maior participação menos menor participação. Unidade: pontos percentuais.'],['HHI regional complementar','Soma dos quadrados das participações em pontos percentuais. Referência uniforme = 10000 / número de regiões.']], [140,365])
h('Indicador e objetivo')
p('A participação é o indicador principal solicitado. Sem uma meta gerencial fornecida, não se declara meta de KPI atingida. Uma participação uniforme de 20% por região é apenas referência matemática; a necessidade de suprimentos pode justificar distribuições diferentes.')
page()
title(2,'Modelo estrela e origem dos campos')
p('Grão da fato: um fornecedor cadastrado na fotografia atual. A chave natural é s_suppkey. A medida quantidadeFornecedores vale 1 para cada cadastro. O modelo representa cobertura cadastral, sem medidas financeiras.')
d=Drawing(505,160)
for x,y,w,ht,a,b in [(0,92,185,55,'DIM_FORNECEDOR','ID e nome'),(320,92,185,55,'DIM_GEOGRAFIA','País e região'),(155,0,195,60,'FATO_CADASTRO','Um fornecedor; quantidade = 1')]:
 d.add(Rect(x,y,w,ht,rx=3,fillColor=colors.HexColor('#e6eff2'),strokeColor=colors.HexColor('#176B73')))
 d.add(String(x+w/2,y+ht-18,a,fontName='ArialN2Bold',fontSize=10,textAnchor='middle'))
 d.add(String(x+w/2,y+14,b,fontName='ArialN2',fontSize=8,textAnchor='middle'))
for a in [(92,92,92,30),(92,30,155,30),(412,92,412,30),(350,30,412,30)]:d.add(Line(*a,strokeColor=colors.HexColor('#176B73')))
story.append(d);story.append(Spacer(1,12))
table([['Origem relacional','Destino analítico'],['supplier.s_suppkey','_id e fornecedor.id; chave única do cadastro.'],['supplier.s_name','fornecedor.nome; remoção de espaços externos de CHAR.'],['supplier.s_nationkey = nation.n_nationkey','Relacionamento para identificar país do fornecedor.'],['nation.n_name','geografia.pais.'],['nation.n_regionkey = region.r_regionkey','Relacionamento para identificar a região.'],['region.r_name','geografia.regiao.']], [245,260])
h('Granularidade e aditividade')
p('Não se juntam lineitem ou partsupp ao fato: isso repetiria fornecedores com vários itens ou peças. Também não se utiliza a região do cliente. O fato pode ser contado por país ou região sem COUNT DISTINCT porque o ID é único. Não existe período de vendas neste modelo.')
p('A data da carga fica nos metadados técnicos. Uma coleção contém apenas o snapshot ativo. Caso o projeto evolua para múltiplos snapshots, deve incluir uma dimensão de referência e filtrar uma única fotografia: contar o mesmo fornecedor em datas diferentes não representa fornecedores distintos.')
page()
title(3,'MongoDB e processo ETL')
h('Representação documental')
p('Adota-se embedding de fornecedor e geografia no fato, pois são atributos pequenos usados juntos nas análises e estáveis nesta fotografia. As coleções auxiliares dim_pais e dim_regiao mantêm o catálogo geográfico para incluir categorias sem fornecedores. Essa representação materializa o modelo estrela conceitual sem exigir uma coleção por dimensão lógica.')
p('Documento ilustrativo do formato, com nomes genéricos; não corresponde a um resultado individual da carga:', 'SmallN2')
story.append(Preformatted('''{
  "_id": 1,
  "fornecedor": {"id": 1, "nome": "Fornecedor ilustrativo"},
  "geografia": {
    "paisId": 0, "pais": "País ilustrativo",
    "regiaoId": 0, "regiao": "Região ilustrativa"
  },
  "quantidadeFornecedores": 1
}''',ParagraphStyle(name='CodeN2',fontName='Courier',fontSize=9,leading=12)))
p('A vantagem é agrupar os cadastros diretamente pelos campos geográficos. A contrapartida é repetir os nomes geográficos e precisar recarregar o snapshot se os atributos mudarem. Referencing seria adequado para atualizações frequentes e independentes. Não se incorporam listas ilimitadas de fornecedores dentro de uma região.')
h('Extração, transformação e carga')
p('<b>Extract:</b> leitura MySQL em transação de snapshot consistente e somente leitura. A consulta usa LEFT JOIN para detectar referências ausentes. <b>Transform:</b> preservação dos IDs, remoção de espaços de CHAR, rejeição de nome vazio ou geografia ausente e atribuição da medida 1. <b>Load:</b> inserção em coleções temporárias com ID único, comparação do conteúdo e criação de índices.')
p('Depois da conferência, as coleções anteriores são preservadas com nome de backup e o novo snapshot assume os nomes de consulta. Assim, uma mudança de escopo não mistura documentos antigos com a nova carga. A publicação de três coleções é sequencial e requer uma janela sem leitores ou cargas concorrentes; não é uma transação única no MongoDB standalone.')
h('Reprodutibilidade')
p('preparar_base.py gera a escala e carrega um schema novo n2_..., sem substituir schemas existentes. projeto.py executa a ETL e salva manifesto, indicadores, validação e versões. Os CSVs da origem e seus hashes permitem rastrear os dados. As conexões ficam em .env local, excluído do pacote de entrega.')
page()
title(4,'Validação comparativa e integridade')
table([['Controle','MySQL','MongoDB','Resultado'],['Fornecedores',val['mysql']['fornecedores'],val['mongodb']['fornecedores'],'Correspondente'],['Países',val['mysql']['paises'],val['mongodb']['paises'],'Correspondente'],['Regiões',val['mysql']['regioes'],val['mongodb']['regioes'],'Correspondente'],['Fornecedores divergentes','Referência','0','Aprovado'],['IDs adicionais','Referência','0','Aprovado'],['Indicadores regionais','SQL independente','Equivalentes','Aprovado'],['Indicadores por país','SQL independente','Equivalentes','Aprovado']], [185,90,110,120])
h('Método de conferência')
p('A validação compara todos os campos projetados de todos os fornecedores, preservando a chave de origem, e detecta ausências, alterações ou documentos adicionais. As consultas SQL independentes 02_regioes.sql e 03_paises.sql calculam contagens e porcentagens diretamente nas tabelas relacionais. Os pipelines MongoDB são comparados por ID geográfico.')
p('As contagens são exatas. As participações são arredondadas a quatro casas decimais e comparadas com tolerância numérica de 0,000051 ponto percentual. Neste recorte, a soma regional é exatamente 100%. Não se confunde a equivalência dos dados com uma comparação de velocidade.')
h('Testes de casos críticos em MongoDB real')
table([['Caso','Comportamento confirmado'],['Região sem fornecedor','A região continua no resultado, com contagem e participação iguais a zero.'],['ID repetido','Inserção rejeitada pela chave única _id.'],['Fornecedor sem país','Transformação rejeitada, impedindo publicação de conteúdo inconsistente.'],['Universo sem fornecedores','Pipeline evita divisão por zero e retorna participação nula; a carga principal rejeita fonte vazia.']], [150,355])
h('Evidências')
p('evidencias/validacao.json contém contagens, comparações completas por região e país e hashes da projeção de origem e destino. evidencias/testes_integridade.json registra os testes. A validação foi aprovada na execução real; as coleções dos testes foram isoladas em banco temporário e removidas ao término.')
p('O conferente relê a mesma origem da ETL. A correção semântica também depende da revisão do grão e das chaves; um hash igual, sozinho, não prova que a pergunta de negócio foi corretamente modelada. Por isso o relatório explicita as relações e os denominadores.')
page()
title(5,'Resultado principal: participação regional')
chart('participacao_regiao.png',500,195)
p('Fonte: agregação MongoDB sobre o snapshot TPC-H SF=0,01, conferida com consulta SQL independente. Rótulos mostram participação e número de fornecedores. Universo: 100 cadastros.', 'SmallN2')
table([['Região do fornecedor','Quantidade','Participação'],*[[trad[x['regiao']],x['fornecedores'],f"{x['participacao_pct']:.0f}%"] for x in reg],['Total',100,'100%']], [285,110,110])
h('Leitura dos resultados')
p('A Ásia reúne 27 fornecedores e a maior participação do recorte, 27%. O Oriente Médio reúne 12, correspondentes a 12%, com a menor participação. A amplitude entre esses extremos é de 15 pontos percentuais. América e Europa têm 20 fornecedores cada, mas a igualdade regional não demonstra igualdade de cobertura por país.')
p('O HHI regional é 2114. Para cinco regiões, a referência perfeitamente uniforme seria 2000. O resultado está 114 pontos, ou 5,7%, acima dessa referência matemática. Não se aplica classificação de risco concorrencial nem se presume que o cadastro deva ser uniforme. A distribuição necessária depende de demanda, peças e viabilidade de contratação.')
h('Implicação para suprimentos')
p('O indicador ajuda a selecionar onde aprofundar a pesquisa de fornecedores. A menor quantidade de cadastros pode significar menos alternativas, mas não comprova falta de capacidade ou necessidade de ampliar compras. Qualificação, custo e atendimento precisam ser verificados antes de qualquer decisão operacional.')
page()
title(6,'Visualização complementar: países')
chart('fornecedores_pais.png',500,182)
p('Fonte: mesma carga validada. O gráfico inclui todos os seis países com pelo menos seis fornecedores; eles somam 40% do cadastro. A tabela abaixo mantém os 25 países.', 'SmallN2')
table([['País (nome do benchmark)','Região','Fornecedores','% do total'],*[[x['pais'],x['regiao'],x['fornecedores'],f"{x['participacao_pct']:.0f}%"] for x in paises]], [205,140,85,75],True)
page()
title(7,'Análise gerencial e recomendações')
table([['Achado observado','Decisão que pode apoiar','Informação adicional necessária'],['Ásia: 27%; Oriente Médio: 12%.','Priorizar investigação de alternativas onde houver demanda operacional e poucas opções cadastradas.','Peças demandadas, capacidade, localização da operação e fornecedores já qualificados.'],['EUA: 8 dos 20 fornecedores da América (40%).','Avaliar a distribuição interna e possíveis alternativas nos demais países da região.','Criticidade dos produtos, custos, prazos e barreiras de contratação.'],['Egito: 6 dos 12 fornecedores do Oriente Médio (50%).','Investigar se a concentração cadastral também aparece nas peças ou nos gastos da região.','Histórico de compras, peças atendidas e dependência operacional.'],['Todos os 25 países têm fornecedor no recorte.','Aprofundar a qualidade e a capacidade das opções existentes, sem presumir que presença cadastral seja atendimento suficiente.','Qualificação, contratos e capacidade efetiva.']], [165,180,160])
h('Conclusão gerencial')
p('A visão por região localiza a distribuição do cadastro, enquanto a visão por país revela concentrações internas que o total regional esconde. O planejamento de suprimentos pode usar esses indicadores para organizar a investigação e a qualificação de opções. A análise não justifica, isoladamente, transferir compras ou impor quotas geográficas.')
h('Limites da interpretação')
p('O TPC-H é sintético e o recorte SF=0,01 não representa estatisticamente toda a base SF=1. Não há gasto de compras, peças críticas, capacidade, risco político ou prazo neste modelo. A fotografia do cadastro não permite análise de evolução temporal. A região com mais fornecedores não é automaticamente a melhor escolha e a menor não é automaticamente inadequada.')
p('Uma evolução do projeto poderia integrar partsupp e dados de compras, mas precisaria definir outro grão e novas medidas. A contagem de fornecedores deve continuar distinta da quantidade de pares peça-fornecedor e da quantidade de itens comercializados.')
page()
title(8,'Consulta e desempenho auxiliar')
p('O enunciado atualizado dispensa comparação de desempenho entre MySQL e MongoDB. Mesmo assim, os materiais de tuning e a rubrica anexada motivaram um experimento auxiliar: consultar os mesmos IDs de fornecedores de uma região, ordenados por ID, nas duas bases.')
h('Planos e medições reais')
natural=perf['mongodb_explain']['natural']['executionStats'];idx=perf['mongodb_explain']['indice']['executionStats']
table([['Métrica MongoDB','Varredura forçada','Índice forçado'],['Fornecedores retornados',natural['nReturned'],idx['nReturned']],['Documentos examinados',natural['totalDocsExamined'],idx['totalDocsExamined']],['Chaves examinadas',natural['totalKeysExamined'],idx['totalKeysExamined']],['Mediana cliente/driver (ms)',f"{perf['mongodb_tempos']['natural']['mediana_ms']:.3f}",f"{perf['mongodb_tempos']['indice']['mediana_ms']:.3f}"]], [245,130,130])
p(f"A consulta SQL equivalente teve mediana de {perf['mysql_mediana_ms']:.3f} ms em sete execuções. Os IDs retornados coincidiram em todos os caminhos. Foram salvos EXPLAIN FORMAT=JSON e EXPLAIN ANALYZE do MySQL, além de executionStats e sete medições por estratégia no MongoDB.")
p('O índice composto ix_regiao_fornecedor cobre geografia.regiaoId e _id. Neste filtro, a leitura indexada examinou 21 chaves e zero documentos, contra 100 documentos na varredura. A redução de documentos lidos não comprovou melhoria de latência na pequena base: a mediana com índice ficou ligeiramente maior nesta medição.')
p('Os hints forçam caminhos de acesso; o plano automático também foi registrado. Os tempos incluem driver e transferência, são muito curtos e sensíveis a cache e variações do ambiente. Este ensaio não demonstra superioridade geral de um SGBD nem garante ganho em agregações globais. Não se criaram índices adicionais na origem MySQL.')
h('Pipelines e equivalência')
p('Os quatro pipelines nativos estão em consultas/mongodb e foram executados. O pipeline regional agrupa fornecedores, une o catálogo de regiões com contagens zero, soma novamente por região, calcula o total e a participação e ordena. A inclusão do catálogo mantém categorias vazias visíveis. A versão por país segue o mesmo princípio.')
p('As variantes consultas/redash usam a ordenação name/direction exigida pelo conector legado do laboratório. Sua execução dentro do Redash ainda precisa ser verificada. Não se apresentou teste de sintaxe nativa como prova de funcionamento da interface de BI.')
page()
title(9,'Dashboard, critérios e reprodução')
h('Composição do dashboard exigido')
table([['Visual no Redash','Configuração prevista'],['Barras por região','X: região; Y: participação_pct. Título: Participação dos fornecedores por região. Unidade: %.'],['Visual complementar por país','Barras ou tabela: país, região, fornecedores e participação. Manter a tabela dos 25 países acessível.'],['Cartões complementares','100 fornecedores, 25 países com fornecedor e cinco regiões com fornecedor.'],['Descrição do painel','Informar SF=0,01, universo cadastral e data de atualização. Contagem não representa gasto ou capacidade.']], [165,340])
p('<b>Pendência:</b> o Redash não está funcional nesta máquina. O Docker Desktop apresenta falhas ao inicializar seus serviços internos e não inicia os contêineres do laboratório. A ETL foi executada usando servidores nativos. A pasta dashboard contém Compose adaptado, guia de visuais e script para copiar o snapshot para o MongoDB do Compose sem conflito de portas. É necessário executar e conferir os gráficos no Redash e salvar as capturas para concluir a Etapa 6.')
h('Cobertura dos critérios e conflito no documento')
p('As etapas 1 a 5 e 7 têm implementação e evidências neste pacote. A Etapa 6 tem consultas MongoDB executadas e gráficos estáticos, mas a construção no Redash continua pendente. A seção 6 do enunciado atribui 3/4/3 pontos a ETL, dashboard e insights; a rubrica anexada nas páginas 7 e 8 apresenta 5/3/2 e inclui desempenho e GitLab. O pacote segue a descrição atual, inclui desempenho auxiliar e estrutura de repositório, mas não declara publicação GitLab ou histórico de commits inexistente. Confirmar com o professor qual rubrica prevalece.')
h('Reprodução e organização')
p('1. Instalar requirements.txt em ambiente virtual e configurar .env.<br/>2. Para uma origem nova SF=0,01, executar preparar_base.py com schema novo n2_...; para usar a base da turma, omitir essa etapa.<br/>3. Executar gerar_consultas.py, projeto.py executar e testar_integridade.py.<br/>4. Executar gerar_relatorio.py. Caso a origem mude, atualizar os números e os slides.<br/>5. Executar as visualizações no Redash conforme dashboard/LEIA-ME.md e anexar as capturas.')
p('As conexões locais não são entregues. Os arquivos dados/origem.json, CSVs e evidências preservam a linhagem do recorte utilizado. O roteiro da apresentação distribui os dez minutos entre os quatro integrantes. O README documenta execução, interpretação e pendências.')
page()
title(10,'Materiais de referência e rastreabilidade')
p('Foram consultados os 40 PDFs de cont, incluindo todas as subpastas, além da avaliação atualizada situada na pasta superior. O inventário docs/fontes.json registra caminho absoluto, número de páginas, hash SHA-256 e aplicação de cada material ao projeto. Materiais de exercícios são referência conceitual e técnica; o desafio e os requisitos decorrem do enunciado atualizado.')
table([['Conjunto de materiais','Aplicação na solução'],['Avaliação Somativa N2 atualizada','Desafio 10; etapas 1 a 7; apresentação em 17/11/2026, 21h40; identificação de conflito entre as rubricas.'],['Atividade de diagnóstico; Aulas 01 e 02b; DB L01 (15 passos)','Baseline, EXPLAIN, EXPLAIN ANALYZE, cardinalidade de JOINs e avaliação de índices com evidências.'],['Aula 03; guia MongoDB/GitLab','BSON, documentos, coleções, consultas e uso do MongoDB nativo.'],['Aula 04; DB L02 (9 passos)','Modelo dimensional, embedding/referencing, supplier-nation-region e geração TPC-H SF=0,01 no passo 9.'],['DB L03 (9 passos)','Fluxo MySQL, ETL, MongoDB e Redash; validação independente; distinção entre medida, indicador e KPI; dashboard e análise gerencial.'],['Diagrama TPCH','Tipos e chaves dos relacionamentos de fornecedor, país e região.']], [235,270])
h('Fontes técnicas primárias')
p('DuckDB. TPC-H Extension. https://duckdb.org/docs/current/core_extensions/tpch<br/>MongoDB. $unionWith. https://www.mongodb.com/docs/manual/reference/operator/aggregation/unionWith/<br/>Redash. MongoDB. https://redash.io/help/data-sources/querying/mongodb/<br/>Redash. API. https://redash.io/help/user-guide/integrations-and-api/api/', 'SmallN2')
p('Repositório didático de referência para a infraestrutura:<br/>https://gitlab.com/gilbriatore/2026/database/analytics-bi-redash.git', 'SmallN2')
h('Arquivos de evidência')
p('carga.json: escopo, quantidade e manifesto da carga.<br/>validacao.json: comparação completa MySQL/MongoDB.<br/>indicadores.json: resultados das quatro consultas.<br/>testes_integridade.json: casos críticos executados.<br/>desempenho.json: planos e medições auxiliares.<br/>versoes.json e dados/origem.json: ambiente e geração da origem.', 'SmallN2')

def rodape(c,doc):
 c.setStrokeColor(colors.HexColor('#d0dadd'));c.line(42,39,553,39)
 c.setFont('ArialN2',8);c.setFillColor(colors.HexColor('#506575'))
 c.drawString(42,25,'Equipe 10 - TPC-H SF=0,01 - Distribuição geográfica dos fornecedores')
 c.drawRightString(553,25,str(doc.page))

pdf=OUT/'relatorio_equipe10.pdf'
SimpleDocTemplate(str(pdf),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=38,bottomMargin=53,
    title='Avaliação N2 - Equipe 10 - Distribuição geográfica dos fornecedores',
    author='Bárbara Tebaldi Franco; Henrique Dias de Carvalho Junior; Joao Vitor Lima Cecilio; Lucas Andrzejewski de Lima').build(story,onFirstPage=rodape,onLaterPages=rodape)
print(pdf)
