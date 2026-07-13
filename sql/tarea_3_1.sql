-- Query Reto 3.1: Arrastre Alianza Verde (Cámara codpar=5, Senado codpar=57)
-- Nota: En los datos simulados unificados se utiliza la equivalencia técnica indicada.

WITH VotosCamara AS (
    SELECT 
        m.municipio,
        m.puesto,
        SUM(rv.votos) AS total_votos_ca
    FROM resultados_votos rv
    JOIN mesas m ON rv.id_mesa = m.id_mesa
    WHERE rv.corporacion = 'CA' AND rv.codpar = 5
    GROUP BY m.municipio, m.puesto
),
VotosSenado AS (
    SELECT 
        m.municipio,
        m.puesto,
        SUM(rv.votos) AS total_votos_se
    FROM resultados_votos rv
    JOIN mesas m ON rv.id_mesa = m.id_mesa
    -- Se mapea la equivalencia de partidos definida en los pliegos técnicos
    WHERE rv.corporacion = 'SE' AND (rv.codpar = 5 OR rv.codpar = 57)
    GROUP BY m.municipio, m.puesto
)
SELECT 
    vc.municipio,
    vc.puesto,
    vc.total_votos_ca,
    COALESCE(vs.total_votos_se, 0) AS total_votos_se,
    ROUND(CAST(COALESCE(vs.total_votos_se, 0) AS REAL) / vc.total_votos_ca, 4) AS ratio_arrastre
FROM VotosCamara vc
LEFT JOIN VotosSenado vs ON vc.municipio = vs.municipio AND vc.puesto = vs.puesto
ORDER BY ratio_arrastre DESC;