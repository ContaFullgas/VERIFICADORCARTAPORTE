# main.py
"""
    Este archivo principal (`main.py`) implementa una aplicación Streamlit para la verificación de
    cartaportes. Permite a los usuarios cargar archivos XML, ZIP o PDF, procesarlos y visualizar los
    resultados. Las principales funcionalidades incluyen:

    1. **Carga de Archivos**:
       - Los usuarios pueden cargar múltiples archivos XML, ZIP o PDF utilizando un cargador de archivos.
       - Los archivos ZIP se descomprimen automáticamente para extraer su contenido.

    2. **Procesamiento de Archivos**:
       - Los archivos cargados se procesan mediante la función `process_uploaded_files` del módulo `pdf_handler`.
       - Se extraen datos relevantes de los archivos XML y se asocian con los archivos PDF correspondientes.

    3. **Visualización de Resultados**:
       - Los datos procesados se muestran en un DataFrame interactivo.
       - Se calculan y muestran las sumas totales de litros facturados y transportados.
       - Los usuarios pueden filtrar los resultados por tipo de combustible y ver las sumas correspondientes.

    4. **Descarga de Resultados**:
       - Los usuarios pueden descargar los datos procesados en formato Excel.
       - También pueden descargar un archivo ZIP que incluye el Excel y los PDFs asociados.

    5. **Visualización de PDFs Asociados**:
       - Los usuarios pueden seleccionar y visualizar los archivos PDF asociados directamente en la aplicación.

    Notas:
      - La aplicación utiliza `st.session_state` para almacenar los resultados procesados y los archivos PDF.
      - Se manejan casos en los que no se encuentran XML válidos o PDFs asociados.
      - La interfaz incluye mensajes de advertencia, éxito e información para mejorar la experiencia del usuario.

    Cómo ejecutar:
      - Ejecuta este archivo con `streamlit run main.py` en la terminal.
      - Accede a la aplicación en el navegador web para interactuar con las funcionalidades.

    Dependencias:
      - Streamlit
      - Pandas
      - Funciones auxiliares del módulo `pdf_handler` (`process_uploaded_files`, `generar_zip`).
"""
import os
import base64
from io import BytesIO
import streamlit as st
from pdf_handler import process_uploaded_files, generar_zip

def main():
    st.title("📁 Verificación Cartaportes")

    uploaded_files = st.file_uploader(
        "📂 Sube archivos XML, ZIP o PDF (puedes seleccionar varios archivos):",
        type=["zip", "xml", "pdf"],
        accept_multiple_files=True
    )

    if st.button("🚀 Procesar archivos"):
        if uploaded_files:
            df_result, pdf_files = process_uploaded_files(uploaded_files)
            st.session_state.df_result = df_result
            st.session_state.pdf_files = pdf_files

            if not df_result.empty:
                st.success("✅ Datos procesados correctamente:")
            else:
                st.warning("⚠️ No se encontraron XML válidos en los archivos cargados.")
        else:
            st.warning("⚠️ Por favor sube archivos antes de procesar.")

    if "df_result" in st.session_state and not st.session_state.df_result.empty:
        st.dataframe(st.session_state.df_result)

        total_facturada = st.session_state.df_result["Cantidad Litros Facturada"].sum()
        total_transportada = st.session_state.df_result["Litros Transportada"].sum()

        st.write(f"**Suma total Facturada (todas las filas):** {total_facturada:.3f}")
        st.write(f"**Suma total Transportada (todas las filas):** {total_transportada:.3f}")

        combustibles_unicos = st.session_state.df_result["Combustible"].dropna().unique()
        if len(combustibles_unicos) > 0:
            combustible_seleccionado = st.selectbox("Filtrar suma por combustible:", options=combustibles_unicos)
            df_filtrado = st.session_state.df_result[st.session_state.df_result["Combustible"] == combustible_seleccionado]
            total_facturada_filtrada = df_filtrado["Cantidad Litros Facturada"].sum()
            total_transportada_filtrada = df_filtrado["Litros Transportada"].sum()
            st.write(f"Suma total Facturada para **{combustible_seleccionado}**: {total_facturada_filtrada:.3f}")
            st.write(f"Suma total Transportada para **{combustible_seleccionado}**: {total_transportada_filtrada:.3f}")
        else:
            st.info("No se encontraron valores de combustible para filtrar.")

        # Descarga de Excel
        excel_buffer = BytesIO()
        st.session_state.df_result.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        st.download_button(
            "📥 Descargar Excel (solo datos)",
            data=excel_buffer,
            file_name="datos_procesados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Descarga de ZIP (Excel + PDFs asociados)
        zip_buffer = generar_zip(st.session_state.df_result, st.session_state.pdf_files)
        st.download_button(
            "📥 Descargar ZIP (Excel + PDFs asociados)",
            data=zip_buffer,
            file_name="datos_y_pdfs.zip",
            mime="application/zip"
        )

        st.markdown("---")
        st.subheader("📄 **Visualizar PDF asociado**")
        archivos_con_pdf = st.session_state.df_result[
            st.session_state.df_result['PDF Asociado'] != 'No encontrado'
        ]['PDF Asociado'].unique().tolist()

        if archivos_con_pdf:
            selected_pdf = st.selectbox("Selecciona un PDF para visualizar:", archivos_con_pdf)
            pdf_path = st.session_state.pdf_files[selected_pdf]

            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = f'''
                    <iframe src="data:application/pdf;base64,{base64_pdf}"
                            width="100%" height="700"
                            type="application/pdf">
                    </iframe>
                '''
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.error(f"❌ Archivo no encontrado: {pdf_path}")
        else:
            st.info("ℹ️ No hay PDFs asociados para visualizar.")

if __name__ == "__main__":
    main()
