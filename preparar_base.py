"""Gera TPC-H SF=0.01 como no L02, passo 9, e carrega só supplier/nation/region.

Escreve APENAS em um schema novo cujo nome começa por n2_. Se o schema existir,
interrompe sem alterar tabelas. Não substitui a base da turma.
"""
import csv
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
import duckdb
import pymysql
from dotenv import load_dotenv

ROOT=Path(__file__).resolve().parent
load_dotenv(ROOT/'.env')

DDL={
 'region': '''CREATE TABLE region(r_regionkey INT PRIMARY KEY, r_name CHAR(25) NOT NULL,
 r_comment VARCHAR(152)) ENGINE=InnoDB''',
 'nation': '''CREATE TABLE nation(n_nationkey INT PRIMARY KEY, n_name CHAR(25) NOT NULL,
 n_regionkey INT NOT NULL, n_comment VARCHAR(152),
 FOREIGN KEY(n_regionkey) REFERENCES region(r_regionkey)) ENGINE=InnoDB''',
 'supplier': '''CREATE TABLE supplier(s_suppkey INT PRIMARY KEY, s_name CHAR(25) NOT NULL,
 s_address VARCHAR(40), s_nationkey INT NOT NULL, s_phone CHAR(15),
 s_acctbal DECIMAL(15,2), s_comment VARCHAR(101),
 FOREIGN KEY(s_nationkey) REFERENCES nation(n_nationkey)) ENGINE=InnoDB'''}

def main():
    schema=os.environ['MYSQL_DATABASE']
    if not schema.startswith('n2_') or not schema.replace('_','').isalnum():
        raise ValueError('Por segurança, a geração exige um schema novo n2_...')
    conn=pymysql.connect(host=os.getenv('MYSQL_HOST','127.0.0.1'),
        port=int(os.getenv('MYSQL_PORT','3308')), user=os.getenv('MYSQL_USER','root'),
        password=os.environ['MYSQL_PASSWORD'],charset='utf8mb4')
    try:
        with conn.cursor() as c:
            c.execute('SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME=%s',(schema,))
            if c.fetchone():
                raise RuntimeError('Schema já existe; nada foi substituído. Para usar os dados, execute projeto.py executar.')
        # Gera em memória, sem modificar bancos preexistentes.
        d=duckdb.connect()
        d.execute('INSTALL tpch');d.execute('LOAD tpch');d.execute('CALL dbgen(sf=0.01)')
        out=ROOT/'dados';out.mkdir(exist_ok=True)
        manifesto={'origem':'DuckDB extension tpch / dbgen', 'duckdb':duckdb.__version__,
            'scale_factor':0.01,'schema_mysql':schema,
            'observacao':'Base reduzida gerada para este projeto. Não é a imagem SF=1/PT-BR da turma.',
            'gerado_em_utc':datetime.now(timezone.utc).isoformat(),'tabelas':{}}
        with conn.cursor() as c:
            c.execute(f'CREATE DATABASE `{schema}` CHARACTER SET utf8mb4 COLLATE utf8mb4_bin')
            c.execute(f'USE `{schema}`')
            for tabela,ddl in DDL.items():
                c.execute(ddl)
                rows=d.execute(f'SELECT * FROM {tabela} ORDER BY 1').fetchall()
                placeholders=','.join(['%s']*len(rows[0]))
                c.executemany(f'INSERT INTO {tabela} VALUES ({placeholders})',rows)
                f=out/(tabela+'.csv')
                with f.open('w',encoding='utf-8',newline='') as fp:
                    w=csv.writer(fp);w.writerow([x[0] for x in d.description]);w.writerows(rows)
                manifesto['tabelas'][tabela]={'registros':len(rows),'sha256_csv':hashlib.sha256(f.read_bytes()).hexdigest()}
        conn.commit()
        (out/'origem.json').write_text(json.dumps(manifesto,ensure_ascii=False,indent=2),encoding='utf-8')
        d.close()
        print(json.dumps(manifesto,ensure_ascii=False,indent=2))
    finally:
        conn.close()

if __name__=='__main__':main()
