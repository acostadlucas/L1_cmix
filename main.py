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
pd.options.mode.chained_assignment = None

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

# Función para procesar el archivo PDF con Tesseract OCR
def process_pdf_with_ocr(pdf_file):
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

def convert_fecha_format(fecha_str):
    # Establecer el idioma español para el formato de fecha
    locale.setlocale(locale.LC_TIME, 'es_ES')

    # Crear un objeto datetime a partir de la fecha en formato "dd de mes de yyyy"
    fecha_obj = datetime.datetime.strptime(fecha_str, "%d de %B de %Y")

    # Convertir la fecha a formato "dd/mm/yyyy"
    fecha_formato_deseado = fecha_obj.strftime("%d/%m/%Y")

    return fecha_formato_deseado

def find_referencia_in_text(text_list):
    # Expresión regular para buscar el texto entre "REFERENCIA:" y la primera doble línea "\n\n"
    pattern0 = r'N°\s+(\d{4}-\d{1}-\d{3})' 
    pattern2 = r'REFERENCIA:(.*?)(?:\n\n|$)' 
    pattern3 = r'(\d{4}-\d{1}-\d{3})'
    pattern1 = r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})'
    count_ref = 0
    
    the_patterns =[pattern0, pattern1, pattern2]
    # Lista para almacenar las referencias encontradas
    referencia_list = []

    # Buscar el patrón en el único texto de la lista
    for text in text_list:
        for pa in the_patterns:   
            matches = re.findall(pa, text, re.DOTALL)
            referencia_list.extend(matches)

    # Procesar el texto para eliminar las líneas adicionales "\n"
    processed_referencias = []
    for referencia in referencia_list:
        if re.match(pattern1, referencia):
            referencia = convert_fecha_format(referencia)
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
        
    
    return(processed_referencias)

def are_tables_equal(table1, table2):
    if len(table1) != len(table2) or len(table1[0]) != len(table2[0]):
        return False
    
    for i in range(len(table1)):
        for j in range(len(table1[0])):
            if table1[i][j] != table2[i][j]:
                return False
    
    return True

def clean_double_row(df):
    # Select rows with NaN values in any column
    nan_rows = df[df.isna().any(axis=1)]

    # Calculate the proportion of non-null values per row
    def calculate_completeness(row):
        non_null_count = row.count()
        total_columns = len(row)
        completeness = non_null_count / total_columns * 100
        return completeness

    # Apply the function to each row of the DataFrame
    nan_rows.loc[:, 'Completeness'] = nan_rows.apply(calculate_completeness, axis=1)

    # Initialize variables
    combined_rows = []
    current_combined_row = None

    # Iterate through nan_rows
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

    # Append the last combined row
    if current_combined_row is not None:
        combined_rows.append(current_combined_row)

    # Create a DataFrame from the combined rows
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
    # Guardar los headers originales del dataframe
    original_headers = df.columns.tolist()
    #print(f"estos son los valores originales en el header:\n{original_headers}")
    
    # Verificar el número de columnas del dataframe
    num_columns = len(df.columns)
    
    # Crear una nueva fila con los valores originales
    original_values = df.values.tolist()
    original_values.append(original_headers)  # Usamos append() en lugar de extend()
    #print(original_values)
    
    # Crear un nuevo dataframe con los valores originales en una nueva fila
    new_df = pd.DataFrame([original_values[0]], columns=original_headers)
    #print(f"y esto tb quiero ver:\n{new_df}")
    
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

def get_source():
    global path
    path = p.Path(askdirectory())
    text = tk.Label(text=path)
    text.pack()

    # Obtener una lista de nombres de carpetas dentro del directorio seleccionado
    folder_names = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    print("Lista de nombres de carpetas dentro del directorio:")
    print(folder_names)
    first_print = pd.DataFrame()

    # Iterar a través de las carpetas y buscar archivos PDF que cumplan con ciertas condiciones
    for folder_name in folder_names:
        folder_path = os.path.join(path, folder_name)
        pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))

        # Filtrar archivos PDF por nombre utilizando expresiones regulares y otras condiciones
        #print(f"\nEncontrados los siguientes archivos PDF en '{folder_name}' con el número '1561':")
        #print(pdf_files)
        
        for pdf_file in pdf_files:
            file_name = os.path.basename(pdf_file)
            
            if re.search(r"1561", file_name) and "LOP" not in file_name:
                print("------------------------------------------------------------------------------------------")
                print(f"estoy considerando que 1561 esta en {file_name}")
                # AQUI SE OBTIENE EL NUMERO DE LO DEL RECIBIDO, SU FECHA Y REFERENCIA #
                if file_name.startswith("LO"):
                    #print("ESTA ENTRANDO ACA")
                    # Si el archivo contiene "LO" en su nombre, procesarlo con OCR usando la función process_pdf_with_ocr
                    print(f"Archivo: {file_name} - Procesando con OCR:")
                    print(find_referencia_in_text(process_pdf_with_ocr(pdf_file)))
                    #print(process_pdf_with_ocr(pdf_file))
                    
                #poner elif para tomar tablas de los documentos con "OT"
                else:
                    if file_name.startswith("OT") or file_name.startswith("NOTA"):
                        # Si el archivo no contiene "LO" en su nombre, obtener y mostrar los datos de las tablas dentro del PDF usando tabula
                        #print(f"Archivo: {pdf_file}")
                        
                        try:
                            tables = tabula.read_pdf(pdf_file, pages='all', encoding='latin-1', lattice=True)
                            print(len(tables))
                            print("Información de las tablas:")
                            target_tables = []
                            for table in tables:
                                pattern3 = r'^\d{3}-\d{5}-\d{3}$'
                                first_header = table.columns[0]
                                #print(table)
                                
                                #print(table.columns[0])
                                if "Doc. N°" in first_header or re.match(pattern3, first_header) or "DOC. N°" in first_header:
                                    if re.match(pattern3, first_header):
                                        print("que paso aca si es que tiene pattern3")
                                        print(table)

                                    #agregar otro if table = table.drop("Unnamed: 0", axis=1)
                                    else:
                                        print(" no se esta considerando el  pattern3")
                                        print(table)
                                    
                                    target_tables.append(table)
                                    #print(table.columns[0])
                                #print(f"Tabla {i + 1}:\n{table}\n")
                                
                            if len(target_tables) == 0:
                                print("Utilizando 'lattice=True' se rompe todo entonces uso 'lattice=False'")
                                tables = tabula.read_pdf(pdf_file, pages='all', encoding='latin-1', lattice=False)
                                #first_print = pd.DataFrame()
                                pattern3 = r'^Doc\. N°$|^\d{3}-\d{5}-\d{3}$'
                                for table in tables:
                                    #print(table)
                                    a = table
                                    first_header = a.columns[0]
                                    #print(first_print.equals(a))                                     
                                    if (("Doc. N°" in first_header or re.match(pattern3, first_header) or "DOC. N°" in first_header) and first_print.equals(table) == False):
                                        #agregar otro if table = table.drop("Unnamed: 0", axis=1)   
                                        if table.isna().any().any():
                                            print(f"esta es la tabla original que se rompe por doble fila\n{table}")
                                            clean_table = clean_double_row(table)
                                            print(f"esta es la tabla limpia \n{clean_table}")
                                            #print(type(table))
                                            first_print = table
                                        else:
                                            print(table)
                                        #print(first_print.equals(table))

                        except Exception as e:
                            print(f"Error al leer las tablas del archivo {file_name}: {e}")
                    elif file_name.startswith("1561"):
                        print(f"Archivo: {file_name} - Procesando con OCR:")
                        #print(process_pdf_with_ocr(pdf_file))
                        print(find_referencia_in_text(process_pdf_with_ocr(pdf_file)))
                        
                        try:
                            tables = tabula.read_pdf(pdf_file, pages='all', encoding='latin-1', lattice=True)
                            print(len(tables))
                            print("Información de las tablas:")
                            for table in tables:
                                pattern3 = r'^\d{3}-\d{5}-\d{3}$'
                                first_header = table.columns[0]
                                #print(table)
                                
                                if "Doc. N°" in first_header or re.match(pattern3, first_header) or "DOC. N°" in first_header:
                                    
                                    if re.match(pattern3, first_header):
                                        print("aca")
                                        table = table.drop("Unnamed: 0", axis=1)
                                        print(change_headers(table))
                                    else:
                                        print("OOOOOOOO ACA")
                                        table = table.drop("Unnamed: 0", axis=1)
                                        print(table)
                                        

                                    #print(table[1])
                                #print(f"Tabla {i + 1}:\n{table}\n")
                        except Exception as e:
                            print(f"Error al leer las tablas del archivo {file_name}: {e}")

# Crear un botón en la ventana para seleccionar el directorio
button = tk.Button(text="Source 📁", command=get_source)
button.pack()

# Iniciar el bucle principal de la ventana
window.mainloop()
