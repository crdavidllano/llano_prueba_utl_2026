import os
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

DB_PATH = os.path.join(os.path.dirname(__file__), "../db/puestos_2026.db")
OUTPUT_IMG = os.path.join(os.path.dirname(__file__), "scatter_ca_se.png")


def obtener_votos_por_mesa(ruta_db):
    """Obtiene, para cada mesa, el total de votos CA y SE (misma fila = misma mesa)."""
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_mesa,
               SUM(CASE WHEN corporacion = 'CA' THEN votos ELSE 0 END) AS votos_ca,
               SUM(CASE WHEN corporacion = 'SE' THEN votos ELSE 0 END) AS votos_se
        FROM resultados_votos
        GROUP BY id_mesa
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def generar_grafico_dispersion():
    print("[ANALÍTICA] Generando análisis de regresión OLS...")

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"No se encontró la base de datos en {DB_PATH}. Ejecute etl.py primero.")

    rows = obtener_votos_por_mesa(DB_PATH)
    if len(rows) < 3:
        raise ValueError("No hay suficientes mesas con datos para calcular la regresión.")

    x = np.array([r[1] for r in rows], dtype=float)  # votos CA por mesa
    y = np.array([r[2] for r in rows], dtype=float)  # votos SE por mesa
    n_mesas = len(x)

    if np.std(x) == 0 or np.std(y) == 0:
        raise ValueError(
            "Los datos no tienen varianza (todas las mesas dan el mismo total). "
            "Revise el ETL: los votos por mesa no deberían ser constantes."
        )

    r_val, _ = pearsonr(x, y)
    pendiente, intercepto = np.polyfit(x, y, 1)

    print(f"📊 RESULTADO OLS -> r = {r_val:.3f} | pendiente = {pendiente:.3f} | n_mesas = {n_mesas}")

    plt.figure(figsize=(8, 5))
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

    plt.scatter(x, y, color='#2c3e50', s=100, zorder=3, label='Mesas de votación')

    x_linea = np.linspace(x.min() - 10, x.max() + 10, 100)
    y_linea = pendiente * x_linea + intercepto
    plt.plot(x_linea, y_linea, color='#e74c3c', linestyle='--', linewidth=2,
             label=f'Ajuste OLS (y = {pendiente:.2f}x + {intercepto:.1f})')

    plt.title('Reto 5.2: Regresión Lineal OLS — Votos Cámara vs Senado (Boyacá 2026)',
              fontsize=12, fontweight='bold')
    plt.xlabel('Votos Cámara (CA) por mesa', fontsize=10)
    plt.ylabel('Votos Senado (SE) por mesa', fontsize=10)
    plt.legend(loc='upper left')

    plt.text(x.min(), y.max() - (y.max() - y.min()) * 0.1,
              f'r de Pearson: {r_val:.3f} | n = {n_mesas}',
              bbox=dict(facecolor='white', alpha=0.8, edgecolor='#bdc3c7'))

    os.makedirs(os.path.dirname(OUTPUT_IMG), exist_ok=True)
    plt.savefig(OUTPUT_IMG, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Gráfico '{OUTPUT_IMG}' exportado con éxito.")


if __name__ == "__main__":
    generar_grafico_dispersion()