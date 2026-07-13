import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DB_PATH = os.path.join(os.path.dirname(__file__), "../db/puestos_2026.db")
OUTPUT_IMG = os.path.join(os.path.dirname(__file__), "heatmap_municipios.png")

def generar_heatmap():
    conn = sqlite3.connect(DB_PATH)
    
    # Query para extraer pesos porcentuales relativos de candidatos
    query = """
        SELECT m.municipio, rv.candidato_nombre, SUM(rv.votos) as votos
        FROM resultados_votos rv
        JOIN mesas m ON rv.id_mesa = m.id_mesa
        WHERE rv.corporacion = 'CA'
        GROUP BY m.municipio, rv.candidato_nombre
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("[WARN] Base de datos vacía. No se genera mapa de calor.")
        return

    # Pivotar matriz y filtrar top 8 candidatos mundiales
    pivot_df = df.pivot(index='candidato_nombre', columns='municipio', values='votos').fillna(0)
    top_8 = pivot_df.sum(axis=1).nlargest(8).index
    pivot_df = pivot_df.loc[top_8]
    
    # Normalizar a porcentajes por columna (municipio)
    pivot_df_pct = pivot_df.div(pivot_df.sum(axis=0), axis=1) * 100

    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot_df_pct, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={'label': '% Votos del Municipio'})
    plt.title("Reto 5.1: Heatmap de Densidad de Votos - Top 8 Candidatos Cámara")
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(OUTPUT_IMG), exist_ok=True)
    plt.savefig(OUTPUT_IMG, dpi=150)
    plt.close()
    print(f"[SUCCESS] Heatmap guardado en {OUTPUT_IMG}")

if __name__ == "__main__":
    generar_heatmap()