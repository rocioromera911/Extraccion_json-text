import json
import pandas as pd
import re

# Función para procesar los datos de la página y el JSON
def procesar_datos(input_file, txt_file, json_file, output_file):
    # Leer archivo de entrada con la tabla original
    df = pd.read_excel(input_file) if input_file.endswith('.xlsx') else pd.read_csv(input_file)

    # Leer archivo de texto
    with open(txt_file, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()]

    # Leer archivo JSON
    with open(json_file, 'r', encoding='utf-8') as js_file:
        js_data = json.load(js_file)

    # Procesar los bloques en el TXT
    results = []
    i = 0
    while i < len(lines):
        if "Ver Producto" in lines[i]:  # Comienza un nuevo producto
            # Inicializar variables
            brand = None
            name = None
            prices = []
            promotion_details = None
            sku = None
            price_per_unit = None

            # Marca y nombre del producto
            if i + 1 < len(lines):
                brand = lines[i + 1]
            if i + 2 < len(lines):
                name = lines[i + 2]

            # Detectar precios y promociones en el bloque
            j = i + 3  # Comenzar después de `brand` y `name`
            while j < len(lines) and "Agregar" not in lines[j]:  # Bloque termina con "Agregar"
                if "sku:" in lines[j]:
                    sku = lines[j].split(":")[-1].strip()
                elif re.match(r'\$\d+[.,]?\d*', lines[j]):  # Detectar precios
                    prices.append(float(lines[j].replace('$', '').replace('.', '').replace(',', '.')))
                elif re.match(r'(2x1|2do al \d+%|Llevando \d+)', lines[j]):  # Detectar promociones
                    promotion_details = lines[j]
                elif re.match(r'-?\d+%', lines[j]):  # Detectar descuentos en porcentaje
                    if promotion_details:
                        promotion_details += f", {lines[j]}"
                    else:
                        promotion_details = lines[j]
                elif "Precio" in lines[j]:  # Detectar precio por unidad
                    price_per_unit = lines[j]  # Capturar la línea completa
                j += 1

            # Ordenar precios y asignar roles
            prices = sorted(prices)
            promo_price = prices[0] if len(prices) > 0 else None
            previous_price = prices[1] if len(prices) > 1 else None

            # Combinar datos en un diccionario
            results.append({
                "name": name,
                "brand": brand,
                "promo_price_per_unit": promo_price,
                "previous_price": previous_price,
                "price_per_unit": price_per_unit,
                "promotion_details": promotion_details,
                "sku": sku
            })

            # Saltar al siguiente bloque
            i = j
        else:
            i += 1

    # Agregar los datos extraídos a la tabla original
    for index, row in df.iterrows():
        ean = str(row["EAN"]).strip()
        producto = next((r for r in results if r.get("sku") == ean), None)
        if producto:
            df.loc[index, "Marca"] = producto["brand"]
            df.loc[index, "Precio Promoción"] = producto["promo_price_per_unit"]
            df.loc[index, "Precio Anterior"] = producto["previous_price"]
            df.loc[index, "Precio Unidad"] = producto["price_per_unit"]
            df.loc[index, "Detalles Promoción"] = producto["promotion_details"]

    # Guardar la tabla actualizada
    df.to_excel(output_file, index=False)
    print(f"Datos procesados y guardados en {output_file}.")


if __name__ == "__main__":
    input_file = "productos.xlsx"  # Archivo con columnas "Descripción" y "EAN"
    txt_file = "pagina.txt"  # Archivo de texto extraído
    json_file = "Datos.json"  # Archivo JSON extraído
    output_file = "productos_actualizados.xlsx"  # Archivo de salida con los datos actualizados

    procesar_datos(input_file, txt_file, json_file, output_file)
