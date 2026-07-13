-- Query Reto 3.2: Mesas con Dominancia Extrema (>60% de los votos del partido)
WITH TotalVotosPartidoMesa AS (
    SELECT 
        id_mesa,
        corporacion,
        codpar,
        SUM(votos) AS votos_totales_partido
    FROM resultados_votos
    GROUP BY id_mesa, corporacion, codpar
)
SELECT 
    m.municipio,
    rv.id_mesa,
    rv.corporacion,
    rv.codpar,
    rv.candidato_nombre,
    rv.votos AS votos_candidato,
    t.votos_totales_partido,
    ROUND(CAST(rv.votos AS REAL) / t.votos_totales_partido, 4) AS porcentaje_concentracion
FROM resultados_votos rv
JOIN TotalVotosPartidoMesa t ON rv.id_mesa = t.id_mesa 
                            AND rv.corporacion = t.corporacion 
                            AND rv.codpar = t.codpar
JOIN mesas m ON rv.id_mesa = m.id_mesa
WHERE t.votos_totales_partido > 0 
  AND (CAST(rv.votos AS REAL) / t.votos_totales_partido) > 0.60
ORDER BY porcentaje_concentracion DESC;