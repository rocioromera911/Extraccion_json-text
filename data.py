import json
import pandas as pd
from playwright.sync_api import sync_playwright
import os
import time


def extraer_json(page):
    try:
        script_tag = page.locator('//body/div[2]/div/div[1]/div/script')
        json_content = script_tag.text_content()
        return json.loads(json_content)
    except Exception as e:
        print(f"Error al extraer JSON: {e}")
        return None


def extraer_texto_visible(page):
    try:
        return page.inner_text("body")
    except Exception as e:
        print(f"Error al extraer texto visible: {e}")
        return ""


def scrollear_pagina(page, veces=1, espera=2):
    try:
        for i in range(veces):
            print(f"Realizando scroll {i + 1}/{veces}...")
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(espera)
    except Exception as e:
        print(f"Error al scrollear la página: {e}")


def procesar_link(ean, link):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            print(f"Navegando a {link}...")
            page.goto(link)

            # Esperar a que la página cargue completamente
            page.wait_for_load_state("load")

            # Tiempo adicional para asegurar que todos los datos dinámicos se carguen
            print("Esperando 8 segundos adicionales para cargar dinámicamente...")
            time.sleep(8)

            # Scrollear la página para cargar más contenido dinámico
            print("Scrolleando la página...")
            scrollear_pagina(page, veces=1, espera=2)

            # Recargar la página y esperar nuevamente
            print("Recargando la página para asegurar que los datos estén completamente cargados...")
            page.reload()
            page.wait_for_load_state("load")

            # Esperar tiempo adicional
            print("Esperando 8 segundos adicionales después de recargar...")
            time.sleep(8)

            # Extraer datos
            json_data = extraer_json(page)
            texto_visible = extraer_texto_visible(page)

            return {
                "EAN": ean,
                "URL": link,
                "TextoVisible": texto_visible,
                "JSON": json_data
            }

        except Exception as e:
            print(f"Error al procesar el link {link}: {e}")
            return {
                "EAN": ean,
                "URL": link,
                "TextoVisible": "",
                "JSON": None,
                "Error": str(e)
            }

        finally:
            browser.close()


def procesar_input(input_source):
    if os.path.isfile(input_source):  # Detectar si es un archivo
        # Leer archivo (Excel o CSV generado por EXTRACT.py)
        df = pd.read_(input_source) if input_source.endswith('.xlsx') else pd.read_csv(input_source)
        return df[['EAN', 'Link']].dropna().values.tolist()
    else:  # Si no es un archivo, asumir que es un único link
        return [[None, input_source]]  # Retornar como una lista con un link único


def main(input_source, output_file):
    # Procesar el input (archivo o link único)
    links = procesar_input(input_source)

    all_results = []

    # Procesar los links secuencialmente para respetar la lógica original del scrolleo y tiempos
    for ean, link in links:
        result = procesar_link(ean, link)
        all_results.append(result)

    # Guardar resultados en un archivo JSON consolidado
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(all_results, json_file, ensure_ascii=False, indent=4)

    print(f"Resultados guardados en {output_file}.")


if __name__ == "__main__":
    input_source = "C:/vea/Eans/Original/Prueba.xlsx"  # Ruta del archivo o un link directo
    output_file = "resultados_combinados.json"  # Archivo de salida consolidado
    main(input_source, output_file)
