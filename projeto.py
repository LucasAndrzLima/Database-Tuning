"""ETL, validação SQL/MongoDB e evidências. Somente o banco Mongo definido no .env recebe escrita."""
import argparse
import hashlib
import json
import os
import statistics
import time
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pymysql
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

ROOT=Path(__file__).resolve().parent
load_dotenv(ROOT/'.env')

def normal(v):
    if isinstance(v,Decimal):return float(v)
    if isinstance(v,datetime):return v.isoformat(timespec='milliseconds')
    if isinstance(v,dict):return {k:normal(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)):return [normal(x) for x in v]
    return v

def salvar(nome,obj):
    p=ROOT/'evidencias'/nome;p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(normal(obj),ensure_ascii=False,indent=2),encoding='utf-8')

def sql_file(conn,nome):
    with conn.cursor() as c:
        c.execute((ROOT/'sql'/nome).read_text(encoding='utf-8'))
        return list(c.fetchall())

def documento(r):
    if r['pais'] is None or r['regiao'] is None or not r['fornecedor'].strip():
        raise ValueError('Fornecedor sem nome ou geografia válida: '+str(r['fornecedor_id']))
    return {'_id':r['fornecedor_id'],
        'fornecedor':{'id':r['fornecedor_id'],'nome':r['fornecedor'].strip()},
        'geografia':{'paisId':r['pais_id'],'pais':r['pais'].strip(),
            'regiaoId':r['regiao_id'],'regiao':r['regiao'].strip()},
        'quantidadeFornecedores':1}

def digest(d):
    return hashlib.sha256(json.dumps(normal(d),ensure_ascii=False,sort_keys=True,
        separators=(',',':')).encode('utf-8')).hexdigest()

def conectar():
    sql=pymysql.connect(host=os.getenv('MYSQL_HOST','127.0.0.1'),
        port=int(os.getenv('MYSQL_PORT','3308')),user=os.getenv('MYSQL_USER','root'),
        password=os.environ['MYSQL_PASSWORD'],database=os.getenv('MYSQL_DATABASE','tpch'),
        charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor,connect_timeout=10,
        read_timeout=30,write_timeout=30)
    try:
        mongo=MongoClient(os.getenv('MONGO_URI','mongodb://127.0.0.1:27017'),serverSelectionTimeoutMS=10000)
        mongo.admin.command('ping')
    except Exception:
        sql.close();raise
    banco=os.getenv('MONGO_DATABASE','n2_equipe10')
    if not banco.startswith('n2_'):
        sql.close();mongo.close();raise ValueError('Use um banco Mongo isolado cujo nome comece por n2_.')
    return sql,mongo,mongo[banco]

def carregar(sql,db):
    raw=sql_file(sql,'01_extracao.sql')
    integridade=sql_file(sql,'04_integridade.sql')
    if any(x['inconsistencias'] for x in integridade) or not raw:
        salvar('integridade_rejeitada.json',integridade)
        raise RuntimeError('Fonte vazia ou inconsistente. Carga não publicada.')
    docs=[documento(r) for r in raw]
    with sql.cursor() as c:
        c.execute('SELECT r_regionkey AS _id, TRIM(r_name) AS nome FROM region ORDER BY r_regionkey')
        regioes=c.fetchall()
        c.execute('''SELECT n.n_nationkey AS _id, TRIM(n.n_name) AS nome,
            r.r_regionkey AS regiao_id, TRIM(r.r_name) AS regiao
            FROM nation n JOIN region r ON r.r_regionkey=n.n_regionkey ORDER BY n.n_nationkey''')
        paises=[{'_id':r['_id'],'nome':r['nome'],'regiao':{'id':r['regiao_id'],'nome':r['regiao']}} for r in c.fetchall()]
    carga=uuid4().hex
    manifests={'id':carga,'extraido_em_utc':datetime.now(timezone.utc).isoformat(),
        'schema_mysql':os.getenv('MYSQL_DATABASE','tpch'),'escopo':'Todos os fornecedores, países e regiões da origem. Sem filtro temporal e sem LIMIT.',
        'fornecedores':len(docs),'paises':len(paises),'regioes':len(regioes),
        'sha256_projecao_origem':digest(docs)}
    colecoes={'fato_fornecedores':docs,'dim_pais':paises,'dim_regiao':regioes}
    temporarias={}
    for nome,data in colecoes.items():
        tmp=nome+'_carga_'+carga
        db.create_collection(tmp)
        if data:db[tmp].insert_many(data,ordered=True)
        actual=list(db[tmp].find().sort('_id',1))
        if digest(actual)!=digest(data):raise RuntimeError('Conteúdo divergente no staging '+tmp)
        temporarias[nome]=tmp
    db[temporarias['fato_fornecedores']].create_index([('geografia.regiaoId',1),('_id',1)],name='ix_regiao_fornecedor')
    db[temporarias['fato_fornecedores']].create_index([('geografia.paisId',1)],name='ix_pais')
    # Publicação sequencial: executar em janela sem leitores/cargas concorrentes.
    for nome,tmp in temporarias.items():
        if nome in db.list_collection_names():db[nome].rename(nome+'_backup_'+carga)
        db[tmp].rename(nome)
    db['cargas'].insert_one(manifests.copy())
    salvar('carga.json',manifests)
    return manifests

def indicadores(db):
    result={}
    for p in sorted((ROOT/'consultas/mongodb').glob('*.json')):
        result[p.stem]=list(db.fato_fornecedores.aggregate(json.loads(p.read_text(encoding='utf-8')),allowDiskUse=True))
    return result

def conferir(sql,db):
    raw=sql_file(sql,'01_extracao.sql');esperado=[documento(r) for r in raw]
    destino=list(db.fato_fornecedores.find().sort('_id',1))
    by_id={d['_id']:d for d in destino}
    ids_esperados={d['_id'] for d in esperado}
    divergentes=[d['_id'] for d in esperado if d['_id'] not in by_id or digest(d)!=digest(by_id[d['_id']])]
    extras=sorted(set(by_id)-ids_esperados)
    controles=sql_file(sql,'04_integridade.sql')
    ind=indicadores(db)
    a=normal(sql_file(sql,'02_regioes.sql'));b=ind['01_participacao_regiao']
    c=normal(sql_file(sql,'03_paises.sql'));d=ind['02_distribuicao_pais']
    def igual(left,right,id_field):
        l=sorted(left,key=lambda x:x[id_field]);r=sorted(right,key=lambda x:x[id_field])
        if len(l)!=len(r):return False
        for x,y in zip(l,r):
            if set(x)!=set(y):return False
            for k,v in x.items():
                if k=='participacao_pct':
                    if v is None or y[k] is None or abs(v-y[k])>0.000051:return False
                elif v!=y[k]:return False
        return True
    regiao_ok=igual(a,b,'regiao_id');pais_ok=igual(c,d,'pais_id')
    # Também valida dimensões completas, inclusive países/regiões sem fornecedor.
    with sql.cursor() as cur:
        cur.execute('SELECT COUNT(*) AS n FROM nation');n_paises=cur.fetchone()['n']
        cur.execute('SELECT COUNT(*) AS n FROM region');n_regioes=cur.fetchone()['n']
    dimensoes_ok=db.dim_pais.count_documents({})==n_paises and db.dim_regiao.count_documents({})==n_regioes
    aprovado=bool(esperado) and len(esperado)==len(destino) and not divergentes and not extras and regiao_ok and pais_ok and dimensoes_ok and not any(x['inconsistencias'] for x in controles)
    return {'aprovado':aprovado,'instante_utc':datetime.now(timezone.utc).isoformat(),
        'mysql':{'fornecedores':len(esperado),'paises':n_paises,'regioes':n_regioes},
        'mongodb':{'fornecedores':len(destino),'paises':db.dim_pais.count_documents({}),'regioes':db.dim_regiao.count_documents({})},
        'fornecedores_divergentes':divergentes,'ids_extras':extras,'integridade_sql':controles,
        'regioes_equivalentes':regiao_ok,'paises_equivalentes':pais_ok,'dimensoes_equivalentes':dimensoes_ok,
        'soma_participacoes_regioes':sum(x['participacao_pct'] for x in b),
        'comparacao_regioes':{'mysql':a,'mongodb':b},'comparacao_paises':{'mysql':c,'mongodb':d},
        'sha256_mysql':digest(esperado),'sha256_mongodb':digest(destino)},ind

def desempenho(sql,db):
    rid=db.dim_regiao.find_one(sort=[('_id',1)])['_id']
    with sql.cursor() as c:
        query='''SELECT s.s_suppkey FROM supplier s JOIN nation n ON n.n_nationkey=s.s_nationkey
            WHERE n.n_regionkey=%s ORDER BY s.s_suppkey'''
        c.execute('EXPLAIN FORMAT=JSON '+query,(rid,));plano_sql=c.fetchone()
        c.execute('EXPLAIN ANALYZE '+query,(rid,));plano_real=c.fetchall()
        t_sql=[]
        for _ in range(7):
            t=time.perf_counter();c.execute(query,(rid,));ids_sql=[r['s_suppkey'] for r in c.fetchall()];t_sql.append((time.perf_counter()-t)*1000)
    filtro={'geografia.regiaoId':rid}
    proj={'_id':1}
    exp={};times={}
    for nome,hint in [('natural',{'$natural':1}),('indice','ix_regiao_fornecedor')]:
        cmd={'find':'fato_fornecedores','filter':filtro,'projection':proj,'sort':{'_id':1},'hint':hint}
        exp[nome]=db.command('explain',cmd,verbosity='executionStats')
        samples=[]
        for _ in range(7):
            t=time.perf_counter();ids=[r['_id'] for r in db.fato_fornecedores.find(filtro,proj).sort('_id',1).hint(hint)];samples.append((time.perf_counter()-t)*1000)
        if ids!=ids_sql:raise RuntimeError('Consulta de desempenho perdeu equivalência de IDs')
        times[nome]={'amostras_ms':samples,'mediana_ms':statistics.median(samples)}
    exp['automatico']=db.command('explain',{'find':'fato_fornecedores','filter':filtro,'projection':proj,'sort':{'_id':1}},verbosity='executionStats')
    return {'regiao_id_filtrada':rid,'repeticoes':7,'equivalencia_ids':True,'mysql_plano_estimado':plano_sql,
        'mysql_plano_executado':plano_real,'mysql_amostras_ms':t_sql,'mysql_mediana_ms':statistics.median(t_sql),
        'mongodb_tempos':times,'mongodb_explain':exp,
        'limite':'Experimento auxiliar no recorte. Tempos incluem driver e transferência. Hints forçam caminhos de acesso; não comprovam superioridade de um SGBD nem benefício em agregações globais.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('acao',choices=['executar','validar','exportar','desempenho'])
    args=p.parse_args()
    sql,mongo,db=conectar()
    try:
        with sql.cursor() as c:
            c.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')
            c.execute('START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY')
        if args.acao=='executar':carregar(sql,db)
        if args.acao in ['executar','validar']:
            valid,ind=conferir(sql,db);salvar('validacao.json',valid);salvar('indicadores.json',ind)
            if not valid['aprovado']:raise RuntimeError('Validação reprovada. Consulte evidencias/validacao.json')
            print('Validação aprovada:',valid['mysql'])
        if args.acao=='exportar':salvar('indicadores.json',indicadores(db))
        if args.acao in ['executar','desempenho']:
            salvar('desempenho.json',desempenho(sql,db))
        salvar('versoes.json',{'pymysql':pymysql.VERSION_STRING,'mongo_server':mongo.server_info()['version'],
            'schema_mysql':os.getenv('MYSQL_DATABASE','tpch'),'ambiente':'Execução real, sem mocks'})
    finally:
        sql.rollback();sql.close();mongo.close()

if __name__=='__main__':main()
