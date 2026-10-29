SELECT n.n_nationkey AS pais_id, n.n_name AS pais,
       r.r_name AS regiao, COUNT(s.s_suppkey) AS fornecedores,
       ROUND(100.0 * COUNT(s.s_suppkey) / NULLIF((SELECT COUNT(*) FROM supplier), 0), 4) AS participacao_pct
FROM nation n
JOIN region r ON r.r_regionkey = n.n_regionkey
LEFT JOIN supplier s ON s.s_nationkey = n.n_nationkey
GROUP BY n.n_nationkey, n.n_name, r.r_name
ORDER BY fornecedores DESC, pais_id
