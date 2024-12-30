import pandas as pd

# Función para generar los enlaces
def generar_link(ean):
    return f"https://www.vea.com.ar/{ean}?_q={ean}&map=ft"

# Cargar el archivo Excel
input_file = "C:/vea/Eans/Original/Prueba.xlsx"  # Reemplaza con el nombre de tu archivo
output_file = "links.csv"  # Nombre del archivo de salida

# Leer el archivo Excel
df = pd.read_excel(input_file)

# Generar la columna de enlaces
df['link'] = df['EAN'].apply(generar_link)

# Guardar el DataFrame con los enlaces en un nuevo archivo Excel
df.to_csv(output_file, index=False)

print("Archivo generado con éxito:", output_file)
