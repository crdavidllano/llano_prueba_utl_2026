import os
import sqlite3
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "../db/puestos_2026.db")
JSON_OUTPUT = os.path.join(os.path.dirname(__file__), "data.json")

def exportar_a_json():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Obtener totales consolidados de Cámara para Gráfico Comparativo Inicial
    cursor.execute("""
        SELECT m.municipio, SUM(rv.votos) 
        FROM resultados_votos rv 
        JOIN mesas m ON rv.id_mesa = m.id_mesa
        WHERE rv.corporacion = 'CA'
        GROUP BY m.municipio
    """)
    comparativo = {row[0]: row[1] for row in cursor.fetchall()}
    
    # 2. Datos por municipio (Top Candidatos y Partido Líder)
    municipios = ["TUNJA", "PAIPA", "SOGAMOSO", "DUITAMA"]
    por_municipio = {}
    
    for mun in municipios:
        # Top 10 candidatos Cámara
        cursor.execute("""
            SELECT rv.candidato_nombre, p.nombre_partido, SUM(rv.votos)
            FROM resultados_votos rv
            JOIN mesas m ON rv.id_mesa = m.id_mesa
            JOIN partidos p ON rv.codpar = p.codpar
            WHERE m.municipio = ? AND rv.corporacion = 'CA'
            GROUP BY rv.candidato_nombre, p.nombre_partido
            ORDER BY SUM(rv.votos) DESC
            LIMIT 10
        """, (mun,))
        top_cand = [{"candidato": r[0], "partido": r[1], "votos": r[2]} for r in cursor.fetchall()]
        
        # Partido Líder en Senado
        cursor.execute("""
            SELECT p.nombre_partido, SUM(rv.votos)
            FROM resultados_votos rv
            JOIN mesas m ON rv.id_mesa = m.id_mesa
            JOIN partidos p ON rv.codpar = p.codpar
            WHERE m.municipio = ? AND rv.corporacion = 'SE'
            GROUP BY p.nombre_partido
            ORDER BY SUM(rv.votos) DESC
            LIMIT 1
        """, (mun,))
        lider_row = cursor.fetchone()
        lider_se = lider_row[0] if lider_row else "N/A"
        
        # Ratios de Arrastre Verde por Puesto
        cursor.execute("""
            SELECT m.puesto, 
                   CAST(SUM(CASE WHEN rv.corporacion='SE' THEN rv.votos ELSE 0 END) AS REAL) / 
                   NULLIF(SUM(CASE WHEN rv.corporacion='CA' THEN rv.votos ELSE 0 END), 0)
            FROM resultados_votos rv
            JOIN mesas m ON rv.id_mesa = m.id_mesa
            WHERE m.municipio = ? AND rv.codpar = 5
            GROUP BY m.puesto
        """, (mun,))
        ratios_puestos = [{"puesto": r[0], "ratio": round(r[1], 2) if r[1] else 0.0} for r in cursor.fetchall()]
        
        por_municipio[mun] = {
            "top_candidatos": top_cand,
            "partido_lider_senado": lider_se,
            "arrastre_verde": ratios_puestos
        }
        
    data_final = {
        "comparativo_ca": comparativo,
        "municipios": por_municipio
    }
    
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data_final, f, indent=4, ensure_ascii=False)
        
    print(f"[SUCCESS] Datos consolidados y exportados a {JSON_OUTPUT}")
    conn.close()

if __name__ == "__main__":
    exportar_a_json()