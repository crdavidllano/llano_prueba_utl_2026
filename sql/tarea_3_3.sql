-- Query Reto 3.3: Atribución Determinística de Votos en Senado
-- Formula: A_ij = (votos_cand / votos_partido) x votos_SE_partido
-- (con corporacion='SE', votos_SE_partido = votos_partido, así que A_ij = votos_cand;
--  lo importante es dejar el ratio calculado explícitamente, no solo la suma)

WITH VotosPorCandidato AS (
    SELECT
        codpar,
        candidato_nombre,
        SUM(votos) AS votos_cand
    FROM resultados_votos
    WHERE corporacion = 'SE'
    GROUP BY codpar, candidato_nombre
),
VotosPorPartido AS (
    SELECT
        codpar,
        SUM(votos) AS votos_se_partido
    FROM resultados_votos
    WHERE corporacion = 'SE'
    GROUP BY codpar
)
SELECT
    vc.candidato_nombre,
    vc.codpar,
    vc.votos_cand,
    vp.votos_se_partido,
    ROUND(CAST(vc.votos_cand AS REAL) / vp.votos_se_partido, 4) AS ratio_candidato,
    ROUND((CAST(vc.votos_cand AS REAL) / vp.votos_se_partido) * vp.votos_se_partido, 2) AS atribucion_consolidada
FROM VotosPorCandidato vc
JOIN VotosPorPartido vp ON vc.codpar = vp.codpar
ORDER BY atribucion_consolidada DESC
LIMIT 5;