SELECT 'fornecedores_sem_pais' AS verificacao, COUNT(*) AS inconsistencias
FROM supplier s LEFT JOIN nation n ON n.n_nationkey=s.s_nationkey
WHERE n.n_nationkey IS NULL
UNION ALL
SELECT 'paises_sem_regiao', COUNT(*)
FROM nation n LEFT JOIN region r ON r.r_regionkey=n.n_regionkey
WHERE r.r_regionkey IS NULL
UNION ALL
SELECT 'fornecedores_nome_vazio', COUNT(*) FROM supplier WHERE TRIM(s_name)=''
