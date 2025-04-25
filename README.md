# VERIFICADORCARTAPORTE

![image](https://github.com/user-attachments/assets/30cb7965-8682-4aad-89c5-8cef9a10e76a)

# 📘 Manual de Usuario y Documentación Técnica

## 🧾 Descripción General

Este proyecto es una aplicación desarrollada con **Python y Streamlit** para la **verificación de cartaportes**. Permite a los usuarios cargar archivos **XML**, **ZIP** o **PDF**, procesarlos y visualizar los resultados de forma interactiva. Además, ofrece funciones de **descarga de resultados** en Excel o ZIP, así como **visualización directa de los archivos PDF asociados**.

---

## 🗂 Estructura del Proyecto

### 1. `main.py`  
Interfaz principal en **Streamlit**.

- Carga y validación de archivos XML, ZIP o PDF.
- Procesamiento mediante `process_uploaded_files`.
- Visualización de resultados con filtros dinámicos.
- Exportación de resultados en Excel o ZIP.
- Visualización embebida de PDFs asociados.

---

### 2. `pdf_handler.py`  
Manejo de archivos subidos y generación de paquetes.

- Asociación entre XML y sus correspondientes PDFs.
- Extracción y procesamiento de ZIP/XML/PDF.
- Generación de un archivo ZIP con los resultados y PDFs.

---

### 3. `xml_processor.py`  
Procesamiento especializado para los distintos formatos XML de Carta Porte.

- Identificación del formato del XML (`format1`, `format2`, `format31`).
- Extracción de campos comunes (fecha, folio, serie, etc.).
- Extracción de datos específicos según formato (litros facturados/transportados, claves SAT).
- Llamada a funciones específicas según formato detectado.

---

### 4. `utils.py`  
Funciones auxiliares para manejo de datos.

- `parse_float`: conversión robusta de strings a floats.
- `format_and_compare_liters`: comparación entre litros facturados y transportados.
- `map_clave_to_combustible`: mapeo de claves SAT a tipos de combustible (`magna`, `premium`, `diesel`).

---

## ▶️ Cómo Ejecutar el Proyecto

1. Instala las dependencias:
   ```bash
   pip install streamlit pandas openpyxl
   ```

2. Ejecuta la app:
   ```bash
   streamlit run main.py
   ```

3. Accede en el navegador:
   ```
   http://localhost:8501
   ```

---

## 🔄 Flujo de Trabajo

```plaintext
[ Carga de Archivos ]
      ↓
[ Descompresión de ZIP ]
      ↓
[ Procesamiento de XMLs ]
      ↓
[ Asociación con PDFs ]
      ↓
[ Visualización de Datos ]
      ↓
[ Descarga de Excel o ZIP ]
      ↓
[ Visualización Embebida de PDFs ]
```

---

## 🔍 Detalles de los Módulos

### `main.py`
- Interfaz de carga (`st.file_uploader`)
- Botón para procesamiento.
- Filtro por tipo de combustible.
- Visualización en tabla (`st.dataframe`).
- Botones para descarga (`st.download_button`).
- Visualización en PDF Viewer integrado.

### `pdf_handler.py`
- `identify_pdf(xml_name)`: encuentra el PDF asociado.
- `process_uploaded_files(files)`: centraliza el procesamiento.
- `generar_zip(dataframe, pdf_paths)`: empaqueta resultados en ZIP.

### `xml_processor.py`
- `identify_format(root)`: inspecciona nodos XML para definir el formato.
- `extract_common_data(root)`: extrae datos universales (serie, folio, fecha, etc.).
- `process_xml_formatX(root)`: extrae datos por versión (2.0, 3.0, 3.1).
- `process_file_based_on_format(file)`: orquesta el procesamiento correcto.

### `utils.py`
- Funciones robustas para manejo de valores nulos, formateo de litros y asociaciones semánticas con claves SAT.

---

## 📝 Notas Importantes

- **Soporte**: XMLs `Carta Porte 2.0`, `3.0`, `3.1`.
- **Errores**: Se imprime una advertencia en consola en caso de error de parseo o lectura.
- **Ordenamiento**: Datos ordenados por `FechaEmision` antes de mostrar.
- **Compatibilidad**: Probado en Python 3.8+, Streamlit 1.20+.

---

## 🧪 Ejemplo de Uso

1. Sube un ZIP con XMLs y PDFs.
2. Presiona “Procesar archivos”.
3. Visualiza y filtra la tabla.
4. Descarga el Excel o ZIP.
5. Visualiza un PDF directamente.

---

## 📦 Dependencias

| Paquete        | Descripción                        |
|----------------|------------------------------------|
| `streamlit`    | Interfaz gráfica web               |
| `pandas`       | Manipulación de datos              |
| `openpyxl`     | Escritura de archivos Excel (.xlsx)|

Instalación:
```bash
pip install streamlit pandas openpyxl
```

---

## 👨‍💻 Créditos

Desarrollado por **Javier Can**.  
Este proyecto puede ser extendido para validación avanzada de CFDIs, integración con bases de datos, o análisis histórico de consumo por cliente.

