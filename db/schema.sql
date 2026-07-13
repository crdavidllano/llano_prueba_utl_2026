-- Habilitar el soporte de llaves foráneas en SQLite
PRAGMA foreign_keys = ON;

-- 1. Tabla de Partidos Políticos
CREATE TABLE IF NOT EXISTS partidos (
    codpar INTEGER PRIMARY KEY,
    nombre_partido TEXT NOT NULL,
    color_hex TEXT
);

-- 2. Tabla de Mesas de Votación / Ubicación
CREATE TABLE IF NOT EXISTS mesas (
    id_mesa TEXT PRIMARY KEY, -- Combinación única: depto + mun + zona + puesto + mesa
    departamento TEXT NOT NULL,
    municipio TEXT NOT NULL,
    zona TEXT NOT NULL,
    puesto TEXT NOT NULL,
    mesa TEXT NOT NULL,
    UNIQUE(departamento, municipio, zona, puesto, mesa)
);

-- 3. Tabla de Resultados Electorales (Cámara y Senado)
CREATE TABLE IF NOT EXISTS resultados_votos (
    id_resultado INTEGER PRIMARY KEY AUTOINCREMENT,
    id_mesa TEXT NOT NULL,
    corporacion TEXT CHECK(corporacion IN ('CA', 'SE')), -- CA = Cámara, SE = Senado
    codpar INTEGER NOT NULL,
    candidato_nombre TEXT NOT NULL,
    votos INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (id_mesa) REFERENCES mesas(id_mesa) ON DELETE CASCADE,
    FOREIGN KEY (codpar) REFERENCES partidos(codpar) ON DELETE CASCADE,
    UNIQUE(id_mesa, corporacion, codpar, candidato_nombre)
);

-- 4. Tabla de Auditoría y Control de Cargas (Exigido en Reto 2.1)
CREATE TABLE IF NOT EXISTS carga_log (
    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    municipio TEXT NOT NULL,
    filas_insertadas INTEGER NOT NULL,
    filas_omitidas INTEGER NOT NULL
);

-- ==========================================
-- BONUS: 3+ ÍNDICES SQLITE JUSTIFICADOS
-- ==========================================

-- Índice 1: Optimiza consultas analíticas agregadas por Corporación y Partido (Reto 3.1, 3.3)
CREATE INDEX IF NOT EXISTS idx_resultados_corp_partido 
ON resultados_votos(corporacion, codpar);

-- Índice 2: Optimiza el cálculo de Dominancia Extrema filtrando rápidamente por Mesa y Partido (Reto 3.2)
CREATE INDEX IF NOT EXISTS idx_resultados_mesa_partido 
ON resultados_votos(id_mesa, codpar);

-- Índice 3: Agiliza los filtros geográficos de municipio dentro del Dashboard y ETL
CREATE INDEX IF NOT EXISTS idx_mesas_municipio 
ON mesas(municipio);