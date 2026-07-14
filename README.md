# LLANO-Prueba Técnica UTL Senado 2026

## Candidato
* **Nombre:** Cristhian David Llano
* **Email:** cdllanoocampo@gmail.com
* **Rol:** Analista de Datos

## Instalación 
Para configurar el entorno virtual y preparar el sistema para la ejecución de todo el pipeline, ejecute el siguiente comando en su terminal:
```bash
pip install -r requirements.txt

# Paso 2: Procesar, normalizar y poblar la base de datos relacional SQLite
python db/etl.py

# Paso 3: Consolidar métricas y generar JSON estructurado para el Dashboard
python dashboard/export_data.py

# Paso 4: Generar visualizaciones estáticas (Mapas de calor y dispersión)
python viz/heatmap.py
python viz/scatter.py

# Paso 5: Compilar el manifiesto final de evaluación institucional
python outputs/generar_manifest.py

## Pipeline de ejecución

# 1. Ejecutar el Scraper (Intentará consumir la API; de lo contrario, usará los datos de 'sample_data/')
python scraper/scraper.py

# 2. Ejecutar el proceso ETL (Transforma, normaliza e inserta los datos en SQLite 'puestos_2026.db')
python db/etl.py

# 3. Exportar universos consolidados de la base de datos al JSON requerido por el dashboard
python dashboard/export_data.py

# 4. Generar visualizaciones y reportes estadísticos (Mapas de calor y gráficos de dispersión)
python viz/heatmap.py
python viz/scatter.py

# 5. Generar el manifiesto de evaluación oficial de la UTL
python outputs/generar_manifest.py

## API
Patrón de URL mapeado: https://resultadospreccongreso2026.registraduria.gov.co/api/v1/del/{departamento}/{municipio}  Campos JSON Críticos Identificados (8+): id_mesa, codpar, candidato_nombre, votos, corporacion, zona, puesto y mesa.  Mecanismo Nomenclátor: Los parámetros codificados asocian los identificadores numéricos a las agrupaciones políticas. Por ejemplo, el código de partido (codpar) 5 mapea a Alianza Verde en Cámara y se homologa de forma cruzada con el código 57 en Senado.  Cabeceras HTTP requeridas: Se implementa el uso obligatorio de un User-Agent institucional con el fin de mitigar bloqueos preventivos por parte de Firewalls de Aplicación Web (WAF).  
## Municipios en la BD
La base de datos contiene la cobertura completa de los cuatro municipios del departamento de Boyacá estipulados para este análisis:  TUNJA: Capital del departamento.  PAIPA: Ciudad intermedia.  SOGAMOSO: Segunda ciudad.  DUITAMA: Tercera ciudad.

## Hallazgos principales
Fenómeno de Arrastre: Se evidencia un fuerte arrastre de votos en la colectividad Alianza Verde en las cabeceras municipales principales, donde el ratio supera el umbral de 1.0, indicando tracción directa desde las listas de Senado hacia las regionales.  Anomalías por Dominancia: Mediante el análisis de control SQL, se identificaron mesas específicas con concentraciones atípicas superiores al 60%, sugiriendo núcleos consolidados de votación homogénea.  Atribución Determinística Explicada (Reto 3.3): El Top de Cámara no coincide necesariamente con el de Senado, ya que la transferencia de votos depende estrictamente del factor proporcional del partido y no del volumen absoluto bruto por candidato individual. 

## Bonus implementados 
Flag --preflight en Scraper: Permite inspeccionar volúmenes y la disponibilidad de la API sin necesidad de realizar descargas físicas de registros[cite: 4].

3 Índices de Optimización SQLite: Implementados directamente en el archivo schema.sql para acelerar los tiempos de ejecución de las consultas cruzadas complejas[cite: 4].

Dark Mode Toggle: Integrado de forma nativa en el Dashboard mediante variables y propiedades CSS personalizadas[cite: 4].

Botón de Exportación CSV: Funcionalidad del lado del cliente que permite descargar de forma inmediata el set analítico sin depender de llamadas adicionales al backend[cite: 4].
