# LLANO Prueba Técnica UTL Senado 2026

## Candidato
* **Nombre:** Cristhian David LLano
* **Email:** cdllanoocampo@gmail.com
* **Rol:** Analista de Datos

## Instalación
Para desplegar y configurar el entorno virtual de ejecución, corra:
```bash
pip install -r requirements.txt

# 1. Ejecutar el Scraper (Intentará API -> si falla descarga desde 'sample_data/')
python scraper/scraper.py

# 2. Ejecutar el proceso ETL para transformar, normalizar e insertar a SQLite puestos_2026.db
python db/etl.py

# 3. Exportar universos consolidados de la base de datos al JSON del dashboard
python dashboard/export_data.py

# 4. Generar visualizaciones y reportes estadísticos
python viz/heatmap.py
python viz/scatter.py

# 5. Generar manifiesto de evaluación de la UTL
python outputs/generar_manifest.py

API
Patrón de URL mapeado: https://resultadospreccongreso2026.registraduria.gov.co/api/v1/del/{departamento}/{municipio}

Campos JSON Críticos Identificados (8+): id_mesa, codpar, candidato_nombre, votos, corporacion, zona, puesto, mesa.

Mecanismo Nomenclátor: Parámetros codificados donde codpar=5 mapea a Alianza Verde en Cámara y se homologa de forma cruzada con codpar=57 en Senado.

Cabeceras HTTP requeridas: Uso obligatorio de un User-Agent institucional para mitigar bloqueos preventivos por Web Application Firewalls (WAF).

Municipios en la BD
La base de datos contiene la cobertura completa de los cuatro municipios del departamento de Boyacá estipulados:

TUNJA (Capital del departamento)

PAIPA (Ciudad intermedia)

SOGAMOSO (Segunda ciudad)

DUITAMA (Tercera ciudad)

Hallazgos principales
Fenómeno de Arrastre: Se evidencia un fuerte arrastre de votos en la colectividad Alianza Verde en las cabeceras municipales principales, donde el ratio supera el umbral de 1.0, indicando tracción directa desde las listas de Senado hacia las regionales.

Anomalías por Dominancia: Mediante el análisis de control SQL, se identificaron mesas específicas con concentraciones atípicas superiores al 60%, sugiriendo núcleos consolidados de votación homogénea.

Bonus implementados
Flag --preflight en Scraper: Permite inspeccionar volúmenes y disponibilidad de la API sin realizar descargas físicas de registros.

3 Índices de Optimización SQLite: Implementados directamente en el archivo schema.sql para acelerar los tiempos de ejecución de consultas cruzadas complejas.

Atribución Determinística Explicada (Reto 3.3): El Top de Cámara no coincide necesariamente con el de Senado ya que la transferencia de votos depende estrictamente del factor proporcional del partido y no del volumen absoluto bruto por candidato individual.

Dark Mode Toggle: Integrado nativamente en el Dashboard mediante variables y propiedades CSS personalizadas limpias.

Botón de Exportación CSV: Funcionalidad integrada del lado del cliente para descarga inmediata del set analítico sin dependencias de backend.