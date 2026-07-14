"""
ETL - Prueba Analista de Datos UTL Boyacá 2026
Carga la información desde temp_extracted/ o sample_data/ e inserta en SQLite.
"""

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "puestos_2026.db"
TEMP_PATH = ROOT / "temp_extracted"
SAMPLE_PATH = ROOT / "sample_data"
SCHEMA_PATH = ROOT / "db" / "schema.sql"

def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def crear_bd(conn):
    with open(SCHEMA_PATH, encoding="utf8") as f:
        conn.executescript(f.read())
    conn.commit()

def obtener_jsons():
    archivos = sorted(TEMP_PATH.glob("*.json"))
    if archivos:
        print(f"\nSe encontraron {len(archivos)} archivos en temp_extracted")
        return archivos
    archivos = sorted(SAMPLE_PATH.glob("*.json"))
    print(f"\nUsando {len(archivos)} archivos desde sample_data")
    return archivos

def cargar_json(path):
    with open(path, encoding="utf8") as f:
        return json.load(f)

def extraer_resultados(datos):
    resultados = []
    # Si viene estructura anidada en 'camaras', iterar; de lo contrario procesar raíz
    camaras = datos.get("camaras", [])
    if not camaras and "partotabla" in datos:
        camaras = [datos]

    for camara in camaras:
        # Resolver corporación bajo el CHECK constraint ('CA', 'SE')
        corporacion = "SE"
        if str(camara.get("cam", "0")) != "0" or "CA" in str(datos.get("amb", "")):
            corporacion = "CA"

        for partido in camara.get("partotabla", []):
            info = partido.get("act", {})
            if not info:
                continue
            codpar = int(info["codpar"])
            nombre_partido = info.get("nompar", f"PARTIDO {codpar}").upper()

            for candidato in info.get("cantotabla", []):
                nombre = " ".join(
                    filter(
                        None,
                        [
                            candidato.get("nomcan"),
                            candidato.get("apecan"),
                            candidato.get("nomcan2"),
                            candidato.get("apecan2")
                        ]
                    )
                ).strip().upper()

                resultados.append(
                    {
                        "codpar": codpar,
                        "partido": nombre_partido,
                        "corporacion": corporacion,
                        "candidato": nombre if nombre else "VOTOS EN BLANCO / NO MARCADOS",
                        "votos": int(candidato.get("vot", 0))
                    }
                )
    return resultados

def main():
    conn = conectar()
    crear_bd(conn)
    cursor = conn.cursor()

    archivos = obtener_jsons()
    total_insertadas = 0
    total_omitidas = 0

    for archivo in archivos:
        print(f"\nProcesando {archivo.name}")
        datos = cargar_json(archivo)

        # Identificar Metadatos del archivo de votación
        municipio_raw = datos.get("amb", archivo.stem.split("_")[0]).upper()
        departamento = datos.get("numdep", "BOYACA").upper()

        corporacion_actual = "SE"
        if "_CA" in archivo.stem or "CA" in datos.get("amb", ""):
            corporacion_actual = "CA"

        # Simular y estructurar una relación de mesa e id_mesa consistente
        id_mesa_simulada = f"MESA_{municipio_raw}_{corporacion_actual}"
        cursor.execute(
            """
            INSERT OR IGNORE INTO mesas (id_mesa, municipio, puesto, mesa)
            VALUES (?, ?, ?, ?)
            """,
            (id_mesa_simulada, municipio_raw, f"PUESTO_{municipio_raw}", 1)
        )

        resultados = extraer_resultados(datos)
        filas_insertadas = 0
        filas_omitidas = 0

        for r in resultados:
            # Registrar o actualizar Catálogo de Partidos
            cursor.execute(
                """
                INSERT OR IGNORE INTO partidos (codpar, nombre_partido)
                VALUES (?, ?)
                """,
                (r["codpar"], r["partido"])
            )

            # Insertar resultados de votación con relación de clave foránea a la mesa
            try:
                cursor.execute(
                    """
                    INSERT INTO resultados_votos (id_mesa, corporacion, codpar, candidato_nombre, votos)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        id_mesa_simulada,
                        r["corporacion"],
                        r["codpar"],
                        r["candidato"],
                        r["votos"]
                    )
                )
                filas_insertadas += 1
            except Exception as e:
                filas_omitidas += 1

        # Cargar resumen consolidado si el objeto del JSON lo permite
        if "totales" in datos:
            try:
                cargar_resumen(cursor, datos, departamento)
            except Exception as e:
                print(f"  ⚠ Resumen omitido o incompleto: {e}")

        # Registrar log de auditoría interna de carga
        cursor.execute(
            """
            INSERT INTO carga_log (municipio, filas_insertadas, filas_omitidas)
            VALUES (?, ?, ?)
            """,
            (municipio_raw, filas_insertadas, filas_omitidas)
        )

        conn.commit()
        total_insertadas += filas_insertadas
        total_omitidas += filas_omitidas
        print(f"  ✔ {filas_insertadas} registros insertados")

    conn.close()
    print("\n==============================")
    print("ETL FINALIZADO CON ÉXITO")
    print("==============================")
    print(f"Insertados : {total_insertadas}")
    print(f"Omitidos   : {total_omitidas}")

def cargar_resumen(cursor, datos, departamento):
    municipio = datos["amb"].upper()
    totales = datos["totales"]["act"]

    potencial = int(totales["centota"])
    votantes = int(totales["votant"])
    abstenciones = int(totales["absten"])
    blancos = int(totales["votblan"])
    nulos = int(totales["votnul"])
    validos = int(totales["votval"])

    cursor.execute(
        """
        INSERT OR REPLACE INTO resumen_municipio (municipio, departamento, potencial_electoral, votantes, abstenciones, votos_validos, votos_blanco, votos_nulos)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            municipio,
            departamento,
            potencial,
            votantes,
            abstenciones,
            validos,
            blancos,
            nulos
        )
    )

if __name__ == "__main__":
    main()