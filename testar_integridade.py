"""Testes de regressão com MongoDB real: ausências, duplicação e geografia inválida.
Não acessa nem altera a coleção principal. Remove apenas o banco temporário criado aqui.
"""
import json
from pathlib import Path
from uuid import uuid4
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from projeto import documento,ROOT

def main():
    import os
    c=MongoClient(os.getenv('MONGO_URI','mongodb://127.0.0.1:27017'),serverSelectionTimeoutMS=5000)
    nome='n2_teste_'+uuid4().hex;db=c[nome]
    try:
        db.dim_regiao.insert_many([{'_id':0,'nome':'R0'},{'_id':1,'nome':'R1'}])
        db.dim_pais.insert_many([{'_id':0,'nome':'P0','regiao':{'id':0,'nome':'R0'}},
            {'_id':1,'nome':'P1','regiao':{'id':1,'nome':'R1'}}])
        row={'fornecedor_id':1,'fornecedor':'F1','pais_id':0,'pais':'P0','regiao_id':0,'regiao':'R0'}
        doc=documento(row);db.fato_fornecedores.insert_one(doc)
        pipe=json.loads((ROOT/'consultas/mongodb/01_participacao_regiao.json').read_text(encoding='utf-8'))
        res=list(db.fato_fornecedores.aggregate(pipe))
        assert [(r['regiao_id'],r['fornecedores'],r['participacao_pct']) for r in res]==[(0,1,100.0),(1,0,0.0)]
        dup=False
        try:db.fato_fornecedores.insert_one(doc.copy())
        except DuplicateKeyError:dup=True
        assert dup,'ID repetido deve falhar'
        invalida=False
        try:documento(dict(row,pais=None))
        except ValueError:invalida=True
        assert invalida,'Órfão deve falhar'
        db.fato_fornecedores.delete_many({})
        res=list(db.fato_fornecedores.aggregate(pipe))
        assert all(r['fornecedores']==0 and r['participacao_pct'] is None for r in res)
        result={'mongo_real':True,'regiao_sem_fornecedor_preservada':True,
            'duplicata_rejeitada':True,'geografia_orfa_rejeitada':True,'denominador_zero_sem_divisao':True}
        (ROOT/'evidencias/testes_integridade.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print('Testes de integridade: aprovados')
    finally:
        c.drop_database(nome);c.close()

if __name__=='__main__':main()
