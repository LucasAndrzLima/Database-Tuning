-- Executar no MySQL Workbench, conexão localhost:3308, root, senha do laboratório.
USE tpch;

SELECT r.r_name AS regiao, COUNT(s.s_suppkey) AS fornecedores,
       ROUND(100.0 * COUNT(s.s_suppkey) / NULLIF((SELECT COUNT(*) FROM supplier), 0), 4) AS participacao_pct
FROM region r
LEFT JOIN nation n ON n.n_regionkey = r.r_regionkey
LEFT JOIN supplier s ON s.s_nationkey = n.n_nationkey
GROUP BY r.r_regionkey, r.r_name
ORDER BY fornecedores DESC, r.r_regionkey;

SELECT n.n_name AS pais, r.r_name AS regiao, COUNT(s.s_suppkey) AS fornecedores
FROM nation n
JOIN region r ON r.r_regionkey = n.n_regionkey
LEFT JOIN supplier s ON s.s_nationkey = n.n_nationkey
GROUP BY n.n_nationkey, n.n_name, r.r_regionkey, r.r_name
ORDER BY fornecedores DESC, n.n_nationkey;
