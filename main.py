# Importar los módulos necesarios de la biblioteca tkinter y otras librerías
import tkinter as tk
from tkinter.filedialog import askdirectory
import os
import pathlib as p
import glob
import re
import tabula
import pytesseract
from pdf2image import convert_from_path
import datetime
import locale
import pandas as pd
import time
import difflib
pd.options.mode.chained_assignment = None

DF_BASE = pd.DataFrame(columns=['Doc. N°-Tipo', 'Rev.', 'Descripción', 'Nº LO', 'Fecha', 'Nº LO Resp', 'Situación'])

def process_pdf_with_ocr(pdf_file):
    """
    Procesa un archivo PDF utilizando OCR (Optical Character Recognition) para extraer texto de imágenes.

    Parameters:
        pdf_file (str): La ruta al archivo PDF a procesar.

    Returns:
        list: Una lista de textos extraídos de las imágenes en el PDF.
              Si ocurre un error durante el procesamiento, devuelve None.
    """
    try:
        # Convertir el PDF a imágenes usando pdf2image
        pages = convert_from_path(pdf_file)

        # Lista para almacenar los textos extraídos
        extracted_text_list = []

        # Procesar cada página de imagen con Tesseract OCR
        for i, page in enumerate(pages):
            # Extraer el texto de la imagen usando Tesseract OCR
            image_text = pytesseract.image_to_string(page)

            # Agregar el texto extraído a la lista
            extracted_text_list.append(image_text)

            # Procesar el texto extraído
            # (Aquí puedes agregar código para identificar y extraer información de las tablas
            # Dependiendo de la estructura del PDF, puede que necesites técnicas de procesamiento de texto adicionales)

            # Imprimir el texto extraído
            #print(f"Texto extraído de la página {i + 1} del archivo {pdf_file}:\n{image_text}\n")

        # Devolver la lista de textos extraídos
        return extracted_text_list
    except Exception as e:
        print(f"Error al procesar el archivo {pdf_file} con OCR: {e}")
        return None

def convert_date_format(fecha_str):
    """
    Convierte una fecha en formato "dd de mes de yyyy" a formato "dd/mm/yyyy".

    Parameters:
        fecha_str (str): La fecha en formato "dd de mes de yyyy".

    Returns:
        str: La fecha convertida en formato "dd/mm/yyyy".
    """
    # Establecer el idioma español para el formato de fecha
    locale.setlocale(locale.LC_TIME, 'es_ES')

    # Crear un objeto datetime a partir de la fecha en formato "dd de mes de yyyy"
    fecha_obj = datetime.datetime.strptime(fecha_str, "%d de %B de %Y")

    # Convertir la fecha a formato "dd/mm/yyyy"
    fecha_formato_deseado = fecha_obj.strftime("%d/%m/%Y")

    return fecha_formato_deseado

def find_referencia_in_text(text_list):
    """
    Busca referencias en una lista de texto utilizando patrones de expresión regular.

    Parameters:
        text_list (list of str): La lista de texto en la que se buscarán las referencias.

    Returns:
        list of str: Una lista de referencias encontradas en el texto.
    """
    # Patrones de expresión regular para buscar referencias
    pattern0 = r'N°\s+(\d{4}-\d{1}-\d{3})' 
    pattern2 = r'REFERENCIA:(.*?)(?:\n\n|$)' 
    pattern3 = r'(\d{4}-\d{1}-\d{3})'
    pattern1 = r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})'
    count_ref = 0
    
    the_patterns = [pattern0, pattern1, pattern2]
    
    # Lista para almacenar las referencias encontradas
    referencia_list = []

    # Buscar el patrón en el texto de la lista
    for text in text_list:
        for pa in the_patterns:   
            matches = re.findall(pa, text, re.DOTALL)
            referencia_list.extend(matches)

    # Procesar el texto para eliminar líneas adicionales y espacios en blanco
    processed_referencias = []
    for referencia in referencia_list:
        if re.match(pattern1, referencia):
            referencia = convert_date_format(referencia)
            processed_referencia = re.sub(r'\n', ' ', referencia)
            processed_referencia = re.sub(r'\s{2,}', ' ', referencia)
            processed_referencias.append(processed_referencia.strip())
        else:
            processed_referencia = referencia.replace("\n", " ")
            processed_referencia = re.sub(r'\n', '', processed_referencia)
            processed_referencia = re.sub(r'\s{2,}', ' ', processed_referencia)
            processed_referencias.append(processed_referencia.strip())

    for ref in processed_referencias:
        if re.match(pattern3, ref) and count_ref == 1:
            processed_referencias.remove(ref)
        count_ref += 1
    
    return processed_referencias

def are_tables_equal(table1, table2):
    """
    Compara dos tablas (listas de listas) para verificar si son iguales.

    Parameters:
        table1 (list of list): La primera tabla a comparar.
        table2 (list of list): La segunda tabla a comparar.

    Returns:
        bool: True si las tablas son iguales, False en caso contrario.
    """
    # Comprobar si las tablas tienen el mismo número de filas y columnas
    if len(table1) != len(table2) or len(table1[0]) != len(table2[0]):
        return False
    
    # Iterar a través de las filas y columnas de las tablas para comparar los valores
    for i in range(len(table1)):
        for j in range(len(table1[0])):
            if table1[i][j] != table2[i][j]:
                return False
    
    return True

def clean_double_row(df):
    """
    Limpia las filas duplicadas en un DataFrame al combinar valores de celdas con NaN.
    
    Parameters:
        df (DataFrame): El DataFrame a limpiar.
        
    Returns:
        DataFrame: El DataFrame limpiado con valores de celdas NaN combinados.
    """
    # Seleccionar filas con valores NaN en cualquier columna
    nan_rows = df[df.isna().any(axis=1)]

    # Calcular la proporción de valores no nulos por fila
    def calculate_completeness(row):
        non_null_count = row.count()
        total_columns = len(row)
        completeness = non_null_count / total_columns * 100
        return completeness

    # Aplicar la función a cada fila del DataFrame
    nan_rows.loc[:, 'Completeness'] = nan_rows.apply(calculate_completeness, axis=1)

    # Inicializar variables
    combined_rows = []
    current_combined_row = None

    # Iterar a través de las filas con valores NaN
    for index, row in nan_rows.iterrows():
        if current_combined_row is None or row['Completeness'] == 75:
            if current_combined_row is not None:
                combined_rows.append(current_combined_row)
            current_combined_row = row.copy()
        else:
            for col in df.columns:
                if pd.notna(row[col]):
                    if pd.notna(current_combined_row[col]):
                        current_combined_row[col] = current_combined_row[col] + ' ' + row[col]
                    else:
                        current_combined_row[col] = row[col]

    # Agregar la última fila combinada
    if current_combined_row is not None:
        combined_rows.append(current_combined_row)

    # Crear un DataFrame a partir de las filas combinadas
    combined_df = pd.DataFrame(combined_rows)

    while True:
        new_combined_rows = []
        current_combined_row = None
        for index, row in combined_df.iterrows():
            if current_combined_row is None or row['Completeness'] >= 75:
                if current_combined_row is not None:
                    new_combined_rows.append(current_combined_row)
                current_combined_row = row.copy()
            else:
                for col in df.columns:
                    if pd.notna(row[col]):
                        if pd.notna(current_combined_row[col]):
                            current_combined_row[col] = current_combined_row[col] + ' ' + row[col]
                        else:
                            current_combined_row[col] = row[col]
        if current_combined_row is not None:
            new_combined_rows.append(current_combined_row)
        if len(new_combined_rows) == len(combined_df):
            break
        combined_df = pd.DataFrame(new_combined_rows)
    combined_df = combined_df.drop(columns=["Completeness"])
    df = df.dropna()
    new_df = pd.concat([df, combined_df])
    
    return new_df

def change_headers(df):
    """
    Transforma un dataframe reemplazando los headers y agregando una nueva fila con los valores originales.
    
    Parameters:
        df (DataFrame): El dataframe a transformar.
        
    Returns:
        DataFrame: El dataframe transformado con nuevos headers y una fila con valores originales.
    """
    # Guardar los headers originales del dataframe
    original_headers = df.columns.tolist()
    
    # Verificar el número de columnas del dataframe
    num_columns = len(df.columns)
    
    # Crear una nueva fila con los valores originales
    original_values = df.values.tolist()
    original_values.append(original_headers)
    
    # Crear un nuevo dataframe con los valores originales en una nueva fila
    new_df = pd.DataFrame([original_values[0]], columns=original_headers)
    
    # Reemplazar los headers del dataframe según el número de columnas
    if num_columns == 5:
        new_headers = ['Doc. N°', 'Tipo', 'Rev.', 'Descripción', 'Situación']
    elif num_columns == 4:
        new_headers = ['Doc. N°', 'Tipo', 'Rev.', 'Descripcion']
    else:
        raise ValueError("El dataframe debe tener más 4 o 5 columnas")
    
    new_df.columns = new_headers
    
    # Agregar el resto de filas al nuevo dataframe
    new_df = pd.concat([new_df, pd.DataFrame(original_values[1:], columns=new_headers)], ignore_index=True)
    
    return new_df

def get_folder_names(path):
    """
    Obtiene una lista de nombres de carpetas dentro del directorio especificado.
    
    Parameters:
        path (str): Ruta del directorio a explorar.
    
    Returns:
        list: Lista de nombres de las carpetas dentro del directorio.
    """
    folder_names = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    return folder_names

def process_pdf_tables(pdf_file):
    """
    Procesa las tablas de un archivo PDF utilizando la biblioteca Tabula.

    Parameters:
        pdf_file (str): La ruta al archivo PDF a procesar.

    Returns:
        list: Lista de tablas objetivos ya limpias.
    """
    try:
        # Leer todas las páginas del PDF y extraer las tablas
        tables = tabula.read_pdf(pdf_file, pages='all', encoding='latin-1', lattice=False)

        # Patrón para identificar números de documento y encabezados de tablas
        pattern3 = r'^Doc\. N°$|^\d{3}-\d{5}-\d{3}$'

        # Variable para almacenar la primera tabla para comparar
        first_print = pd.DataFrame()
        targets_tables = []

        for table in tables:
            a = table
            first_header = a.columns[0]
            

            # Verificar si la tabla es diferente a la anterior y cumple con los patrones
            if (("Doc. N°" in first_header or re.match(pattern3, first_header) or "DOC. N°" in first_header) and not first_print.equals(table)):
                # Verificar si la tabla tiene celdas vacías
                if table.isna().any().any():
                    print(f"Tabla original con filas duplicadas:\n{table}")
                    clean_table = clean_double_row(table)  # Usar tu función clean_double_row
                    print(f"Tabla limpia:\n{clean_table}")
                    first_print = table
                    try:
                        clean_table.rename(columns={'DOC. N°': 'Doc. N°'})
                    except KeyError:
                        continue
                    targets_tables.append(clean_table)
                else:
                    try:
                        table.rename(columns={'DOC. N°': 'Doc. N°'})
                    except KeyError:
                        continue
                    print(table)
                    targets_tables.append(table)
        
        return targets_tables

    except Exception as e:
        print(f"Error al procesar el archivo {pdf_file} con Tabula: {e}")

def process_pdf_tables1(pdf_file):
    """
    Procesa las tablas de un archivo PDF utilizando la biblioteca Tabula y maneja los encabezados.

    Parameters:
        pdf_file (str): La ruta al archivo PDF a procesar.

    Returns:
        list: Lista de tablas objetivos ya limpias.
    """
    try:
        # Leer todas las páginas del PDF y extraer las tablas
        tables = tabula.read_pdf(pdf_file, pages='all', encoding='latin-1', lattice=True)
        print(f"Número de tablas encontradas: {len(tables)}")
        print("Información de las tablas:")
        targets_tables = []
        
        for table in tables:
            pattern3 = r'^\d{3}-\d{5}-\d{3}$'
            first_header = table.columns[0]
            
            # Verificar si el encabezado cumple con los patrones
            if "Doc. N°" in first_header or re.match(pattern3, first_header) or "DOC. N°" in first_header:
                if re.match(pattern3, first_header):
                    print("Procesando con cambio de encabezados:")
                    table = table.drop("Unnamed: 0", axis=1)
                    table = change_headers(table) 
                    try:
                        table.rename(columns={'DOC. N°': 'Doc. N°'})
                    except KeyError:
                        continue
                    print(table)  
                    targets_tables.append(table)
                else:
                    print("Procesando sin cambio de encabezados:")
                    table = table.drop("Unnamed: 0", axis=1)
                    try:
                        table.rename(columns={'DOC. N°': 'Doc. N°'})
                    except KeyError:
                        continue
                    print(table)
                    targets_tables.append(table)
        return targets_tables
    except Exception as e:
        print(f"Error al procesar el archivo {pdf_file} con Tabula: {e}")

def process_pdf_tables2(pdf_file):
    """
    Procesa las tablas de un archivo PDF utilizando la biblioteca Tabula y maneja los encabezados.

    Parameters:
        pdf_file (str): La ruta al archivo PDF a procesar.

    Returns:
        list: Lista de tablas objetivos ya limpias.
    """
    try:
        # Leer todas las páginas del PDF y extraer las tablas
        tables = tabula.read_pdf(pdf_file, pages='all', encoding='latin-1', lattice=True)
        print(f"Número de tablas encontradas: {len(tables)}")
        print("Información de las tablas:")
        target_tables = []
        
        for table in tables:
            pattern3 = r'^\d{3}-\d{5}-\d{3}$'
            first_header = table.columns[0]
            
            # Verificar si el encabezado cumple con los patrones
            if "Doc. N°" in first_header or re.match(pattern3, first_header) or "DOC. N°" in first_header:
                if re.match(pattern3, first_header):
                    print("Procesando con pattern3:")
                    print(table)
                    table.rename(columns={'DOC. N°': 'Doc. N°'})
                    target_tables.append(table)
                else:
                    print("Procesando sin pattern3:")
                    try:
                        table.rename(columns={'DOC. N°': 'Doc. N°'})
                    except KeyError:
                        continue    
                    print(table)
                    target_tables.append(table)
                              
        if len(target_tables) == 0:
            print("Utilizando 'lattice=True' se rompe todo, entonces uso 'lattice=False'")
            target_tables = process_pdf_tables(pdf_file)  # Llamar a tu función original
        return target_tables
    except Exception as e:
        print(f"Error al procesar el archivo {pdf_file} con Tabula: {e}")

def transform_situation(tablas, umbral_similitud=0.843):
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
        
        if tabla.shape[1] == 5:
            print(f"Se procedera a cambiar esta tabla en su serie 'Situacion'")
            quinta_columna = tabla.iloc[:, 4]
            for i, valor in enumerate(quinta_columna):
                nuevo_valor = transformar_valor(valor)
                quinta_columna[i] = nuevo_valor
            tablas_modificadas.append(tabla)
            print(f"Esta es la tabla cambiando su situacion \n{tabla}")
    return tablas_modificadas

def convert_to_final(df, valores):
    """
    Agrega nuevas columnas a un DataFrame utilizando una lista de datos.

    Parameters:
        df (pandas.DataFrame): El DataFrame al que se agregarán las nuevas columnas.
        valores (list): Lista de valores correspondientes a las nuevas columnas.
        df_base (pandas.DataFrame): El DataFrame final para seguimiento de todos los documentos.

    Returns:
        pandas.DataFrame: El DataFrame actualizado con las nuevas columnas.
    """
    recibidos_headers = ['Nº LO','Fecha']
    for i, columna_nueva in enumerate(recibidos_headers):
        df[columna_nueva] = valores[i]
    
    # Unir las dos primeras columnas con un "-" y almacenar el resultado en una nueva columna
    df['Doc. N°-Tipo'] = df[df.columns[0]].astype(str) + '-' + df[df.columns[1]]
    # Eliminar las dos primeras columnas
    df.drop([df.columns[0], df.columns[1]], axis=1, inplace=True)
    # Reordenar las columnas para que la nueva columna esté en primer lugar
    columnas = df.columns.tolist()
    columnas = ['Doc. N°-Tipo'] + columnas
    # Reemplazar el DataFrame original con las columnas reordenadas
    df = df[columnas]
    # Eliminar la última columna que contiene la concatenación
    df = df.iloc[:, :-1]  # Elimina la última columna
       
    

    return df

# OJO FALTA RESOLVER ESTA FUNCION PARA OBTENER TABLA FINAL CON DATOS DE RESPUESTA
def append_LO_respuesta(df, valores):
    """
    Agrega nuevas columnas a un DataFrame utilizando una lista de datos.

    Parameters:
        data_list (list): Lista de nombres de columnas a agregar.
        df (pandas.DataFrame): El DataFrame al que se agregarán las nuevas columnas.
        valores (list): Lista de valores correspondientes a las nuevas columnas.

    Returns:
        pandas.DataFrame: El DataFrame actualizado con las nuevas columnas.
    """
    recibidos_headers = ['Nº LO','Fecha']
    for i, columna_nueva in enumerate(recibidos_headers):
        df[columna_nueva] = valores[i]
    
def renombrar_archivos_pdf_recibidos(dataframe, path):
    """
    Renombra archivos PDF en un directorio según los valores de un DataFrame.

    Args:
        dataframe (pd.DataFrame): El DataFrame que contiene los valores a partir de los cuales se generarán los nuevos nombres.
        path (str): La ruta al directorio que contiene los archivos PDF a renombrar.

    Returns:
        None

    """
    # Obtener una lista de archivos PDF en el directorio
    archivos_pdf = [archivo for archivo in os.listdir(path) if archivo.endswith('.pdf')]

    # Recorrer cada fila del DataFrame
    for indice, fila in dataframe.iterrows():
        # Obtener el valor de la primera columna
        primer_valor = str(fila[0])[:19]  # Tomar los primeros 19 caracteres
        #print(f"Estos son los primeros 19 caracteres: {primer_valor}")

        # Buscar un archivo PDF que coincida con el valor
        archivo_encontrado = None
        for archivo_pdf in archivos_pdf:
            if primer_valor in archivo_pdf:
                archivo_encontrado = archivo_pdf
                break

        if archivo_encontrado:
           # Renombrar el archivo PDF con la concatenación de los primeros tres valores de la fila
            nuevo_nombre = '-'.join(str(valor) for valor in fila[:3])
            nuevo_nombre = nuevo_nombre.replace('/', '-')  # Reemplazar barras por guiones
            nuevo_nombre = nuevo_nombre.replace('\r', ' ')
            nuevo_nombre = nuevo_nombre[:255]  # Limitar el nombre a 255 caracteres (sistema de archivos)

            
            # Ruta completa del archivo antiguo y nuevo
            archivo_antiguo = os.path.join(path, archivo_encontrado)
            archivo_nuevo = os.path.join(path, f'{nuevo_nombre}.pdf')

            # Renombrar el archivo
            os.rename(archivo_antiguo, archivo_nuevo)
            print(f"Renombrado: {archivo_antiguo} -> {archivo_nuevo}")
        else:
            print(f"No se encontró un archivo para: {primer_valor}")

def renombrar_archivos_pdf_respuestas(dataframe, path):
    """
    Renombra archivos PDF en un directorio según los valores de un DataFrame.

    Args:
        dataframe (pd.DataFrame): El DataFrame que contiene los valores a partir de los cuales se generarán los nuevos nombres.
        path (str): La ruta al directorio que contiene los archivos PDF a renombrar.

    Returns:
        None

    """
    # Obtener una lista de archivos PDF en el directorio
    archivos_pdf = [archivo for archivo in os.listdir(path) if archivo.endswith('.pdf')]

    # Recorrer cada fila del DataFrame
    for indice, fila in dataframe.iterrows():
        # Obtener el valor de la primera columna
        primer_valor = str(fila[0])[:19]  # Tomar los primeros 19 caracteres
        #print(f"Estos son los primeros 19 caracteres: {primer_valor}")

        # Buscar un archivo PDF que coincida con el valor
        archivo_encontrado = None
        for archivo_pdf in archivos_pdf:
            if primer_valor in archivo_pdf:
                archivo_encontrado = archivo_pdf
                break

        if archivo_encontrado:
           # Renombrar el archivo PDF con la concatenación de los primeros tres valores de la fila
            nuevo_nombre = '-'.join(str(valor) for valor in fila[:4])
            nuevo_nombre = nuevo_nombre.replace('/', '-')  # Reemplazar barras por guiones
            nuevo_nombre = nuevo_nombre.replace('\r', ' ')
            nuevo_nombre = nuevo_nombre[:255]  # Limitar el nombre a 255 caracteres (sistema de archivos)

            
            # Ruta completa del archivo antiguo y nuevo
            archivo_antiguo = os.path.join(path, archivo_encontrado)
            archivo_nuevo = os.path.join(path, f'{nuevo_nombre}.pdf')

            # Renombrar el archivo
            os.rename(archivo_antiguo, archivo_nuevo)
            print(f"Renombrado: {archivo_antiguo} -> {archivo_nuevo}")
        else:
            print(f"No se encontró un archivo para: {primer_valor}")


def start():
    global DF_BASE
    # utiliza funcion para una lista con los nombres de las carpetas en el path seleccionado
    start_time = time.time()  # Marca el tiempo de inicio
    try:
        folder_names = get_folder_names(selected_directory)
    
        # Iterar a través de las carpetas y buscar todos los archivos PDF 
        for folder_name in folder_names:
            folder_path = os.path.join(selected_directory, folder_name)
            pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))

            # iterea a traves de cada archivo pdf y realiza ciertas taraea con c/u
            for pdf_file in pdf_files:
                file_name = os.path.basename(pdf_file)
                
                # toma todos los archivos con 1561, los objetivos son LO recibidos y respuestas asi como NOTAS
                if re.search(r"1561", file_name) and "LOP" not in file_name:
                    print("------------------------------------------------------------------------------------------")
                    print(f"estoy considerando que 1561 esta en {file_name}")

                    
                    # aqui entra el LO de recibidos 
                    if file_name.startswith("LO"):
                        #print("---Proceso A---")                    
                        print(f"Archivo: {file_name} - Procesando con OCR:")
                        info_LO = find_referencia_in_text(process_pdf_with_ocr(pdf_file))
                        print(info_LO)                   
                        
                    
                    else:
                        #aca entra la nota ya sea de LT o SE
                        if file_name.startswith("OT") or file_name.startswith("NOTA"):
                            # Si el archivo no contiene "LO" en su nombre, obtener y mostrar los datos de las tablas dentro del PDF usando tabula
                            #print(f"este esel file name: {file_name}")                        
                            try:
                               target_tables = process_pdf_tables2(pdf_file)
                               #transform_situation(target_tables)
                               if file_name.startswith("OT"):
                                    # Aplicar las mismas transformaciones al nombre del archivo
                                    file_name_new = pdf_file.replace("OT", "NOTA LIC OT ")
                                    os.rename(pdf_file, file_name_new)
                                    #print(f"supuestamente se cambio a {os.path.basename(file_name_new)}")
                               else:
                                    print("supuestamente no comienza con OT")
                               

                            except Exception as e:
                                print(f"Error al leer las tablas del archivo en la seccion A {file_name}: {e}")
                            


                        # aca entra el LO de respuesta
                        elif file_name.startswith("1561"):
                            print(f"Archivo: {file_name} - Procesando con OCR:")
                            #print(process_pdf_with_ocr(pdf_file))
                            info_LO = find_referencia_in_text(process_pdf_with_ocr(pdf_file))
                            print(info_LO)
                            
                            try:
                                
                                target_tables = process_pdf_tables1(pdf_file)
                                target_tables = transform_situation(target_tables)

                            except Exception as e:
                                print(f"Error al leer las tablas del archivo en la seccion B {file_name}: {e}")
        
            # en esta indentacion tengo que modificar lo extraido para obtener tabla final
            df_final = pd.concat(target_tables, axis=0)
            info_LO = info_LO[:2]

            #if len(df_final.columns) == 4:
            df_final = convert_to_final(df_final,info_LO)
            print(f"esta es la tabla final unificada:\n{df_final}")
            print(df_final['Rev.'].dtype)

            # AQUI REDACTAR EL CODIGO PARA RENOMBRAR CADA ARCHIVO EN EL DIRECTORIO ACTUAL
            if len(df_final.columns) == 5:
                renombrar_archivos_pdf_recibidos(df_final, folder_path)
            else:
                renombrar_archivos_pdf_respuestas(df_final, folder_path)
            
            # ESTA ES LA LINEA DE CODIGO PARA CONVERTIR LA SERIE 'Rev.' a integer 
            df_final['Rev.'] = pd.to_numeric(df_final['Rev.'], errors='coerce')
            #DF_BASE = pd.concat([DF_BASE, df_final], ignore_index=True)
            print(df_final['Rev.'].dtype)

    except Exception as e:
        print(f"Ningún directorio seleccionado o {e}")
    
    end_time = time.time()  # Marca el tiempo de finalización
    elapsed_time = end_time - start_time
    print("Tiempo transcurrido:", elapsed_time, "segundos")

def get_source():
    global selected_directory  # Accede a la variable global
    selected_directory = askdirectory()
    text = tk.Label(text=selected_directory)
    text.pack()


# Crear una nueva ventana utilizando la biblioteca tkinter
window = tk.Tk()
window.title("L1")
window.iconbitmap(default="icons8-compare-50.ico")
window.minsize(width=650, height=600)

# Crear un lienzo en la ventana para mostrar una imagen
canvas = tk.Canvas(width=150, height=200)
img = tk.PhotoImage(file="L1_cmix.png")
img = img.subsample(8, 8)
canvas.create_image(75, 100, image=img)
canvas.pack()


# Crear un botón en la ventana para seleccionar el directorio
button1 = tk.Button(text="Source 📁", command=get_source)
button1.pack()

button2 = tk.Button(text="Start", command=start)
button2.pack()


# Iniciar el bucle principal de la ventana
window.mainloop()
