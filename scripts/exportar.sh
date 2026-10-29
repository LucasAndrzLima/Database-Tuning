#!/usr/bin/env bash
set -euo pipefail
cd /projeto
mkdir -p dados evidencias
# A mesma conexão executa toda a extração em snapshot consistente, somente leitura.
# JSON_OBJECT mantém escaping de strings; --raw evita escapar o JSON uma segunda vez.
mysql --host="${MYSQL_HOST}" --port="${MYSQL_PORT}" --user="${MYSQL_USER}" \
  --database="${MYSQL_DATABASE}" --default-character-set=utf8mb4 \
  --batch --raw --skip-column-names \
  < sql/01_extrair.sql > dados/extracao.ndjson.tmp
mv dados/extracao.ndjson.tmp dados/extracao.ndjson
echo "Extração SQL gravada em dados/extracao.ndjson. Execute carregar e validar."
