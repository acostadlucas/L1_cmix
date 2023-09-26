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
import csv
import openpyxl
pd.options.mode.chained_assignment = None


DIRECTORIO = "C:\\Users\\lucas\\Downloads\\Recibidos y respuestas"
ABS_DIRECTORY = os.path.abspath(DIRECTORIO)
TARGET = "229-26110-001"
#target_prove = "72102201-016"
#directory_prove = os.path.abspath("C:\\Users\\lucas\\Downloads\\pruebaBusquedaLO")
count = 0 
start_time = time.time()

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
    # Patrón de expresión regular para buscar el formato de fecha esperado
    pattern = r'(\d{1,2}) de (\w+) de (\d{4})'

    # Buscar una coincidencia en el formato esperado
    match = re.search(pattern, fecha_str)

    if match:
        # Extraer los componentes de la fecha
        dia, mes, anio = match.groups()

        # Mapear nombres de meses en español a nombres en inglés
        meses_esp_to_eng = {
            'enero': 'January',
            'febrero': 'February',
            'marzo': 'March',
            'abril': 'April',
            'mayo': 'May',
            'junio': 'June',
            'julio': 'July',
            'agosto': 'August',
            'setiembre': 'September',
            'octubre': 'October',
            'noviembre': 'November',
            'diciembre': 'December'
        }

        # Reemplazar nombres de meses en español con nombres en inglés
        mes = meses_esp_to_eng.get(mes.lower(), mes)

        # Crear un objeto datetime
        fecha_obj = datetime.datetime.strptime(f"{dia} {mes} {anio}", "%d %B %Y")

        # Convertir la fecha a formato "dd/mm/yyyy"
        fecha_formato_deseado = fecha_obj.strftime("%d/%m/%Y")

        return fecha_formato_deseado

    else:
        return fecha_str  

def find_referencia_in_text(text_list, target, directory):
    """
    Busca referencias en una lista de texto utilizando patrones de expresión regular.

    Parameters:
        text_list (list of str): La lista de texto en la que se buscarán las referencias.
        target (str): Hilo de caracteres a buscar dentro de los archivos.
        directory(str): hilo de caracteres que pertenese al path del archivo sobre el que se esta trabajando.

    Returns:
        none.
        En su lugar imprime el nombre del archivo tomado si el target se encuentra en el.
    """

    for text in text_list:
        if target in text:
            print(f"{TARGET} ubicado en: {os.path.basename(directory)}")
        
def list_LO(directorio):
    """
    Toma un directorio y devuelve una lista con el path de cada archivo PDF dentro del directorio.
    """
    archivos_pdf = []
    
    # Usamos glob para buscar archivos PDF en el directorio
    archivos_pdf.extend(glob.glob(os.path.join(directorio, "*.pdf")))
    
    return archivos_pdf


for LO in list_LO(ABS_DIRECTORY):
    count += 1
    text_in_LO = process_pdf_with_ocr(LO)
    find_referencia_in_text(text_in_LO, TARGET,LO)

    
print(count)
end_time = time.time()  # Marca el tiempo de finalización
elapsed_time = end_time - start_time
print("Tiempo transcurrido:", elapsed_time, "segundos")