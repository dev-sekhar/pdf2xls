import pdfplumber
import pandas as pd
import re

"""
src/extractor.py
----------------
Purpose: Provides all core functionality for parsing PDF files.
This microservice isolates the table detection heuristics, text-box 
reading capabilities, and raw data cleanup before passing it down.
"""

from src.config import get_logger

logger = get_logger(__name__)

def get_tables_from_pdf(pdf_file_obj):
    """Parses a PDF file buffer and securely extracts tables dynamically."""
    all_tables = []
    try:
        with pdfplumber.open(pdf_file_obj) as pdf:
            logger.info(f"Successfully opened PDF. Processing {len(pdf.pages)} pages...")
            
            for page_num, page in enumerate(pdf.pages):
                try:
                    found_tables = page.find_tables()
                    if not found_tables:
                        continue
                    
                    for table_num, table_obj in enumerate(found_tables):
                        table_data = table_obj.extract()
                        if not table_data:
                            continue
                            
                        # Attempt to find a title immediately above the table
                        table_top = table_obj.bbox[1]
                        top_bound = max(0, table_top - 60)
                        bottom_bound = max(top_bound + 1, table_top - 2)
                        crop_box = (0, top_bound, page.width, bottom_bound)
                        
                        sheet_name = ""
                        try:
                            title_crop = page.crop(crop_box)
                            title_text = title_crop.extract_text()
                            if title_text and title_text.strip():
                                lines = [line.strip() for line in title_text.strip().split('\n') if line.strip()]
                                if lines:
                                    raw_name = lines[-1]
                                    clean_name = re.sub(r'[\[\]:\*\?/\\]', '', raw_name).strip()
                                    sheet_name = clean_name[:31]
                        except Exception as e:
                            logger.debug(f"Could not extract title for a table on page {page_num+1}: {e}")
                            
                        if not sheet_name or len(sheet_name) < 3:
                            sheet_name = f"Page_{page_num+1}_T{table_num+1}"

                        cleaned_table = []
                        for row in table_data:
                            cleaned_row = [str(cell).replace('\n', ' ') if cell is not None else '' for cell in row]
                            cleaned_table.append(cleaned_row)
                        
                        df = None
                        if cleaned_table and len(cleaned_table) > 1:
                            # Streamlit requires all column names to be strictly unique
                            raw_cols = cleaned_table[0]
                            seen = {}
                            unique_cols = []
                            for col in raw_cols:
                                col_name = str(col).strip()
                                if not col_name:
                                    col_name = "Unnamed"
                                if col_name in seen:
                                    seen[col_name] += 1
                                    unique_cols.append(f"{col_name}_{seen[col_name]}")
                                else:
                                    seen[col_name] = 0
                                    unique_cols.append(col_name)
                                    
                            df = pd.DataFrame(cleaned_table[1:], columns=unique_cols)
                        elif cleaned_table and len(cleaned_table) == 1:
                            df = pd.DataFrame(cleaned_table)
                            df.columns = [str(c) for c in df.columns]
                            
                        if df is not None:
                            # Safely handle duplicate sheet names
                            base_sheet_name = sheet_name
                            counter = 1
                            while any(name == sheet_name for name, _ in all_tables):
                                suffix = f"_{counter}"
                                sheet_name = f"{base_sheet_name[:31-len(suffix)]}{suffix}"
                                counter += 1
                                
                            all_tables.append((sheet_name, df))
                except Exception as e:
                    logger.warning(f"Skipping page {page_num+1} due to processing error: {e}")
                    continue
                    
    except Exception as e:
        logger.error(f"Failed to read or parse the PDF document: {e}")
        raise
        
    return all_tables
