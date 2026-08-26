-- Window Function: ranking de sinistralidade por seguradora, dentro de cada ano
-- PARTITION BY ano garante que o ranking reinicia a cada ano (nao eh um rank global)
-- Reaproveita a mesma CTE de sinistralidade anual validada anteriormente (Sprint 4)

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
),
sinistralidade_calculada AS (
    SELECT
        seguradora,
        ano,
        ROUND(total_premios, 2) AS total_premios,
        ROUND(total_sinistros, 2) AS total_sinistros,
        ROUND((total_sinistros / NULLIF(total_premios, 0) * 100), 2) AS sinistralidade_pct
    FROM sinistralidade_anual
)
SELECT
    seguradora,
    ano,
    total_premios,
    sinistralidade_pct,
    RANK() OVER (PARTITION BY ano ORDER BY sinistralidade_pct DESC) AS ranking_no_ano
FROM sinistralidade_calculada
WHERE ano = 2023
ORDER BY ranking_no_ano
LIMIT 15;
