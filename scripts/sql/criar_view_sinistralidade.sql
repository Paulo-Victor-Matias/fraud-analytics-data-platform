-- View: sinistralidade anual por seguradora, reutilizavel
-- Encapsula o tratamento de virgula->ponto e o filtro de materialidade (>5M em premio)
-- validados durante a pratica de JOIN/CTE/Window Function da Sprint 4.
-- Uso: SELECT * FROM bronze.vw_sinistralidade_anual WHERE ano = 2023 ORDER BY sinistralidade_pct DESC;

CREATE OR REPLACE VIEW bronze.vw_sinistralidade_anual AS
WITH sinistralidade_anual AS (
    SELECT
        c."Noenti" AS seguradora,
        (s.damesano / 100) AS ano,
        SUM(REPLACE(s.sinistro_ocorrido, ',', '.')::numeric) AS total_sinistros,
        SUM(REPLACE(s.premio_ganho, ',', '.')::numeric) AS total_premios
    FROM bronze.susep_seguros s
    JOIN bronze.susep_cias c ON s.coenti = c."Coenti"
    GROUP BY c."Noenti", (s.damesano / 100)
    HAVING SUM(REPLACE(s.premio_ganho, ',', '.')::numeric) > 5000000
)
SELECT
    seguradora,
    ano,
    ROUND(total_premios, 2) AS total_premios,
    ROUND(total_sinistros, 2) AS total_sinistros,
    ROUND((total_sinistros / NULLIF(total_premios, 0) * 100), 2) AS sinistralidade_pct
FROM sinistralidade_anual;
