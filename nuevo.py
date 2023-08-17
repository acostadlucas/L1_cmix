import pandas as pd
mi_tabla = [
    ['Doc. N°', 'Descripción', 'Fecha'],
    ['1561-1-872', 'Tabla 1', '2023-07-24'],
    ['229-23060-089', 'Tabla 2', '2023-07-25']
]


# Crear un DataFrame a partir de la tabla
df = pd.DataFrame(mi_tabla[1:], columns=mi_tabla[0])

print(df)

# Acceder al texto del primer encabezado
primer_header = df.columns[0]

print(primer_header)
