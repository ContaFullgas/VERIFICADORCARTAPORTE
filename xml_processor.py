# xml_processor.py

import xml.etree.ElementTree as ET
from datetime import datetime
from utils import parse_float, format_and_compare_liters, map_clave_to_combustible

# Namespace para el CFDI
NS_CFDI = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}

def identify_format(file_path: str) -> str | None:
    """
    La función `identify_format` analiza un archivo XML e identifica el formato basándose en la presencia de
    elementos específicos con espacios de nombres definidos.
    
    param ruta_archivo: La función `identify_format` toma una ruta de archivo como entrada e intenta identificar
    el formato del archivo basándose en la presencia de elementos específicos en la estructura XML. Comprueba
    la presencia de ciertos elementos como 'Mercancia' dentro de diferentes espacios de nombres para determinar el
    formato del fichero
    :type ruta_archivo: str
    :return: La función `identify_format` devuelve una cadena que indica el formato del fichero
    basándose en la presencia de elementos específicos en la estructura XML. Los posibles valores de retorno son
    format1', 'format2', 'format31', o None si no se encuentra ninguno de los elementos especificados en el fichero XML especificado.
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
    Extrae datos comunes del XML, como Fecha, Serie, Folio, etc.
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
    Procesa un archivo XML en formato CartaPorte20 (format1).
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
    Procesa un archivo XML en formato CartaPorte30 (format2).
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
    """
    Procesa un archivo XML en formato CartaPorte31 (format31).
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
    Identifica el formato del XML y llama a la función de procesamiento correspondiente.
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
