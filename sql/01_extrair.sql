-- Desafio 10: censo dos fornecedores, com país e região DO FORNECEDOR.
-- Cada linha de saída é um JSON. Executar com mysql --batch --raw -N.
SET NAMES utf8mb4;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY;

SELECT JSON_OBJECT('tipo', 'fornecedor', 'dados', JSON_OBJECT(
    'id', s.s_suppkey, 'nome', TRIM(s.s_name),
    'paisId', n.n_nationkey, 'pais', TRIM(n.n_name),
    'regiaoId', r.r_regionkey, 'regiao', TRIM(r.r_name)))
FROM supplier s
LEFT JOIN nation n ON n.n_nationkey = s.s_nationkey
LEFT JOIN region r ON r.r_regionkey = n.n_regionkey
ORDER BY s.s_suppkey;

SELECT JSON_OBJECT('tipo', 'regiao', 'dados',
    JSON_OBJECT('_id', r_regionkey, 'nome', TRIM(r_name)))
FROM region ORDER BY r_regionkey;

SELECT JSON_OBJECT('tipo', 'pais', 'dados', JSON_OBJECT(
    '_id', n.n_nationkey, 'nome', TRIM(n.n_name),
    'regiao', JSON_OBJECT('id', r.r_regionkey, 'nome', TRIM(r.r_name))))
FROM nation n LEFT JOIN region r ON r.r_regionkey = n.n_regionkey
ORDER BY n.n_nationkey;

-- Indicadores calculados de forma independente na origem relacional.
SELECT JSON_OBJECT('tipo', 'indicador_regiao', 'dados', JSON_OBJECT(
    'regiao_id', r.r_regionkey, 'regiao', TRIM(r.r_name),
    'fornecedores', COUNT(s.s_suppkey),
    'participacao_pct', ROUND(100.0 * COUNT(s.s_suppkey) /
        NULLIF((SELECT COUNT(*) FROM supplier), 0), 4)))
FROM region r
LEFT JOIN nation n ON n.n_regionkey = r.r_regionkey
LEFT JOIN supplier s ON s.s_nationkey = n.n_nationkey
GROUP BY r.r_regionkey, r.r_name ORDER BY r.r_regionkey;

SELECT JSON_OBJECT('tipo', 'indicador_pais', 'dados', JSON_OBJECT(
    'pais_id', n.n_nationkey, 'pais', TRIM(n.n_name), 'regiao', TRIM(r.r_name),
    'fornecedores', COUNT(s.s_suppkey),
    'participacao_pct', ROUND(100.0 * COUNT(s.s_suppkey) /
        NULLIF((SELECT COUNT(*) FROM supplier), 0), 4)))
FROM nation n JOIN region r ON r.r_regionkey = n.n_regionkey
LEFT JOIN supplier s ON s.s_nationkey = n.n_nationkey
GROUP BY n.n_nationkey, n.n_name, r.r_name ORDER BY n.n_nationkey;

SELECT JSON_OBJECT('tipo', 'controle', 'dados', JSON_OBJECT(
    'schema', DATABASE(), 'versao_mysql', VERSION(),
    'extraido_em_utc', UTC_TIMESTAMP(3),
    'fornecedores', (SELECT COUNT(*) FROM supplier),
    'paises', (SELECT COUNT(*) FROM nation), 'regioes', (SELECT COUNT(*) FROM region),
    'fornecedores_sem_pais', (SELECT COUNT(*) FROM supplier s LEFT JOIN nation n
        ON n.n_nationkey = s.s_nationkey WHERE n.n_nationkey IS NULL),
    'paises_sem_regiao', (SELECT COUNT(*) FROM nation n LEFT JOIN region r
        ON r.r_regionkey = n.n_regionkey WHERE r.r_regionkey IS NULL)));
ROLLBACK;
