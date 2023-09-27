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
import difflib


def renombrar_key_to_files_pdf_recibidos(dataframe, path):
    """
    Renombra key_to_files PDF en un directorio según los valores de un DataFrame.

    Args:
        dataframe (pd.DataFrame): El DataFrame que contiene los valores a partir de los cuales se generarán los nuevos nombres.
        path (str): La ruta al directorio que contiene los key_to_files PDF a renombrar.

    Returns:
        None

    """
    # Obtener una lista de key_to_files PDF en el directorio
    key_to_files_pdf = [archivo for archivo in os.listdir(path) if archivo.endswith('.pdf')]

    # Recorrer cada fila del DataFrame
    for indice, fila in dataframe.iterrows():
        # Obtener el valor de la primera columna
        primer_valor = str(fila[0])[:19]  # Tomar los primeros 19 caracteres
        #print(f"Estos son los primeros 19 caracteres: {primer_valor}")

        # Buscar un archivo PDF que coincida con el valor
        archivo_encontrado = None
        for archivo_pdf in key_to_files_pdf:
            if primer_valor in archivo_pdf:
                archivo_encontrado = archivo_pdf
                break

        if archivo_encontrado:
           # Renombrar el archivo PDF con la concatenación de los primeros tres valores de la fila
            nuevo_nombre = '-'.join(str(valor) for valor in fila[:3])
            nuevo_nombre = nuevo_nombre.replace('/', '-')  # Reemplazar barras por guiones
            nuevo_nombre = nuevo_nombre[:500]  # Limitar el nombre a 255 caracteres (sistema de key_to_files)

            
            # Ruta completa del archivo antiguo y nuevo
            archivo_antiguo = os.path.join(path, archivo_encontrado)
            archivo_nuevo = os.path.join(path, f'{nuevo_nombre}.pdf')

            # Renombrar el archivo
            os.rename(archivo_antiguo, archivo_nuevo)
            print(f"Renombrado: {archivo_antiguo} -> {archivo_nuevo}")
        else:
            print(f"No se encontró un archivo para: {primer_valor}")




# Ejemplo de uso:
data = {'Columna1': ['M-2000-35170-003-PL', '229-23256-001-MC', '229-23256-001-PL'],
        'Columna2': ['Lorem Ipsum', 'Lorem Ipsum', 'Lorem Ipsum'],
        'Columna3': ['Neque', 'Neque', 'Neque'],
        'Columna4': ['porro', 'porro', 'porro'],
        'Columna5': ['quisquam', 'quisquam', 'quisquam'],
        'Columna6': ['est', 'est', 'est'],
        'Columna7': ['qui', 'qui', 'qui'],
        'Columna8': ['dolorem', 'dolorem', 'dolorem']}
df = pd.DataFrame(data)

archivo_path = 'C:\\Users\\lucas\\Downloads\\ejemplo\\ejemploB\\1561-1-766 2023-06-05\\1561-1-766.pdf'
#renombrar_key_to_files_pdf(df, directorio)

############################################################
import os
import csv

import os
import openpyxl

def manejar_key_to_files_excel(path_directorio):
    """
    Administra key_to_files Excel en un directorio dado.
    
    :param path_directorio: Ruta al directorio donde se buscarán y crearán key_to_files Excel.
    :return: Un diccionario con nombres de archivo como claves y rutas completas a los key_to_files Excel como valores.
    """
    key_to_files = {
        "ProyCivil_SE": None,
        "ProyElec_SE": None,
        "ProyElectro_SE": None,
        "ProyMec_SE": None,
        "ProyCivil_LT": None,
        "ProyElectro_LT": None,
        "ProyMec_LT": None,
        "Suministros_SE": None,
        "Suministros_LT":None,
    }
    
    # Verificar si el directorio existe, si no, crearlo
    if not os.path.exists(path_directorio):
        os.makedirs(path_directorio)

    for nombre_archivo in key_to_files.keys():
        archivo_path = os.path.join(path_directorio, f"{nombre_archivo}.xlsx")
        
        # Comprobar si el archivo existe
        if os.path.exists(archivo_path):
            key_to_files[nombre_archivo] = archivo_path
            print(f"El archivo {nombre_archivo}.xlsx existe en {archivo_path}")
        else:
            # Si el archivo no existe, créalo con openpyxl
            wb = openpyxl.Workbook()
            
            # Seleccionar la hoja de trabajo activa (por defecto es la primera)
            hoja = wb.active
            
            # Agregar los encabezados
            encabezados = ['Doc. N°-Tipo', 'Rev.', 'Descripción', 'Nº LO', 'Recibido', 'Nº LO Resp', 'Respuesta', 'Situación']
            hoja.append(encabezados)
            
            wb.save(archivo_path)
            key_to_files[nombre_archivo] = archivo_path
            print(f"El archivo {nombre_archivo}.xlsx fue creado en {archivo_path}")

    return key_to_files


# Ejemplo de uso:
# directorio = "C:\\Users\\lucas\\Downloads\\se crea"
directorio = "C:\\Users\\lucas\\Downloads\\otraCrear"
#key_to_files_csv = manejar_key_to_files_csv(directorio)

# Imprimir los resultados
# for nombre, ruta in key_to_files_csv.items():
#     print(f"{nombre}: {ruta}")

#######################################################################
import pandas as pd
import os


def procesar_dataframe_y_escribir_key_to_files(dataframe, directorios):
    """
    Carga los datos en los archivos excel.
    
    :param dataframe: dataframe del cual obtendra los datos de los documentos a cargar.
    :directorios: Un diccionario con nombres de archivo como claves y rutas completas a los archivos como valores.
    """
    key_to_files = {
        "23": "ProyCivil_SE",
        "24": "ProyElec_SE",
        "26": "ProyElectro_SE",
        "25": "ProyMec_SE",
        "33": "ProyCivil_LT",
        "36": "ProyElectro_LT",
        "35": "ProyMec_LT",
        "7": "Suministros_SE",
        "8": "Suministros_LT",
    }

    is_doc_LT = False
    is_doc_SE = False

    for index, fila in dataframe.iterrows():
        valor_primera_columna = fila['Doc. N°-Tipo']
        
        # Separar el valor en función de si comienza con L, M u otra letra
        if valor_primera_columna.startswith(('L', 'M')):
            is_doc_LT = True
            valores = valor_primera_columna.split('-')[2:][0][:2]
            print(valores)
        else:
            is_doc_SE = True
            valores = valor_primera_columna.split('-')[1:][0][:2]
            print(valores)

        # Buscar si los valores coinciden con las claves en key_to_files
        key_a_buscar = "".join(valores)


        if key_a_buscar in key_to_files:
            directorio_key = key_to_files[key_a_buscar]

            # Obtener el directorio correspondiente desde el diccionario directorios
            directorio = directorios.get(directorio_key)

            # Leer el archivo Excel existente en un DataFrame
            df_existente = pd.read_excel(directorio)

            # Comprobar si ya existe un valor idéntico en la columna 'Doc. N°-Tipo'
            if valor_primera_columna in df_existente['Doc. N°-Tipo'].values:
                # Si existe, verificar si hay nuevas columnas para completar
                existing_row = df_existente[df_existente['Doc. N°-Tipo'] == valor_primera_columna]

                # Completar las columnas vacías en el registro existente
                for col in df_existente.columns:
                    if col in fila.index and pd.isna(existing_row[col].values[0]):
                        df_existente.loc[existing_row.index, col] = fila[col]
            else:
                # Si no existe, agregar la fila completa al DataFrame existente
                df_existente = pd.concat([df_existente, fila.to_frame().T], ignore_index=True)

            # Exportar el archivo existente como XLSX pero con los datos cargados
            df_existente.to_excel(directorio, index=False)
        
        elif is_doc_LT or is_doc_SE:
            if is_doc_SE:
                print("ESTOY ACA")
                is_doc_SE = False
                print(f"Ahora la variables is_doc_SE es {is_doc_SE}")
                directorio_key = key_to_files["7"]
                print(f"este es el key donde se debe escribir datos {directorio_key}")
                directorio = directorios.get(directorio_key)
                print(f"este es el directorio donde se debe escribir datos {directorio}")
                df_existente = pd.read_excel(directorio)
                if valor_primera_columna in df_existente['Doc. N°-Tipo'].values:
                    existing_row = df_existente[df_existente['Doc. N°-Tipo'] == valor_primera_columna]
                    for col in df_existente.columns:
                        if col in fila.index and pd.isna(existing_row[col].values[0]):
                            df_existente.loc[existing_row.index, col] = fila[col]
                else:
                    df_existente = pd.concat([df_existente, fila.to_frame().T], ignore_index=True)
                    print(f"este es el df ahora:\n{df_existente}")

                df_existente.to_excel(directorio, index=False)

            elif is_doc_LT:
                is_doc_LT = False
                directorio_key = key_to_files["8"]
                directorio = directorios.get(directorio_key)
                df_existente = pd.read_excel(directorio)
                if valor_primera_columna in df_existente['Doc. N°-Tipo'].values:
                    existing_row = df_existente[df_existente['Doc. N°-Tipo'] == valor_primera_columna]
                    for col in df_existente.columns:
                        if col in fila.index and pd.isna(existing_row[col].values[0]):
                            df_existente.loc[existing_row.index, col] = fila[col]
                else:
                    df_existente = pd.concat([df_existente, fila.to_frame().T], ignore_index=True)
                
                df_existente.to_excel(directorio, index=False)
                                        
        else:
            print(f"La clave {key_a_buscar} no está en el diccionario key_to_files")

directorios = manejar_key_to_files_excel(directorio)
print(directorios)

# DataFrame de ejemplo
data = {'Doc. N°-Tipo': [ '229-16000-'],
       'Descripción': ['Valor3']}

df = pd.DataFrame(data)

# Llamada a la función para procesar el DataFrame y escribir en los key_to_files CSV
# Reemplaza 'directorios' con tu propia lógica para obtener los directorios
directorios = manejar_key_to_files_excel(directorio)
procesar_dataframe_y_escribir_key_to_files(df, directorios)

################################################
# import locale
# import datetime
# import re

# def convert_date_format(fecha_str):
#     """
#     Convierte una fecha en formato "dd de mes de yyyy" a formato "dd/mm/yyyy".

#     Parameters:
#         fecha_str (str): La fecha en formato "dd de mes de yyyy".

#     Returns:
#         str: La fecha convertida en formato "dd/mm/yyyy".
#     """
#     # Establecer el idioma español para el formato de fecha
#     locale.setlocale(locale.LC_TIME, 'es_ES')

#     # Reemplazar "setiembre" por "septiembre" en la cadena de fecha
#     fecha_str = fecha_str.replace('setiembre', 'septiembre')

#     # Eliminar caracteres de salto de línea ('\n') y espacios en blanco adicionales de la cadena de fecha
#     fecha_str = fecha_str.replace('\n', '').strip()
#     fecha_str = re.sub(r'de(\d{4})', r'de \1', fecha_str)

#     # Crear un objeto datetime a partir de la fecha en formato "dd de mes de yyyy"
#     fecha_obj = datetime.datetime.strptime(fecha_str, "%d de %B de %Y")

#     # Convertir la fecha a formato "dd/mm/yyyy"
#     fecha_formato_deseado = fecha_obj.strftime("%d/%m/%Y")

#     return fecha_formato_deseado

# lista_fechas = ['01 de enero de 2023','02 de febrero de 2024','03 de marzo de 2025','04 de abril de 2026', '05 de mayo de 2027','06 de junio de 2028','07 de julio de 2029','08 de agosto de 2030','09 de setiembre de\n\n2031','10 de octubre de\n\n2032','11 de noviembre de\n\n2033', '12 de diciembre de\n\n2034']

# for fech in lista_fechas:
#     print(convert_date_format(fech))

