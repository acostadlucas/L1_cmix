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
""" 
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
print(new_df) """

#########################################################################################
import tabula
import difflib
import pandas as pd

data = {
    'Col1': ["M-2000-36140-001", "PL", "-", "PL"],
    'Col2': ["PL", "-", "PL", "PL"],
    'Col3': ["00", "-", "PL", "PL"],
    'Col4': ["Puesta tierra en suelo Rocoso", "Protocolos de resistividad - Seccionamiento LT", "PL", "VHA"],
    'SITUACION': ["APROBADO", "Aprobado Con\rLimitación", "NO APROBADO", "VISTO"]
    
}

df = pd.DataFrame(data)

tables = [df]


def transformar_situacion(tablas, umbral_similitud=0.843):
    """
    Aplica un algoritmo de transformación a las tablas proporcionadas.

    Esta función toma una lista de DataFrames y realiza las siguientes transformaciones en la quinta columna de cada tabla:
    - Si el valor se asemeja a "aprobado" en un cierto umbral, se reemplaza por "(A)".
    - Si el valor se asemeja a "no aprobado" en un cierto umbral, se reemplaza por "(NA)".
    - Si el valor se asemeja a "aprobado con limitacion" en un cierto umbral, se reemplaza por "(ACL)".
    - Si no cumple con las restricciones anteriores, se encierra en paréntesis.

    :param tablas: Una lista de DataFrames, donde cada DataFrame representa una tabla con al menos cinco columnas.
    :param umbral_similitud: El umbral de similitud para considerar la similitud entre cadenas (por defecto, 0.843).
    :return: Una lista de DataFrames modificados.
    """
    def transformar_valor(valor):
        if valor and isinstance(valor, str):
            valor = valor.lower()
            if difflib.SequenceMatcher(None, valor, "aprobado").ratio() >= umbral_similitud:
                return "(A)"
            elif difflib.SequenceMatcher(None, valor, "no aprobado").ratio() >= umbral_similitud:
                return "(NA)"
            elif difflib.SequenceMatcher(None, valor, "aprobado con limitacion").ratio() >= umbral_similitud:
                return "(ACL)"
            else:
                return f"({valor.upper()})"
        return valor

    tablas_modificadas = []
    for tabla in tablas:
        print(f"Esta es la tabla sin cambiar su situacion \n{tabla}")
        if tabla.shape[1] == 5:
            quinta_columna = tabla.iloc[:, 4]
            for i, valor in enumerate(quinta_columna):
                nuevo_valor = transformar_valor(valor)
                quinta_columna[i] = nuevo_valor
            tablas_modificadas.append(tabla)
        print(f"Esta es la tabla cambiando su situacion \n{tabla}")
    return tablas_modificadas


#transformar_situacion(tables)

################################

import pandas as pd

# DataFrame de ejemplo
data = {
    'A': [1, 2, 3],
    'B': [4, 5, 6]
}
df = pd.DataFrame(data)

# Crear un MultiIndex para las columnas
multi_index = pd.MultiIndex.from_tuples([('Grupo 1', 'A'), ('Grupo 2', 'B')])

# Establecer el MultiIndex en las columnas del DataFrame
df.columns = multi_index

# Ahora el DataFrame tiene un MultiIndex en las columnas
#print(df)



#######################################
import pandas as pd

# DataFrame de ejemplo
data = {'Columna1': [1, 2, 3], 'Columna2': [4, 5, 6]}
df = pd.DataFrame(data)

# Lista de strings que deseas agregar como nuevas columnas
lista_de_strings = ['Fecha', 'Nº LO', 'Asunto']
valores= ['12/08/2023', '1561-1-205', 'Descripcion del asunto para Nota']

# Usar un bucle for para agregar cada elemento de la lista como una nueva columna
def append_LO_data(data_list, df, valores):
    """
    Agrega nuevas columnas a un DataFrame utilizando una lista de datos.

    Parameters:
        data_list (list): Lista de nombres de columnas a agregar.
        df (pandas.DataFrame): El DataFrame al que se agregarán las nuevas columnas.
        valores (list): Lista de valores correspondientes a las nuevas columnas.

    Returns:
        pandas.DataFrame: El DataFrame actualizado con las nuevas columnas.
    """
    for i, columna_nueva in enumerate(data_list):
        df[columna_nueva] = valores[i]
    return df

# El DataFrame ahora tiene las nuevas columnas agregadas
#print(append_LO_data(lista_de_strings, df, valores))


##########################################################
import pandas as pd

# Crear un DataFrame de ejemplo
data = {'Columna1': [1, 2, 3],
        'Columna2': ['A', 'B', 'C'],
        'Columna3': [4, 5, 6]}

df = pd.DataFrame(data)

# Unir las dos primeras columnas con un "-" y almacenar el resultado en una nueva columna
df['Columna1-Columna2'] = df['Columna1'].astype(str) + '-' + df['Columna2']

# Eliminar las dos primeras columnas
df.drop(['Columna1', 'Columna2'], axis=1, inplace=True)

# Reordenar las columnas para que la nueva columna esté en primer lugar
columnas = df.columns.tolist()
columnas = ['Columna1-Columna2'] + columnas

# Reemplazar el DataFrame original con las columnas reordenadas
df = df[columnas]

# Eliminar la última columna que contiene la concatenación
df = df.iloc[:, :-1]  # Elimina la última columna

# Mostrar el DataFrame resultante
#print(df)


###############################
import pandas as pd

# Crear un DataFrame vacío con 7 columnas
DF_BASE = pd.DataFrame(columns=['Doc. N°-Tipo', 'Rev.', 'Descripción', 'Nº LO', 'Fecha', 'Nº LO Resp', 'días'])

# Crear un segundo DataFrame con datos de ejemplo
data = {'Columna1': [1, 2, 3],
        'Columna2': ['A', 'B', 'C'],
        'Columna3': [4, 5, 6]}

df2 = pd.DataFrame(data)

# Llenar df1 con los contenidos de df2
DF_BASE = pd.concat([DF_BASE, df2], ignore_index=True)

# Mostrar el DataFrame resultante
#print(DF_BASE)


######################################################################
import os
import pandas as pd

def renombrar_archivos_pdf(dataframe, path):
    # Obtener una lista de archivos PDF en el directorio
    archivos_pdf = [archivo for archivo in os.listdir(path) if archivo.endswith('.pdf')]

    # Recorrer cada fila del DataFrame
    for indice, fila in dataframe.iterrows():
        # Obtener el valor de la primera columna
        primer_valor = str(fila[0])[:18]  # Tomar los primeros 18 caracteres

        # Buscar un archivo PDF que coincida con el valor
        archivo_encontrado = None
        for archivo_pdf in archivos_pdf:
            if primer_valor in archivo_pdf:
                archivo_encontrado = archivo_pdf
                break

        if archivo_encontrado:
            # Renombrar el archivo PDF con la concatenación de la fila
            nuevo_nombre = '-'.join(str(valor) for valor in fila)
            nuevo_nombre = nuevo_nombre.replace('/', '-')  # Reemplazar barras por guiones
            nuevo_nombre = nuevo_nombre[:255]  # Limitar el nombre a 255 caracteres (sistema de archivos)
            
            # Ruta completa del archivo antiguo y nuevo
            archivo_antiguo = os.path.join(path, archivo_encontrado)
            archivo_nuevo = os.path.join(path, f'{nuevo_nombre}.pdf')

            # Renombrar el archivo
            os.rename(archivo_antiguo, archivo_nuevo)
            print(f"Renombrado: {archivo_antiguo} -> {archivo_nuevo}")
        else:
            print(f"No se encontró un archivo para: {primer_valor}")

# Ejemplo de uso:
data = {'Columna1': ['Valor1', 'Valor2', 'Valor3'],
        'Columna2': ['Lorem Ipsum', 'Lorem Ipsum', 'Lorem Ipsum'],
        'Columna3': ['Neque', 'Neque', 'Neque'],
        'Columna4': ['porro', 'porro', 'porro'],
        'Columna5': ['quisquam', 'quisquam', 'quisquam'],
        'Columna6': ['est', 'est', 'est'],
        'Columna7': ['qui', 'qui', 'qui'],
        'Columna8': ['dolorem', 'dolorem', 'dolorem']}
df = pd.DataFrame(data)

directorio = 'C:\\Users\\lucas\\Downloads\\prueba'
renombrar_archivos_pdf(df, directorio)


