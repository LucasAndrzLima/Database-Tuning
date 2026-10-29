"""Copia o snapshot nativo para um MongoDB acessível ao Redash sem misturar versões.
Uso: python importar_mongo_redash.py --destino mongodb://127.0.0.1:27018
O Compose desta entrega publica seu Mongo na porta 27018 para evitar o serviço nativo.
"""
import argparse
import os
from uuid import uuid4
from pymongo import MongoClient
from projeto import digest

def main():
    p=argparse.ArgumentParser();p.add_argument('--destino',required=True);args=p.parse_args()
    origem=os.getenv('MONGO_URI','mongodb://127.0.0.1:27017')
    if origem.rstrip('/')==args.destino.rstrip('/'):raise ValueError('Origem e destino devem ser distintos')
    a=MongoClient(origem,serverSelectionTimeoutMS=5000);b=MongoClient(args.destino,serverSelectionTimeoutMS=5000)
    nome=os.getenv('MONGO_DATABASE','n2_equipe10')
    if not nome.startswith('n2_'):raise ValueError('Use o banco dedicado n2_...')
    try:
        for col in ['dim_regiao','dim_pais','fato_fornecedores']:
            rows=list(a[nome][col].find().sort('_id',1))
            if not rows:raise ValueError('Coleção vazia na origem: '+col)
            uid=uuid4().hex;tmp=col+'_importacao_'+uid
            b[nome][tmp].insert_many(rows)
            if digest(rows)!=digest(list(b[nome][tmp].find().sort('_id',1))):raise RuntimeError('Cópia divergente')
            if col in b[nome].list_collection_names():b[nome][col].rename(col+'_backup_'+uid)
            b[nome][tmp].rename(col)
        b[nome].fato_fornecedores.create_index([('geografia.regiaoId',1),('_id',1)],name='ix_regiao_fornecedor')
        print('Três coleções copiadas e verificadas. Execute as queries no Redash.')
    finally:a.close();b.close()

if __name__=='__main__':main()
