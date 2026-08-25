SELECT damesano, premio_ganho, sinistro_ocorrido
FROM bronze.susep_seguros s
JOIN bronze.susep_cias c ON s.coenti = c."Coenti"
JOIN bronze.susep_ramos r ON s.coramo::bigint = r.coramo
WHERE c."Noenti" = 'AIG SEGUROS BRASIL S.A.'
  AND r.noramo = '0993 - Vida em Grupo'
  AND s.damesano BETWEEN 202301 AND 202312
ORDER BY damesano;
