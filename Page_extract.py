import json
import pandas as pd
import re
from difflib import SequenceMatcher

# Función para encontrar coincidencias similares
def find_best_match(name, json_products):
    best_match = None
    best_ratio = 0.0
    for product in json_products:
        ratio = SequenceMatcher(None, name.lower(), product['name'].lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = product
    return best_match if best_ratio > 0.7 else None  # Ajustar el umbral si es necesario

# Leer el archivo de texto
with open('pagina.txt', 'r', encoding='utf-8') as file:
    lines = [line.strip() for line in file if line.strip()]

# Leer el archivo JSON
with open('datos.json', 'r', encoding='utf-8') as js_file:
    js_data = json.load(js_file)

# Inicializar lista para almacenar productos
products = []

# Procesar bloques de productos en el TXT
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

        # Buscar información complementaria en el JSON con coincidencia flexible
        json_products = [item['item'] for item in js_data['itemListElement']]
        json_product = find_best_match(name, json_products)

        # Combinar datos y agregar al resultado final
        products.append({
            "name": name,
            "brand": brand,
            "promo_price_per_unit": promo_price,
            "previous_price": previous_price,
            "price_per_unit": price_per_unit,
            "promotion_details": promotion_details,
            "image": json_product.get("image") if json_product else None,
            "description": json_product.get("description") if json_product else None,
            "mpn": json_product.get("mpn") if json_product else None,
            "gtin": json_product.get("gtin") if json_product else None,
            "category": json_product.get("category") if json_product else None,
            "price_currency": json_product.get("offers", {}).get("priceCurrency") if json_product else None
        })

        # Saltar al siguiente bloque
        i = j
    else:
        i += 1

# Guardar los datos consolidados en JSON y CSV
with open('consolidated_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(products, json_file, ensure_ascii=False, indent=4)

df = pd.DataFrame(products)
df.to_csv('consolidated_data.csv', index=False)

print("Datos consolidados guardados en 'consolidated_data.json' y 'consolidated_data.csv'.")
