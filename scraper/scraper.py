from pathlib import Path
import argparse
import json
import logging
import sys
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==========================
# CONFIGURACIÓN
# ==========================

BASE_URL = "https://resultadospreccongreso2026.registraduria.gov.co"

API_ENDPOINTS = {
    "SE": BASE_URL + "/json/ACT/SE/{codigo}.json",
    "CA": BASE_URL + "/json/ACT/CA/{codigo}.json",
}

# Municipios solicitados por la prueba
MUNICIPIOS = {
    "tunja": "0700181",
    "duitama": "0700277",
    "sogamoso": "0700001",
    "paipa": "0700079",
}

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "sample_data"
TEMP_DIR = ROOT / "temp_extracted"

TEMP_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "scraper.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
def crear_sesion():

    retry = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[500, 502, 503, 504],
    )

    adapter = HTTPAdapter(max_retries=retry)

    session = requests.Session()

    session.mount("https://", adapter)

    return session

import time


def descargar_json(session, url):

    response = session.get(url, timeout=30)

    response.raise_for_status()

    return response.json()


def guardar_json(datos, archivo):

    with open(
        archivo,
        "w",
        encoding="utf8"
    ) as f:

        json.dump(
            datos,
            f,
            ensure_ascii=False,
            indent=4
        )
def procesar_municipio(nombre):

    nombre = nombre.lower()

    if nombre not in MUNICIPIOS:

        print(f"Municipio '{nombre}' no soportado")

        return

    codigo = MUNICIPIOS[nombre]

    session = crear_sesion()

    for corporacion in ["SE", "CA"]:

        url = API_ENDPOINTS[corporacion].format(
            codigo=codigo
        )

        print(f"Descargando {url}")

        try:

            datos = descargar_json(
                session,
                url
            )

            archivo_temp = TEMP_DIR / f"{nombre}_{corporacion}.json"

            guardar_json(
                datos,
                archivo_temp
            )

            archivo_sample = DATA_DIR / f"{nombre}_{corporacion}.json"

            if not archivo_sample.exists():

                guardar_json(
                    datos,
                    archivo_sample
                )

            logging.info(
                f"{nombre} {corporacion} OK"
            )

            print(
                f"✓ {archivo_temp.name}"
            )

        except Exception as e:

            logging.error(str(e))

            print(f"✗ Error {nombre} {corporacion}")
def procesar_todos():

    for municipio in MUNICIPIOS:

        procesar_municipio(
            municipio
        )
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(

        "--municipios",

        nargs="+"

    )

    args = parser.parse_args()

    if args.municipios:

        for municipio in args.municipios:

            procesar_municipio(
                municipio
            )

    else:

        procesar_todos()


if __name__ == "__main__":

    main()