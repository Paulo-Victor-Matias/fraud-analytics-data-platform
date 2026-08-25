-- Sinistralidade por seguradora e ramo (SUSEP, ano 2023)
-- Filtro HAVING > 1.000.000 no premio_ganho: exclui combinações seguradora/ramo
-- com base de premio muito pequena, que geram sinistralidade % irreal
-- (ex: AIG Vida em Grupo teve sinistralidade de 1.425% pois o premio anual
-- somado ficou perto de zero, distorcendo a divisao). Achado documentado
-- em 23/08/2026 durante pratica de JOIN + GROUP BY da Sprint 4.

SELECT
    c."Noenti" AS seguradora,
    r.noramo AS ramo,
    ROUND(SUM(REPLACE(s.sinistro_ocorrido, ',', '.')::numeric), 2) AS total_sinistros,
    ROUND(SUM(REPLACE(s.premio_ganho, ',', '.')::numeric), 2) AS total_premios,
    ROUND(
        (SUM(REPLACE(s.sinistro_ocorrido, ',', '.')::numeric)
         / NULLIF(SUM(REPLACE(s.premio_ganho, ',', '.')::numeric), 0) * 100), 2
    ) AS sinistralidade_pct
FROM bronze.susep_seguros s
JOIN bronze.susep_cias c ON s.coenti = c."Coenti"
JOIN bronze.susep_ramos r ON s.coramo::bigint = r.coramo
WHERE s.damesano BETWEEN 202301 AND 202312
GROUP BY c."Noenti", r.noramo
HAVING SUM(REPLACE(s.premio_ganho, ',', '.')::numeric) > 1000000
ORDER BY sinistralidade_pct DESC
LIMIT 15;
