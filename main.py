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
                if "LO" in file_name:
                    # Si el archivo contiene "LO" en su nombre, procesarlo con OCR usando la función process_pdf_with_ocr
                    print(f"Archivo: {file_name} - Procesando con OCR:")
                    print(find_referencia_in_text(process_pdf_with_ocr(pdf_file)))
                    #print(process_pdf_with_ocr(pdf_file))
                    
                #poner elif para tomar tablas de los documentos con "OT"
                else:
                    if re.search(r"OT", file_name): #and re.search(r"\bNOTA\b(?!\d)", file_name):
                        # Si el archivo no contiene "LO" en su nombre, obtener y mostrar los datos de las tablas dentro del PDF usando tabula
                        #print(f"Archivo: {pdf_file}")
                        
                        try:
                            tables = tabula.read_pdf(pdf_file, pages='all', encoding='latin-1', lattice=True)
                            print(len(tables))
                            print("Información de las tablas:")
                            target_tables = []
                            for table in tables:
                                pattern3 = r'^Doc\. N°$|^\d{3}-\d{5}-\d{3}$'
                                first_header = table.columns[0]
                                #print(table)
                                
                                #print(table.columns[0])
                                if "Doc. N°" in first_header or re.match(pattern3, first_header) or "DOC. N°" in first_header:
                                    #agregar otro if table = table.drop("Unnamed: 0", axis=1)
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
                                        print(table)
                                        #print(type(table))
                                        first_print = table
                                        #print(first_print.equals(table))

                        except Exception as e:
                            print(f"Error al leer las tablas del archivo {file_name}: {e}")
                    else:
                        print(f"Archivo: {file_name} - Procesando con OCR:")
                        #print(process_pdf_with_ocr(pdf_file))
                        print(find_referencia_in_text(process_pdf_with_ocr(pdf_file)))
                        
                        try:
                            tables = tabula.read_pdf(pdf_file, pages='all', encoding='latin-1', lattice=True)
                            print(len(tables))
                            print("Información de las tablas:")
                            for table in tables:
                                pattern3 = r'^Doc\. N°$|^\d{3}-\d{5}-\d{3}$'
                                first_header = table.columns[0]
                                #print(table)
                                
                                if "Doc. N°" in first_header or re.match(pattern3, first_header) or "DOC. N°" in first_header:
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
