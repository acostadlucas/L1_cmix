""" import re
import datetime
import locale

def convert_fecha_format(fecha_str):
    # Establecer el idioma español para el formato de fecha
    locale.setlocale(locale.LC_TIME, 'es_ES')

    # Crear un objeto datetime a partir de la fecha en formato "dd de mes de yyyy"
    fecha_obj = datetime.datetime.strptime(fecha_str, "%d de %B de %Y")

    # Convertir la fecha a formato "dd/mm/yyyy"
    fecha_formato_deseado = fecha_obj.strftime("%d/%m/%Y")

    return fecha_formato_deseado


a = ['N° 1561-1-872\nfeces\n\nCONTRATO\nN°:8394/2021\n\nConsorcio San\n\nLICITACION: 1561/2020 José\n\nLOTE N°: 1\n\nDESCRIPCION DE LA OBRA: “Proyecto de Construccién e Interconexién de la\nSubestacion Valenzuela 500 kV”\n\nLUGAR Y FECHA: DE: A:\n24 de Julio de 2023 Contratista ANDE (GT/CSI)\n\nREFERENCIA: CIVIL - PATIO — Estructura soporte trampa de onda y\ndescargador de transformador de 500kV y 220kV\n\nDe nuestra mayor consideraci6n:\n\nNos dirigimos a Ud., con el objeto de hacer entrega de 2 copias de los siguientes documentos\npara su aprobaci6n en respuesta a observaciones nota 1561-1-765 y 1561-1-859:\n\nDoc. N° Tipo | Rev. | Descripcién\n\n229-23100-002 PL 02 | Estructura soporte trampa de onda SOOkV\n229-23100-002 | MC | 02 | Memoria de calculo - Estructura soporte trampa de onda 500kV\n\n|_229-23106-002 PL 02 | Estructura soportes descargador de transformador 5O00kV\nMemoria de calculo - Estructura soportes descargador de\ntransformador 500kV\n\n229-23206-001 | PL 02 | Estructura soportes descargador 220kV\n\n229-23106-002 | MC | 02\n\n229-23206-001 | MC | 02 | Memoria de calculo - Estructura soportes descargador 220kV\n\nAtentamente,\n\nCONSORCIO SAN JOSE SA\n\na\ney\nLAD\nSTR. .\n= sl\naX\n']
#a = [1,2,3]

def find_nro_in_text(text_list):
    # Expresión regular para buscar "N°" seguido de 11 caracteres numéricos
    pattern = r'N°\s+(\d{4}-\d{1}-\d{3})'
    pattern2 = r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})'
    pattern3 = r'REFERENCIA:(.*?)(?=\n\n)'

    # Lista para almacenar los números encontrados
    nro_list = []

    # Buscar el patrón en el único texto de la lista
    for text in text_list:
        matches = re.findall(pattern3, text)
        nro_list.extend(matches)

    return(nro_list)


def find_referencia_in_text(text_list):
    # Expresión regular para buscar el texto entre "REFERENCIA:" y la primera doble línea "\n\n"
    pattern2 = r'REFERENCIA:(.*?)(?:\n\n|$)'
    pattern0 = r'N°\s+(\d{4}-\d{1}-\d{3})'
    pattern1 = r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})'
    the_patterns =[pattern0, pattern1, pattern2]
    # Lista para almacenar las referencias encontradas
    referencia_list = []

    # Buscar el patrón en el único texto de la lista
    for text in text_list:
        for pa in the_patterns:
            matches = re.findall(pa, text, re.DOTALL)
            referencia_list.extend(matches)

    # Procesar el texto para eliminar las líneas adicionales "\n"
    print(referencia_list)
    processed_referencias = []
    for referencia in referencia_list:
        if re.match(pattern1, referencia):
            referencia = convert_fecha_format(referencia)
            processed_referencia = re.sub(r'\n', ' ', referencia)
            processed_referencia = re.sub(r'\s{2,}', ' ', referencia)
            processed_referencias.append(processed_referencia.strip())
        else:
            processed_referencia = str(referencia).replace("\n", " ")
            processed_referencia = re.sub(r'\n', ' ', processed_referencia)
            processed_referencia = re.sub(r'\s{2,}', ' ', processed_referencia)
            processed_referencias.append(processed_referencia.strip())
        

    return(processed_referencias)


#print(find_nro_in_text(a))
#print(find_nro_in_text(a))
print(find_referencia_in_text(a))
#fecha_convertida = convert_fecha_format(find_nro_in_text(a)[0])
#print(fecha_convertida)
 """

""" import win32com.client as win32

def convert_to_pdf(word_file, pdf_file):
    word = win32.Dispatch('Word.Application')
    doc = word.Documents.Open(word_file)
    doc.SaveAs(pdf_file, FileFormat=17)
    doc.Close()  # Cerrar el documento
    word.Quit()  # Cerrar la instancia de Word

word_file = "C:\\Users\\Lucas Acosta\\Downloads\\ejemploH\\687 - Proyecto Civil y Electromecánico LT\\LOP 1561-X-X.docx"
pdf_file = "C:\\Users\\Lucas Acosta\\Downloads\\ejemploH\\687 - Proyecto Civil y Electromecánico LT\\LO 1561-X-X.pdf"
convert_to_pdf(word_file, pdf_file)

print("go go power rangers") """


""" import tabula
import pandas as pd
import re

pdf_file = "C:\\Users\\Lucas Acosta\\Downloads\\ejemploI\\683 - Suministro LT - Resultados ensayos FAT Aisladores de vidrio RUITAI\\NOTA LIC OT 1561-683-23 Suministro LT - Resultados Ensayos FAT Aisladores de Vidrio Ruitai.pdf"
pattern3 = r'^Doc\. N°$|^\d{3}-\d{5}-\d{3}$'
tables = tabula.read_pdf(pdf_file, pages='all', encoding='latin-1', lattice=False)
first_print = pd.DataFrame()

for table in tables:
    first_header = table.columns[0]
    #print(first_print.equals(table))
    
    if (("Doc. N°" in first_header or re.match(pattern3, first_header) or "DOC. N°" in first_header) and 
        not first_print.equals(table)):
        print(table)
        first_print = table
 """


############################################################# ALGORITMO QUE UNIFICA LOS DATOS DE LAS COLUMNAS EN UNA SOLA ###################################################################
# LA IDEA ES CONVERTIR MUCHAS FILAS EN UNA SOLA 
 
""" import pandas as pd
import numpy as np

data = {
    'Col1': ["M-2000-36140-001", np.nan, "-", np.nan],
    'Col2': ["PL", "-", np.nan, np.nan],
    'Col3': ["00", "-", np.nan, np.nan],
    'Col4': ["Puesta tierra en suelo Rocoso", "Protocolos de resistividad - Seccionamiento LT", np.nan, "VHA"]
}

df = pd.DataFrame(data)

print(f"esta es la tabla a trabajar:\n{df}")

# Select rows with NaN values in any column
nan_rows = df[df.isna().any(axis=1)]


print(f"esta es la tabla compuesta unicamente de NaN:\n{nan_rows}")

# Llenar NaN y elementos no NaN juntos en cada columna
df_filled = {col: ' '.join(map(str, nan_rows[col].dropna())) for col in nan_rows.columns}

# Create a new DataFrame with the joined values
result_df = pd.DataFrame([df_filled])
print(result_df) """


################################################################# ALGORITMO QUE CALCULA LA PROPORCION DE COMPLITUD DE CADA FILA #################################################################

""" import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None

data = {
    'Col1': ["M-2000-36140-001", np.nan, "-", np.nan],
    'Col2': ["PL", "-", np.nan, np.nan],
    'Col3': ["00", "-", np.nan, np.nan],
    'Col4': ["Puesta tierra en suelo Rocoso", "Protocolos de resistividad - Seccionamiento LT", np.nan, "VHA"]
}

df = pd.DataFrame(data)

print(f"esta es la tabla a trabajar:\n{df}")

# Select rows with NaN values in any column
nan_rows = df[df.isna().any(axis=1)]

# Calcular la proporción de valores no nulos por fila
def calculate_completeness(row):
    non_null_count = row.count()
    total_columns = len(row)
    completeness = non_null_count / total_columns * 100
    return completeness

# Aplicar la función a cada fila del DataFrame
nan_rows.loc[:, 'Completeness'] = nan_rows.apply(calculate_completeness, axis=1)


print(f"esta es la tabla a final con porcentajes:\n{nan_rows}")
 """

###################################################################################################

""" import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None

data = {
    'Col1': ["M-2000-36140-001", np.nan, "-", np.nan, "L", np.nan],
    'Col2': ["PL", "-", np.nan, np.nan, "u", np.nan],
    'Col3': ["00", "-", np.nan, np.nan, "k's", np.nan],
    'Col4': ["Puesta tierra en suelo Rocoso", "Protocolos de resistividad - Seccionamiento LT", np.nan, "VHA", np.nan, "PURETE"]
}

df = pd.DataFrame(data)

print(f"This is the original DataFrame:\n{df}")

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

print(f"This is the DataFrame with NaN and percentage:\n{nan_rows}")

# Threshold for combining rows based on Completeness
threshold = 75

# Combine rows based on Completeness threshold
combined_rows = []
current_combined_row = nan_rows.iloc[0]
print(f"este no se que es pero es:\n{current_combined_row}")
for index, row in nan_rows.iterrows():
    print(f"what tha row: \n{row}")
    if row['Completeness'] < threshold:
        if current_combined_row['Completeness'] is not threshold:
            current_combined_row = current_combined_row.combine_first(row)
        else:
            combined_rows.append(current_combined_row)
            current_combined_row = row
    else:
        combined_rows.append(current_combined_row)
        current_combined_row = row
combined_rows.append(current_combined_row)

# Create a DataFrame from the combined rows
combined_df = pd.DataFrame(combined_rows)

print(f"This is the final combined DataFrame:\n{combined_df}")
 """


########################################################################7
# une filas que se separan por tener una tabla con filas que poseen doble renglon
# BIEN

import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None

data = {
    'Col1': ["M-2000-36140-001", np.nan, "-", np.nan, "L", np.nan, "A", np.nan, "B"],
    'Col2': ["PL", "-", np.nan, np.nan, "u", np.nan, "a", "np.nan", "b"],
    'Col3': ["00", "-", np.nan, np.nan, "k's", np.nan, "x", np.nan, "y"],
    'Col4': ["Puesta tierra en suelo Rocoso", "Protocolos de resistividad - Seccionamiento LT", np.nan, "VHA", np.nan, "PURETE", np.nan, "Value", np.nan]
}

dfa = pd.DataFrame(data)
print(dfa.isna().any().any())
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

""" combined_df = combined_df.drop(columns=["Completeness"])
print("This is the original DataFrame:")
print(df)
print("\nThis is the DataFrame with NaN and percentage:")
print(nan_rows)
print("\nThis is the DataFrame without NaN and percentage:")
df = df.dropna()
print(df)
print("\nThis is the final combined DataFrame:")
print(combined_df)
df = pd.concat([df, combined_df])
print("\nThis is the final clean DataFrame:")
print(df) """
print("\nThis is the final clean DataFrame:")
print(clean_double_row(dfa))

##################################################################################################################################################
# modificar si la tabla tiene una columna de mas
# BIEN

""" import pandas as pd
import numpy as np
import difflib

data = {
    'DOC. N°': ["M-2000-36140-001", "L-0920-16200-001", "L-0920-16200-001", "M-2000-16100-001"],
    'Tipo': ["PL", "PL", "PL", "PL"],
    'Rev.': ["00", "00", "00", "00"],
    'Unnamed: 0': ["A", "B", "C", "D"],
    'Descripción': [np.nan, np.nan, np.nan, np.nan],
    #'situación': [np.nan, np.nan, np.nan, np.nan],  # Añadida para la última columna
}

tabla1 = pd.DataFrame(data)
print(f"Esta es la tabla original \n{tabla1}")

def clean_unnamed_col(tabla):
    # Verificar si la tabla tiene 5 columnas y el header de la última columna es similar a "situacion"
    if len(tabla.columns) == 5 and not \
            difflib.SequenceMatcher(None, tabla.columns[-1].lower(), "situacion").ratio() >= 0.9:
        # Definir palabras clave y umbrales de similitud
        keywords = ["Descripcion", "Unnamed: 0"]
        similarity_threshold = 0.8  # Puedes ajustar este valor según tu criterio

        # Encontrar el encabezado más similar a cada palabra clave
        header_similarity = {}
        for keyword in keywords:
            closest_match = difflib.get_close_matches(keyword, tabla.columns, n=1, cutoff=similarity_threshold)
            if closest_match:
                header_similarity[keyword] = closest_match[0]

        # Verificar si se encontraron las palabras clave
        if "Descripcion" in header_similarity and "Unnamed: 0" in header_similarity:
            # Intercambiar los encabezados de las columnas según la similitud
            tabla.rename(columns={header_similarity["Descripcion"]: "Temp"}, inplace=True)
            tabla.rename(columns={header_similarity["Unnamed: 0"]: header_similarity["Descripcion"]}, inplace=True)
            tabla.rename(columns={"Temp": header_similarity["Unnamed: 0"]}, inplace=True)

            # Verificar si la nueva última columna está compuesta solo de NaN
            last_column = tabla.columns[-1]
            if tabla[last_column].isnull().all():
                # Eliminar la nueva última columna
                tabla.drop(columns=[last_column], inplace=True)
    
    return tabla

print(f"Esta es la tabla modificada \n{clean_unnamed_col(tabla1)}") """


















