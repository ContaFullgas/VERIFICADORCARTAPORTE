# xml_processor.py

import xml.etree.ElementTree as ET
from datetime import datetime
from utils import parse_float, format_and_compare_liters, map_clave_to_combustible

# Namespace para el CFDI
NS_CFDI = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}

def identify_format(file_path: str) -> str | None:

    """
    Esta función de Python identifica el formato de un archivo basado en la presencia de elementos
    específicos en la estructura XML.
    
    Argumentos:
      file_path (str): La función `identify_format` toma como entrada la ruta de un archivo e intenta
    identificar el formato del archivo basado en la presencia de elementos específicos en la estructura
    XML. Verifica la presencia de ciertos elementos como 'Mercancia' dentro de diferentes espacios de
    nombres para determinar el formato del archivo.
    
    Retorna:
      La función `identify_format` devuelve una cadena que indica el formato del archivo basado en la
    presencia de elementos específicos en la estructura XML. Los posibles valores de retorno son
    'format1', 'format2', 'format31' si se encuentran los elementos correspondientes en el archivo XML.
    Si no se encuentra ninguno de estos elementos, la función devuelve `None`.
"""
    tree = ET.parse(file_path)
    root = tree.getroot()

    if root.findall('.//cartaporte20:Mercancia', namespaces={'cartaporte20': 'http://www.sat.gob.mx/CartaPorte20'}):
        return 'format1'
    elif root.findall('.//cartaporte30:Mercancia', namespaces={'cartaporte30': 'http://www.sat.gob.mx/CartaPorte30'}):
        return 'format2'
    elif root.findall('.//cartaporte31:Mercancia', namespaces={'cartaporte31': 'http://www.sat.gob.mx/CartaPorte31'}):
        return 'format31'
    else:
        return None

def extract_common_data(root: ET.Element) -> dict:
    """
    Argumentos:
      root (ET.Element): La función `extract_common_data` toma un elemento XML `root` como entrada y
    extrae datos comunes como Fecha, Serie, Folio, etc., a partir de los atributos del elemento XML.
    
    Retorna:
      Un diccionario que contiene los datos comunes extraídos del elemento XML, como 'FechaEmision',
    'Periodo', 'Serie', 'Folio', 'Clave SAT', 'Cantidad Litros Facturada', 'Litros Transportada',
    'Combustible' y 'Comparacion'.
    """
    fecha_str = root.attrib.get('Fecha', '')
    try:
        fecha_dt = datetime.fromisoformat(fecha_str)
    except ValueError:
        fecha_dt = None
    periodo = str(fecha_dt.month) if fecha_dt else ''
    return {
        'FechaEmision': fecha_dt,
        'Periodo': periodo,
        'Serie': root.attrib.get('Serie', ''),
        'Folio': root.attrib.get('Folio', ''),
        'Clave SAT': None,
        'Cantidad Litros Facturada': None,
        'Litros Transportada': None,
        'Combustible': None,
        'Comparacion': ''
    }

def process_xml_format1(file_path: str) -> dict:
    """
    La función `process_xml_format1` analiza un archivo XML, extrae elementos de datos específicos,
    realiza cálculos sobre los datos extraídos y devuelve un diccionario con la información procesada.
    
    Argumentos:
      file_path (str): La función `process_xml_format1` procesa un archivo XML para extraer datos
    específicos relacionados con la facturación y el transporte. Extrae datos comunes, como la cantidad
    facturada y transportada, así como el tipo de combustible transportado.
    
    Retorna:
      La función `process_xml_format1` devuelve un diccionario `data` que contiene los datos extraídos
    de un archivo XML especificado por `file_path`. Los datos extraídos incluyen información común,
    cantidad facturada en litros, cantidad transportada en litros, código SAT, tipo de combustible y un
    resultado de comparación entre los litros facturados y transportados.
"""

    tree = ET.parse(file_path)
    root = tree.getroot()
    data = extract_common_data(root)
    
    # Cantidad facturada
    concepto = root.find('.//cfdi:Concepto', namespaces=NS_CFDI)
    if concepto is not None:
        data['Cantidad Litros Facturada'] = concepto.attrib.get('Cantidad', '')
    
    # Cantidad transportada y mapeo de combustible
    mercancia = root.find('.//cartaporte20:Mercancia', namespaces={'cartaporte20': 'http://www.sat.gob.mx/CartaPorte20'})
    if mercancia is not None:
        clave_prod_serv = mercancia.attrib.get('BienesTransp', '')
        data['Clave SAT'] = clave_prod_serv
        data['Litros Transportada'] = mercancia.attrib.get('Cantidad', '')
        data['Combustible'] = map_clave_to_combustible(clave_prod_serv)
    
    fac, trans, comp = format_and_compare_liters(
        data['Cantidad Litros Facturada'] or '0',
        data['Litros Transportada'] or '0'
    )
    data['Cantidad Litros Facturada'] = fac
    data['Litros Transportada'] = trans
    data['Comparacion'] = comp
    return data

def process_xml_format2(file_path: str) -> dict:

    """

    Argumentos:
      file_path (str): El parámetro `file_path` en la función `process_xml_format2` es una cadena que
    representa la ruta del archivo XML que se desea procesar. Esta función lee el archivo XML, extrae
    datos específicos de él y devuelve un diccionario con la información procesada.
    
    Retorna:
      Un diccionario que contiene los datos procesados extraídos del archivo XML en formato CartaPorte30
    (format2), incluyendo datos comunes, cantidad de litros facturados, código SAT, cantidad de litros
    transportados, tipo de combustible, cantidad de litros facturados formateada, cantidad de litros
    transportados formateada y un resultado de comparación.
"""
    tree = ET.parse(file_path)
    root = tree.getroot()
    data = extract_common_data(root)
    
    concepto = root.find('.//cfdi:Concepto', namespaces=NS_CFDI)
    if concepto is not None:
        data['Cantidad Litros Facturada'] = concepto.attrib.get('Cantidad', '')
    
    mercancia = root.find('.//cartaporte30:Mercancia', namespaces={'cartaporte30': 'http://www.sat.gob.mx/CartaPorte30'})
    if mercancia is not None:
        clave_prod_serv = mercancia.attrib.get('BienesTransp', '')
        data['Clave SAT'] = clave_prod_serv
        
        cantidad_transporta = mercancia.find(
            './/cartaporte30:CantidadTransporta',
            namespaces={'cartaporte30': 'http://www.sat.gob.mx/CartaPorte30'}
        )
        if cantidad_transporta is not None:
            data['Litros Transportada'] = cantidad_transporta.attrib.get('Cantidad', '')
        else:
            data['Litros Transportada'] = mercancia.attrib.get('Cantidad', '')
        data['Combustible'] = map_clave_to_combustible(clave_prod_serv)
    
    fac, trans, comp = format_and_compare_liters(
        data.get('Cantidad Litros Facturada', '0'),
        data.get('Litros Transportada', '0')
    )
    data['Cantidad Litros Facturada'] = fac
    data['Litros Transportada'] = trans
    data['Comparacion'] = comp
    return data

def process_xml_format31(file_path: str) -> dict:
    """"Procesa un archivo XML en el formato "Carta Porte 3.1" y extrae datos relevantes.
        file_path (str): La ruta al archivo XML que se va a procesar.
        dict: Un diccionario que contiene los datos extraídos, incluyendo:
            - 'Cantidad Litros Facturada': La cantidad de litros facturada, extraída del nodo 'cfdi:Concepto'.
            - 'Clave SAT': La clave SAT de los bienes transportados, extraída del nodo 'cartaporte31:Mercancia'.
            - 'Litros Transportada': La cantidad de litros transportados, extraída del nodo 'cartaporte31:CantidadTransporta' o del nodo 'cartaporte31:Mercancia'.
            - 'Combustible': El tipo de combustible, mapeado a partir de la clave SAT.
            - 'Comparacion': Un resultado de comparación entre los litros facturados y los litros transportados.
    """

    tree = ET.parse(file_path)
    root = tree.getroot()
    data = extract_common_data(root)
    
    concepto = root.find('.//cfdi:Concepto', namespaces=NS_CFDI)
    if concepto is not None:
        data['Cantidad Litros Facturada'] = concepto.attrib.get('Cantidad', '')
    
    mercancia = root.find(
        './/cartaporte31:Mercancia',
        namespaces={'cartaporte31': 'http://www.sat.gob.mx/CartaPorte31'}
    )
    if mercancia is not None:
        clave_prod_serv = mercancia.attrib.get('BienesTransp', '')
        data['Clave SAT'] = clave_prod_serv
        
        cantidad_transporta_node = mercancia.find(
            './/cartaporte31:CantidadTransporta',
            namespaces={'cartaporte31': 'http://www.sat.gob.mx/CartaPorte31'}
        )
        if cantidad_transporta_node is not None:
            data['Litros Transportada'] = cantidad_transporta_node.attrib.get('Cantidad', '')
        else:
            data['Litros Transportada'] = mercancia.attrib.get('Cantidad', '')
        data['Combustible'] = map_clave_to_combustible(clave_prod_serv)
    
    fac, trans, comp = format_and_compare_liters(
        data.get('Cantidad Litros Facturada', '0'),
        data.get('Litros Transportada', '0')
    )
    data['Cantidad Litros Facturada'] = fac
    data['Litros Transportada'] = trans
    data['Comparacion'] = comp
    return data

def process_file_based_on_format(file_path: str) -> dict | None:
    """
    Procesa un archivo basado en su formato identificado.
    Este método toma la ruta de un archivo, identifica su formato utilizando la función
    `identify_format` y luego llama a la función de procesamiento correspondiente según
    el formato identificado. Si el formato no es reconocido, devuelve `None`.
    Parámetros:
    -----------
    file_path : str
        La ruta completa del archivo que se desea procesar.
    Retorna:
    --------
    dict | None
        Un diccionario con los datos procesados si el formato es reconocido y procesado
        correctamente. Si el formato no es reconocido, devuelve `None`.
    Formatos soportados:
    --------------------
    - 'format1': Procesado por la función `process_xml_format1`.
    - 'format2': Procesado por la función `process_xml_format2`.
    - 'format31': Procesado por la función `process_xml_format31`.
    Nota:
    -----
    Asegúrese de que las funciones `identify_format`, `process_xml_format1`, 
    `process_xml_format2` y `process_xml_format31` estén correctamente implementadas 
    y disponibles en el entorno donde se ejecuta esta función.
    """

    format_type = identify_format(file_path)
    if format_type == 'format1':
        return process_xml_format1(file_path)
    elif format_type == 'format2':
        return process_xml_format2(file_path)
    elif format_type == 'format31':
        return process_xml_format31(file_path)
    else:
        return None
