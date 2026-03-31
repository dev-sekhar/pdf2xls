import streamlit as st

# Must be the very first Streamlit command!
st.set_page_config(page_title="PDF to Excel Converter", page_icon="📊", layout="wide")

import io
import os
import pandas as pd
from src.extractor import get_tables_from_pdf
from src.exporter import save_tables_to_excel

# app.py
# ------
# Purpose: The main entrypoint for the Streamlit web application.
# It provides a user-friendly graphical interface allowing users to upload a PDF,
# interactively review/edit rows, inject explicitly structured columns/rows, 
# and export the result securely as an Excel file.

st.title("📊 PDF to Excel Table Extractor")
st.write("Upload a PDF to automatically extract its tables. You can review and edit them directly in the browser before generating your Excel file!")

# Initialize session state variables to store tables across interactions
if "extracted_tables" not in st.session_state:
    st.session_state.extracted_tables = None
if "current_file" not in st.session_state:
    st.session_state.current_file = None

# Create the file uploader
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    # If the user uploads a different file, reset the session state
    if st.session_state.current_file != uploaded_file.name:
        st.session_state.current_file = uploaded_file.name
        st.session_state.extracted_tables = None

    # Step 1: Extract tables block
    if st.session_state.extracted_tables is None:
        with st.spinner("Automatically extracting tables native (this may take a moment)..."):
            try:
                all_tables = get_tables_from_pdf(uploaded_file)
                
                if not all_tables:
                    st.warning("No tables were found in this PDF.")
                else:
                    # Store extracted tables to our persistent state
                    st.session_state.extracted_tables = all_tables
                    st.rerun()  # Refresh to hide the button and show the editor
            except Exception as e:
                st.error(f"An error occurred: {e}")

    # Step 2: Display tables in interactive data editors
    if st.session_state.extracted_tables is not None:
        st.success(f"Found {len(st.session_state.extracted_tables)} table(s)! You can edit rows/cells below before downloading.")
        
        # We will iterate through and render a data_editor for each table
        edited_tables = []
        for i, (sheet_name, df) in enumerate(st.session_state.extracted_tables):
            st.subheader(f"📝 Sheet: {sheet_name}")
            
            # Add an explicit checkbox column that controls what gets downloaded
            if "Include in Export" not in df.columns:
                df.insert(0, "Include in Export", True)
            
            # Using data_editor allows seamless editing, rearranging, and adding rows natively
            edited_df = st.data_editor(
                df,
                num_rows="dynamic",
                use_container_width=True,
                key=f"editor_tab_{i}",
                hide_index=True
            )
            
            # Sync native edits back to state so explicit buttons don't delete them on rerun
            st.session_state.extracted_tables[i] = (sheet_name, edited_df)
            
            # Explicit feature: Advanced Row & Column inserters
            with st.expander(f"⚙️ Advanced Schema Editor - {sheet_name}"):
                row_col, col_col = st.columns(2)
                with row_col:
                    new_row_idx = st.number_input("Insert Row At Index (0-indexed)", min_value=0, max_value=len(edited_df), value=len(edited_df), key=f"row_idx_{i}")
                    if st.button("➕ Insert Explicit Row", key=f"add_row_btn_{i}"):
                        new_row = pd.DataFrame([[''] * len(edited_df.columns)], columns=edited_df.columns)
                        new_row["Include in Export"] = True
                        updated_df = pd.concat([edited_df.iloc[:new_row_idx], new_row, edited_df.iloc[new_row_idx:]]).reset_index(drop=True)
                        st.session_state.extracted_tables[i] = (sheet_name, updated_df)
                        st.rerun()
                with col_col:
                    new_col_name = st.text_input("New Column Name", key=f"new_col_name_{i}")
                    new_col_idx = st.number_input("Insert Column At Index", min_value=1, max_value=len(edited_df.columns), value=len(edited_df.columns), key=f"col_idx_{i}")
                    if st.button("➕ Insert Explicit Column", key=f"add_col_btn_{i}"):
                        if new_col_name and new_col_name not in edited_df.columns:
                            updated_df = edited_df.copy()
                            updated_df.insert(new_col_idx, new_col_name, '')
                            st.session_state.extracted_tables[i] = (sheet_name, updated_df)
                            st.rerun()
                        elif new_col_name in edited_df.columns:
                            st.error("Wait! A column with that precise name already exists.")

            # Filter rows where user unchecked the box, then drop the helper column
            final_df = edited_df[edited_df["Include in Export"] == True].drop(columns=["Include in Export"])
            edited_tables.append((sheet_name, final_df))
            
        st.divider()
        
        st.subheader("Ready to Export?")
        
        # We write the dynamically edited dataframes rather than the static original ones!
        output_buffer = io.BytesIO()
        save_tables_to_excel(edited_tables, output_buffer)
        
        # Construct intelligent file name
        original_name = uploaded_file.name
        base_name = os.path.splitext(original_name)[0]
        download_name = f"{base_name}.xlsx"
        
        # Layout columns to make the button look nice
        col1, col2 = st.columns([1, 4])
        with col1:
            st.download_button(
                label="📥 Download Excel File",
                data=output_buffer.getvalue(),
                file_name=download_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
        with col2:
            if st.button("🗑️ Clear & Restart"):
                st.session_state.extracted_tables = None
                st.rerun()
