import streamlit as st
import io
import os
from pdf_to_excel import get_tables_from_pdf, save_tables_to_excel

st.set_page_config(page_title="PDF to Excel Converter", page_icon="📊")

st.title("📊 PDF to Excel Table Extractor")
st.write("Upload a PDF to automatically extract its tables into individual Excel sheets.")

# Create the file uploader
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Action button
    if st.button("Extract Tables"):
        with st.spinner("Extracting tables natively (this may take a moment)..."):
            try:
                # 1. Run our core extraction function directly on the uploaded file stream
                all_tables = get_tables_from_pdf(uploaded_file)
                
                if not all_tables:
                    st.warning("No tables were found in this PDF.")
                else:
                    st.success(f"Found {len(all_tables)} table(s)! Preparing Excel file...")
                    
                    # 2. Write the tables to an in-memory buffer so the user can download it securely
                    output_buffer = io.BytesIO()
                    save_tables_to_excel(all_tables, output_buffer)
                    
                    # 3. Construct intelligent file name
                    original_name = uploaded_file.name
                    base_name = os.path.splitext(original_name)[0]
                    download_name = f"{base_name}.xlsx"
                    
                    # 4. Display download button
                    st.download_button(
                        label="📥 Download Excel File",
                        data=output_buffer.getvalue(),
                        file_name=download_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")
