-- Mesmo universo do dashboard: TODOS os fornecedores, incluindo regiões vazias.
SELECT r.r_regionkey AS regiao_id, r.r_name AS regiao,
       COUNT(s.s_suppkey) AS fornecedores,
       ROUND(100.0 * COUNT(s.s_suppkey) / NULLIF((SELECT COUNT(*) FROM supplier), 0), 4) AS participacao_pct
FROM region r
LEFT JOIN nation n ON n.n_regionkey = r.r_regionkey
LEFT JOIN supplier s ON s.s_nationkey = n.n_nationkey
GROUP BY r.r_regionkey, r.r_name
ORDER BY fornecedores DESC, regiao_id
