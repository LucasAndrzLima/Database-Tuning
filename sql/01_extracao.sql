SELECT s.s_suppkey AS fornecedor_id, s.s_name AS fornecedor,
       s.s_nationkey AS pais_id, n.n_name AS pais,
       n.n_regionkey AS regiao_id, r.r_name AS regiao
FROM supplier s
LEFT JOIN nation n ON n.n_nationkey = s.s_nationkey
LEFT JOIN region r ON r.r_regionkey = n.n_regionkey
ORDER BY s.s_suppkey
