import json
import time
import csv
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor

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

def procesar_pagina(url, browser):
    try:
        context = browser.new_context()
        page = context.new_page()

        print(f"Navegando a {url}...")
        page.goto(url)

        # Esperar a que la página cargue completamente
        page.wait_for_load_state("load")

        # Esperar tiempo adicional para asegurarse de que todos los datos dinámicos estén cargados
        print("Esperando 5 segundos adicionales para asegurar la carga completa...")
        time.sleep(5)

        # Scrollear la página
        print("Scrolleando la página para cargar más contenido...")
        scrollear_pagina(page, veces=1, espera=2)

        # Recargar la página y esperar nuevamente
        print("Recargando la página para asegurarse de que los datos estén cargados correctamente...")
        page.reload()
        page.wait_for_load_state("load")

        # Esperar tiempo adicional nuevamente
        print("Esperando 3 segundos adicionales después de recargar...")
        time.sleep(3)

        # Llamar a las funciones de extracción
        json_data = extraer_json(page)
        texto_visible = extraer_texto_visible(page)

        context.close()
        return {"url": url, "json_data": json_data, "texto_visible": texto_visible}

    except Exception as e:
        print(f"Error al procesar la página {url}: {e}")
        return {"url": url, "json_data": None, "texto_visible": None}

def main(ruta_archivo):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        todos_los_datos_json = []
        texto_visible_total = ""

        try:
            # Leer las URLs desde el archivo
            with open(ruta_archivo, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file, delimiter="\t")  # Usamos DictReader para acceder a columnas por nombre
                urls = [row["link"] for row in reader]  # Obtenemos solo los enlaces desde la columna "link"

            # Usar un ThreadPoolExecutor para procesar varias páginas en paralelo
            with ThreadPoolExecutor(max_workers=5) as executor:
                resultados = list(executor.map(lambda url: procesar_pagina(url, browser), urls))

            # Procesar los resultados
            for resultado in resultados:
                url = resultado["url"]
                json_data = resultado["json_data"]
                texto_visible = resultado["texto_visible"]

                if json_data:
                    todos_los_datos_json.append({"url": url, "data": json_data})
                else:
                    print(f"No se pudo extraer JSON de la URL: {url}")

                if texto_visible:
                    texto_visible_total += f"\n--- Contenido de {url} ---\n"
                    texto_visible_total += texto_visible

            # Guardar los resultados en archivos
            with open("Datos_combinados.json", "w", encoding="utf-8") as json_file:
                json.dump(todos_los_datos_json, json_file, ensure_ascii=False, indent=4)

            with open("Texto_visible_combinado.txt", "w", encoding="utf-8") as txt_file:
                txt_file.write(texto_visible_total)

            print("Extracción completada. Datos guardados en 'Datos_combinados.json' y 'Texto_visible_combinado.txt'.")

        except Exception as e:
            print(f"Error en el proceso principal: {e}")

        finally:
            browser.close()

# Llama a main() pasando la ruta del archivo con los enlaces
if __name__ == "__main__":
    ruta_archivo = "C:/vea/links.csv"  # Archivo con una lista de URLs (una por línea o en formato CSV)
    main(ruta_archivo)
