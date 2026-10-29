"""Escreve pipelines nativos e a variante de ordenação do conector Redash do L03."""
import copy
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def contagem(nivel):
    regiao=nivel=='regiao'
    chave={'regiao_id':'$geografia.regiaoId','regiao':'$geografia.regiao'} if regiao else {
        'pais_id':'$geografia.paisId','pais':'$geografia.pais','regiao':'$geografia.regiao'}
    zero={'regiao_id':'$_id','regiao':'$nome'} if regiao else {
        'pais_id':'$_id','pais':'$nome','regiao':'$regiao.nome'}
    return [{'$group':{'_id':chave,'fornecedores':{'$sum':'$quantidadeFornecedores'}}},
        {'$unionWith':{'coll':'dim_regiao' if regiao else 'dim_pais','pipeline':[
            {'$project':{'_id':zero,'fornecedores':{'$literal':0}}}]}},
        {'$group':{'_id':'$_id','fornecedores':{'$sum':'$fornecedores'}}}]

def distribuicao(nivel):
    fields=['regiao_id','regiao'] if nivel=='regiao' else ['pais_id','pais','regiao']
    project={'_id':0,'fornecedores':'$linhas.fornecedores',
        'participacao_pct':{'$cond':[{'$gt':['$total',0]},
          {'$round':[{'$multiply':[100,{'$divide':['$linhas.fornecedores','$total']}]},4]},None]}}
    project.update({f:'$linhas._id.'+f for f in fields})
    return contagem(nivel)+[{'$group':{'_id':None,'total':{'$sum':'$fornecedores'},
        'linhas':{'$push':'$$ROOT'}}},{'$unwind':'$linhas'},
        {'$project':project},{'$sort':{'fornecedores':-1,fields[0]:1}}]

def construir():
    pipes={
      '01_participacao_regiao':distribuicao('regiao'),
      '02_distribuicao_pais':distribuicao('pais'),
      '03_resumo':[{'$group':{'_id':None,'totalFornecedores':{'$sum':1},
          'paises':{'$addToSet':'$geografia.paisId'},'regioes':{'$addToSet':'$geografia.regiaoId'}}},
          {'$project':{'_id':0,'totalFornecedores':1,'paisesComFornecedores':{'$size':'$paises'},
              'regioesComFornecedores':{'$size':'$regioes'}}}],
      '04_concentracao_regional':contagem('regiao')+[
          {'$group':{'_id':None,'total':{'$sum':'$fornecedores'},
              'regioesCadastradas':{'$sum':1},'maximo':{'$max':'$fornecedores'},
              'somaQuadrados':{'$sum':{'$multiply':['$fornecedores','$fornecedores']}}}},
          {'$project':{'_id':0,'maiorParticipacaoPct':{'$multiply':[100,{'$divide':['$maximo','$total']}]},
              'hhiRegional':{'$divide':[{'$multiply':[10000,'$somaQuadrados']},{'$multiply':['$total','$total']}]},
              'referenciaUniformeHHI':{'$divide':[10000,'$regioesCadastradas']}}}]
    }
    for nome,pipe in pipes.items():
        for kind in ['mongodb','redash']:
            out=ROOT/'consultas'/kind;out.mkdir(parents=True,exist_ok=True)
            v=copy.deepcopy(pipe)
            if kind=='redash':
                def sort_redash(x):
                    if isinstance(x,dict):
                        for k,val in list(x.items()):
                            if k=='$sort':x[k]=[{'name':a,'direction':b} for a,b in val.items()]
                            else:sort_redash(val)
                    elif isinstance(x,list):
                        for val in x:sort_redash(val)
                sort_redash(v)
                v={'collection':'fato_fornecedores','aggregate':v,'allowDiskUse':True}
            (out/(nome+'.json')).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':construir()
