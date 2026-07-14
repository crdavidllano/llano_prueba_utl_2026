PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS resultados_votos;
DROP TABLE IF EXISTS mesas;
DROP TABLE IF EXISTS partidos;
DROP TABLE IF EXISTS resumen_municipio;
DROP TABLE IF EXISTS carga_log;

PRAGMA foreign_keys = ON;

CREATE TABLE partidos (
    codpar INTEGER PRIMARY KEY,
    nombre_partido TEXT NOT NULL
);

CREATE TABLE mesas (
    id_mesa TEXT PRIMARY KEY,
    municipio TEXT NOT NULL,
    puesto TEXT NOT NULL,
    mesa INTEGER NOT NULL
);

CREATE TABLE resultados_votos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_mesa TEXT NOT NULL,
    corporacion TEXT CHECK(corporacion IN ('CA', 'SE')),
    codpar INTEGER NOT NULL,
    candidato_nombre TEXT NOT NULL,
    votos INTEGER NOT NULL,
    FOREIGN KEY (id_mesa) REFERENCES mesas(id_mesa),
    FOREIGN KEY (codpar) REFERENCES partidos(codpar)
);

CREATE TABLE resumen_municipio (
    municipio TEXT PRIMARY KEY,
    departamento TEXT,
    potencial_electoral INTEGER,
    votantes INTEGER,
    abstenciones INTEGER,
    votos_validos INTEGER,
    votos_blanco INTEGER,
    votos_nulos INTEGER
);

CREATE TABLE carga_log (
    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    municipio TEXT NOT NULL,
    filas_insertadas INTEGER NOT NULL,
    filas_omitidas INTEGER NOT NULL
);

-- Índices de Optimización
CREATE INDEX IF NOT EXISTS idx_mesas_municipio ON mesas(municipio);
CREATE INDEX IF NOT EXISTS idx_resultados_mesa_partido ON resultados_votos(id_mesa, codpar);
CREATE INDEX IF NOT EXISTS idx_resultados_corp_partido ON resultados_votos(corporacion, codpar);