""" import pandas as pd
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
 """

 #####################################################

import pandas as pd

def transform_dataframe(df):
    # Guardar los headers originales del dataframe
    original_headers = df.columns.tolist()
    print(f"estos son los valores originales en el header:\n{original_headers}")
    
    # Verificar el número de columnas del dataframe
    num_columns = len(df.columns)
    
    # Crear una nueva fila con los valores originales
    original_values = df.values.tolist()
    original_values.append(original_headers)  # Usamos append() en lugar de extend()
    print(original_values)
    
    # Crear un nuevo dataframe con los valores originales en una nueva fila
    new_df = pd.DataFrame([original_values[0]], columns=original_headers)
    print(f"y esto tb quiero ver:\n{new_df}")
    
    # Reemplazar los headers del dataframe según el número de columnas
    if num_columns == 5:
        new_headers = ['Doc. N°', 'Tipo', 'Rev.', 'Descripcion', 'Situacion']
    elif num_columns == 4:
        new_headers = ['Doc. N°', 'Tipo', 'Rev.', 'Descripcion']
    else:
        raise ValueError("El dataframe debe tener más 4 o 5 columnas")
    
    new_df.columns = new_headers
    
    # Agregar el resto de filas al nuevo dataframe
    new_df = pd.concat([new_df, pd.DataFrame(original_values[1:], columns=new_headers)], ignore_index=True)
    
    return new_df

# Ejemplo de uso
data = {
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 8, 9],
    'D': [10, 11, 12],
}

df = pd.DataFrame(data)
new_df = transform_dataframe(df)
print(new_df)

