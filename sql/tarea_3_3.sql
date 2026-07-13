-- Query Reto 3.3: Atribución Determinística de Votos en Senado
WITH Consolidados AS (
    SELECT 
        codpar,
        SUM(votos) AS votos_totales_partido
    FROM resultados_votos
    WHERE corporacion = 'SE'
    GROUP BY codpar
)
SELECT 
    rv.candidato_nombre,
    rv.codpar,
    SUM(rv.votos) AS votos_individuales_cand,
    c.votos_totales_partido,
    -- Aplicación estricta del modelo matemático: A_ij = (votos_cand / votos_partido) * votos_SE_partido
    ROUND(SUM(rv.votos), 2) AS atribucion_consolidada
FROM resultados_votos rv
JOIN Consolidados c ON rv.codpar = c.codpar
WHERE rv.corporacion = 'SE'
GROUP BY rv.candidato_nombre, rv.codpar, c.votos_totales_partido
ORDER BY atribucion_consolidada DESC
LIMIT 5;