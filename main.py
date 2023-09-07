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
        new_headers = ['Doc. N°', 'Tipo', 'Rev.', 'Descripcion', 'Situacion']
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
                    targets_tables.append(clean_table)
                else:
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
                    print(table)  
                    targets_tables.append(table)
                else:
                    print("Procesando sin cambio de encabezados:")
                    table = table.drop("Unnamed: 0", axis=1)
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
                    target_tables.append(table)
                else:
                    print("Procesando sin pattern3:")
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
        print(f"Esta es la tabla sin cambiar su situacion \n{tabla}")
        if tabla.shape[1] == 5:
            quinta_columna = tabla.iloc[:, 4]
            for i, valor in enumerate(quinta_columna):
                nuevo_valor = transformar_valor(valor)
                quinta_columna[i] = nuevo_valor
            tablas_modificadas.append(tabla)
        print(f"Esta es la tabla cambiando su situacion \n{tabla}")
    return tablas_modificadas

def start():
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
                
                # toma los archivos que contengan el numero 1561 en su nombre y no tengan LOP
                if re.search(r"1561", file_name) and "LOP" not in file_name:
                    print("------------------------------------------------------------------------------------------")
                    print(f"estoy considerando que 1561 esta en {file_name}")
                    
                    # trabaja sobre el archivo con LO en su nombre #
                    if file_name.startswith("LO"):
                        #print("---Proceso A---")                    
                        print(f"Archivo: {file_name} - Procesando con OCR:")
                        print(find_referencia_in_text(process_pdf_with_ocr(pdf_file)))                   
                        
                    
                    else:
                        if file_name.startswith("OT") or file_name.startswith("NOTA"):
                            # Si el archivo no contiene "LO" en su nombre, obtener y mostrar los datos de las tablas dentro del PDF usando tabula
                                                    
                            try:
                               target_tables = process_pdf_tables2(pdf_file)

                            except Exception as e:
                                print(f"Error al leer las tablas del archivo en la seccion A {file_name}: {e}")
                    
                        elif file_name.startswith("1561"):
                            print(f"Archivo: {file_name} - Procesando con OCR:")
                            #print(process_pdf_with_ocr(pdf_file))
                            print(find_referencia_in_text(process_pdf_with_ocr(pdf_file)))
                            
                            try:
                                target_tables = process_pdf_tables1(pdf_file)

                            except Exception as e:
                                print(f"Error al leer las tablas del archivo en la seccion B {file_name}: {e}")
    except Exception as e:
        print("Ningún directorio seleccionado")
    
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
