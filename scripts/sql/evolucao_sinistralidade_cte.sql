-- CTE: calcula sinistralidade anual por seguradora (2020-2023)
-- reaproveitando o mesmo tratamento de virgula->ponto e filtro de materialidade
-- validados na sessao anterior (Sprint 4)

WITH sinistralidade_anual AS (
    SELECT
        c."Noenti" AS seguradora,
        (s.damesano / 100) AS ano,
        SUM(REPLACE(s.sinistro_ocorrido, ',', '.')::numeric) AS total_sinistros,
        SUM(REPLACE(s.premio_ganho, ',', '.')::numeric) AS total_premios
    FROM bronze.susep_seguros s
    JOIN bronze.susep_cias c ON s.coenti = c."Coenti"
    WHERE s.damesano BETWEEN 202001 AND 202312
    GROUP BY c."Noenti", (s.damesano / 100)
    HAVING SUM(REPLACE(s.premio_ganho, ',', '.')::numeric) > 5000000
)
SELECT
    seguradora,
    ano,
    ROUND(total_premios, 2) AS total_premios,
    ROUND(total_sinistros, 2) AS total_sinistros,
    ROUND((total_sinistros / NULLIF(total_premios, 0) * 100), 2) AS sinistralidade_pct
FROM sinistralidade_anual
ORDER BY seguradora, ano
LIMIT 20;
