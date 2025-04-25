# pdf_handler.py

import os
import shutil
import zipfile
from io import BytesIO
import pandas as pd
import streamlit as st
from xml_processor import process_file_based_on_format

def identify_pdf(xml_filename: str, pdf_files: dict) -> str:
    """Identifica el archivo PDF asociado a un archivo XML dado.
    Esta función toma el nombre de un archivo XML y un diccionario que contiene
    los nombres de archivos PDF disponibles. Busca un archivo PDF cuyo nombre base
    coincida con el del archivo XML (es decir, el nombre del archivo sin la extensión)
    y devuelve el nombre del archivo PDF si se encuentra. Si no se encuentra un archivo
    PDF correspondiente, devuelve 'No encontrado'.
    Parámetros:
    ----------
    xml_filename : str
        El nombre del archivo XML (incluyendo la extensión .xml).
    pdf_files : dict
        Un diccionario donde las claves son los nombres de los archivos PDF disponibles.
    Retorna:
    -------
    str
        El nombre del archivo PDF asociado si existe, o 'No encontrado' si no se encuentra."""

    """
    Busca el PDF asociado a un archivo XML.
    """
    base_name = os.path.splitext(xml_filename)[0]
    pdf_name = base_name + ".pdf"
    return pdf_name if pdf_name in pdf_files else 'No encontrado'

def process_uploaded_files(uploaded_files) -> tuple[pd.DataFrame, dict]:
    """
    La función `process_uploaded_files` procesa una lista de archivos subidos por el usuario, que pueden
    incluir archivos PDF, XML y ZIP. Realiza las siguientes tareas:

    1. Crea un directorio temporal para almacenar los archivos subidos y extraer el contenido de los ZIP.
    2. Identifica y recopila los archivos PDF y XML presentes en los archivos subidos o extraídos.
    3. Procesa cada archivo XML para extraer información relevante y asocia el archivo PDF correspondiente.
    4. Devuelve un DataFrame con los datos procesados y un diccionario con los archivos PDF.

    Argumentos:
      uploaded_files (list): Lista de archivos subidos por el usuario. Cada archivo puede ser un PDF, XML o ZIP.

    Retorna:
      tuple[pd.DataFrame, dict]: Una tupla que contiene:
        - Un DataFrame con los datos procesados de los archivos XML, incluyendo información como:
          * 'XML_File': Nombre del archivo XML procesado.
          * 'PDF Asociado': Nombre del archivo PDF asociado al XML.
          * Otros datos extraídos del XML, como cantidades facturadas y transportadas.
        - Un diccionario donde las claves son los nombres de los archivos PDF y los valores son sus rutas completas.

    Detalles del procesamiento:
      - Los archivos ZIP se extraen en el directorio temporal para detectar archivos PDF y XML adicionales.
      - Los archivos XML se procesan utilizando la función `process_file_based_on_format`, que extrae datos específicos
        según el formato del XML.
      - Se utiliza la función `identify_pdf` para asociar un archivo PDF al XML basado en el nombre del archivo.
      - Si se detectan errores al procesar un XML, se imprime un mensaje de error en la consola.
      - Se utiliza una barra de progreso (Streamlit) para mostrar el avance del procesamiento de los XML.

    Notas:
      - El DataFrame resultante incluye columnas como 'Cantidad Litros Facturada' y 'Litros Transportada', que se convierten
        a tipo float para facilitar cálculos posteriores.
      - La columna 'FechaEmision' se utiliza para ordenar los datos, pero se elimina antes de devolver el DataFrame.
      - El directorio temporal se elimina y recrea al inicio de la función para garantizar un entorno limpio.
"""
    """
    Procesa los archivos subidos:
      1. Crea un directorio temporal y extrae ZIPs.
      2. Recopila los archivos PDF y XML.
      3. Procesa cada XML y asocia su PDF correspondiente.
      4. Retorna un DataFrame con la información y un diccionario con los PDFs.
    """
    temp_dir = './temp_files'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    pdf_files = {}

    # Guardar archivos y extraer ZIPs
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        if uploaded_file.name.lower().endswith('.pdf'):
            pdf_files[uploaded_file.name] = file_path
        elif uploaded_file.name.lower().endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

    # Detectar PDFs extraídos
    for root_dir, _, files in os.walk(temp_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root_dir, file)
                pdf_files[file] = full_path

    # Recopilar archivos XML
    all_xml_files = []
    for root_dir, _, files in os.walk(temp_dir):
        for file in files:
            if file.lower().endswith('.xml'):
                all_xml_files.append(os.path.join(root_dir, file))
    all_xml_files = sorted(all_xml_files)

    all_data = []
    total_xml = len(all_xml_files)
    progress_bar = st.progress(0) if total_xml else None

    for idx, xml_path in enumerate(all_xml_files, start=1):
        try:
            data = process_file_based_on_format(xml_path)
            if data:
                xml_filename = os.path.basename(xml_path)
                data['XML_File'] = xml_filename
                data['PDF Asociado'] = identify_pdf(xml_filename, pdf_files)
                all_data.append(data)
        except Exception as e:
            print(f"Error procesando {xml_path}: {e}")

        if progress_bar:
            progress_bar.progress(idx / total_xml)

    df_result = pd.DataFrame(all_data)
    if not df_result.empty:
        df_result["Cantidad Litros Facturada"] = df_result["Cantidad Litros Facturada"].astype(float)
        df_result["Litros Transportada"] = df_result["Litros Transportada"].astype(float)
        df_result = df_result.sort_values(by="FechaEmision", na_position='last').reset_index(drop=True)
        df_result.drop(columns=["FechaEmision"], inplace=True)

    return df_result, pdf_files

def generar_zip(df: pd.DataFrame, pdf_files: dict) -> bytes:
    """
    Genera un ZIP en memoria que incluye:
      - Un archivo Excel con los datos procesados.
      - Los PDFs asociados.
    """
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zf:
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        zf.writestr("datos_procesados.xlsx", excel_buffer.getvalue())
        for pdf_name in df['PDF Asociado'].unique():
            if pdf_name != 'No encontrado' and pdf_name in pdf_files:
                zf.write(pdf_files[pdf_name], arcname=pdf_name)
    buffer.seek(0)
    return buffer.getvalue()
