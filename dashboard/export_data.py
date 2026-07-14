import os
import sqlite3
import json

# Rutas absolutas para evitar problemas con el directorio desde donde ejecutas el comando
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "../db/puestos_2026.db"))
JSON_OUTPUT = os.path.abspath(os.path.join(BASE_DIR, "data.json"))

MAPEO_MUNICIPIOS = {
    "0700001": "TUNJA",
    "0700181": "PAIPA",
    "0700277": "SOGAMOSO",
    "0700079": "DUITAMA"
}

MAPEO_PARTIDOS = {
    2: "PARTIDO LIBERAL",
    10: "PARTIDO LIBERAL",       # Senado
    5: "ALIANZA VERDE",
    57: "ALIANZA VERDE",         # Senado
    87: "PACTO HISTÓRICO",
    92: "PACTO HISTÓRICO",       # Senado
    121: "CENTRO DEMOCRÁTICO",
    109: "CENTRO DEMOCRÁTICO",    # Senado
    122: "PARTIDO CONSERVADOR",
    17: "PARTIDO CONSERVADOR"    # Senado
}

def obtener_nombre_partido(codpar, nombre_bd):
    try:
        cod = int(codpar)
        if cod in MAPEO_PARTIDOS:
            return MAPEO_PARTIDOS[cod]
    except (ValueError, TypeError):
        pass
    return str(nombre_bd).upper() if nombre_bd else "DESCONOCIDO"

def exportar_a_json():
    print(f"[INFO] Buscando base de datos en: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] No se encontró la base de datos en {DB_PATH}. Verifique la ruta.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print("[SUCCESS] Conexión exitosa a la base de datos.")

        # 1. Obtener totales consolidados globales de Cámara
        cursor.execute("""
            SELECT m.municipio, SUM(rv.votos)
            FROM resultados_votos rv
            JOIN mesas m ON rv.id_mesa = m.id_mesa
            WHERE rv.corporacion = 'CA'
            GROUP BY m.municipio
        """)
        comparativo = {}
        for row in cursor.fetchall():
            mun_raw = str(row[0]).upper()
            mun_real = MAPEO_MUNICIPIOS.get(mun_raw, mun_raw)
            comparativo[mun_real] = comparativo.get(mun_real, 0) + row[1]

        municipios_clave = ["TUNJA", "PAIPA", "SOGAMOSO", "DUITAMA"]
        comparativo_filtrado = {k: v for k, v in comparativo.items() if k in municipios_clave}

        por_municipio = {}

        for mun_id, mun_nombre in MAPEO_MUNICIPIOS.items():
            # --- TOTAL REAL DE VOTOS GLOBALES EN CÁMARA ---
            cursor.execute("""
                SELECT SUM(rv.votos)
                FROM resultados_votos rv
                JOIN mesas m ON rv.id_mesa = m.id_mesa
                WHERE (UPPER(m.municipio) = ? OR UPPER(m.municipio) = ?) AND rv.corporacion = 'CA'
            """, (mun_nombre, mun_id))
            row_total_ca = cursor.fetchone()
            total_global_ca = row_total_ca[0] if row_total_ca and row_total_ca[0] is not None else 0

            # --- TOTAL REAL DE VOTOS GLOBALES EN SENADO ---
            cursor.execute("""
                SELECT SUM(rv.votos)
                FROM resultados_votos rv
                JOIN mesas m ON rv.id_mesa = m.id_mesa
                WHERE (UPPER(m.municipio) = ? OR UPPER(m.municipio) = ?) AND rv.corporacion = 'SE'
            """, (mun_nombre, mun_id))
            row_total_se = cursor.fetchone()
            total_global_se = row_total_se[0] if row_total_se and row_total_se[0] is not None else 0

            # --- TOP 10 CÁMARA ---
            cursor.execute("""
                SELECT rv.candidato_nombre, p.nombre_partido, SUM(rv.votos), rv.corporacion, p.codpar
                FROM resultados_votos rv
                JOIN mesas m ON rv.id_mesa = m.id_mesa
                JOIN partidos p ON rv.codpar = p.codpar
                WHERE (UPPER(m.municipio) = ? OR UPPER(m.municipio) = ?) AND rv.corporacion = 'CA'
                GROUP BY rv.candidato_nombre, p.nombre_partido, rv.corporacion, p.codpar
                ORDER BY SUM(rv.votos) DESC
                LIMIT 10
            """, (mun_nombre, mun_id))
            
            top_camara = []
            for r in cursor.fetchall():
                top_camara.append({
                    "candidato": r[0],
                    "partido": obtener_nombre_partido(r[4], r[1]),
                    "votos": r[2],
                    "corporacion": "CÁMARA"
                })

            # --- TOP 10 SENADO ---
            cursor.execute("""
                SELECT rv.candidato_nombre, p.nombre_partido, SUM(rv.votos), rv.corporacion, p.codpar
                FROM resultados_votos rv
                JOIN mesas m ON rv.id_mesa = m.id_mesa
                JOIN partidos p ON rv.codpar = p.codpar
                WHERE (UPPER(m.municipio) = ? OR UPPER(m.municipio) = ?) AND rv.corporacion = 'SE'
                GROUP BY rv.candidato_nombre, p.nombre_partido, rv.corporacion, p.codpar
                ORDER BY SUM(rv.votos) DESC
                LIMIT 10
            """, (mun_nombre, mun_id))
            
            top_senado = []
            for r in cursor.fetchall():
                top_senado.append({
                    "candidato": r[0],
                    "partido": obtener_nombre_partido(r[4], r[1]),
                    "votos": r[2],
                    "corporacion": "SENADO"
                })

            # Partido líder en Senado
            cursor.execute("""
                SELECT p.nombre_partido, SUM(rv.votos), p.codpar
                FROM resultados_votos rv
                JOIN mesas m ON rv.id_mesa = m.id_mesa
                JOIN partidos p ON rv.codpar = p.codpar
                WHERE (UPPER(m.municipio) = ? OR UPPER(m.municipio) = ?) AND rv.corporacion = 'SE'
                GROUP BY p.nombre_partido, p.codpar
                ORDER BY SUM(rv.votos) DESC
                LIMIT 1
            """, (mun_nombre, mun_id))
            lider_row = cursor.fetchone()
            lider_se = obtener_nombre_partido(lider_row[2], lider_row[0]) if lider_row else "PACTO HISTÓRICO"

            # Ratio de arrastre Verde por puesto
            cursor.execute("""
                SELECT m.puesto,
                       CAST(SUM(CASE WHEN rv.corporacion = 'SE' AND rv.codpar = 57 THEN rv.votos ELSE 0 END) AS REAL) /
                       NULLIF(SUM(CASE WHEN rv.corporacion = 'CA' AND rv.codpar = 5 THEN rv.votos ELSE 0 END), 0)
                FROM resultados_votos rv
                JOIN mesas m ON rv.id_mesa = m.id_mesa
                WHERE (UPPER(m.municipio) = ? OR UPPER(m.municipio) = ?) AND rv.codpar IN (5, 57)
                GROUP BY m.puesto
            """, (mun_nombre, mun_id))
            ratios_puestos = [{"puesto": r[0], "ratio": round(r[1], 2) if r[1] is not None else 0.0}
                               for r in cursor.fetchall()]

            por_municipio[mun_nombre] = {
                "top_camara": top_camara,
                "top_senado": top_senado,
                "total_votos_global_ca": total_global_ca,
                "total_votos_global_se": total_global_se,
                "partido_lider_senado": lider_se,
                "arrastre_verde": ratios_puestos,
            }

        data_final = {
            "comparativo_ca": comparativo_filtrado,
            "municipios": por_municipio,
        }

        with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
            json.dump(data_final, f, indent=4, ensure_ascii=False)

        print(f"[SUCCESS] Archivo JSON generado exitosamente en: {JSON_OUTPUT}")
        conn.close()

    except Exception as e:
        print(f"[ERROR CRÍTICO] Ocurrió un error procesando los datos: {e}")

if __name__ == "__main__":
    exportar_a_json()