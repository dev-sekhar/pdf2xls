import pdfplumber
import pandas as pd
import sys
import os
import re
import logging
from dotenv import load_dotenv

load_dotenv()

# Set up logging for better tracking and debugging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_tables_from_pdf(pdf_file_obj):
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
                            df = pd.DataFrame(cleaned_table[1:], columns=cleaned_table[0])
                        elif cleaned_table and len(cleaned_table) == 1:
                            df = pd.DataFrame(cleaned_table)
                            
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

def save_tables_to_excel(all_tables, output_path_or_buffer):
    try:
        with pd.ExcelWriter(output_path_or_buffer, engine='openpyxl') as writer:
            for sheet_name, df in all_tables:
                # Final safety check on sheet names to prevent corrupting the workbook
                safe_sheet_name = re.sub(r'[\[\]:\*\?/\\]', '', sheet_name).strip()[:31] or "Unnamed_Sheet"
                df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
    except PermissionError:
        logger.error(f"Permission denied: Cannot write to {output_path_or_buffer}. Is the Excel file currently open?")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while saving Excel file: {e}")
        raise

def extract_tables_to_excel(pdf_path, output_excel_path):
    if not os.path.exists(pdf_path):
        logger.error(f"Error: The file '{pdf_path}' does not exist.")
        return False

    try:
        logger.info(f"Starting extraction process for: {pdf_path}")
        all_tables = get_tables_from_pdf(pdf_path)

        if not all_tables:
            logger.warning(f"No valid tables were found in the document: {pdf_path}")
            return False

        logger.info(f"Extraction successful: {len(all_tables)} table(s) found. Saving to dataset...")
        save_tables_to_excel(all_tables, output_excel_path)
        logger.info(f"Process complete! File saved safely to: {output_excel_path}")
        
        return True

    except Exception as e:
        logger.error(f"Extraction sequence failed with an exception: {e}")
        return False

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            pdf_file = input("Please enter the path or name of the PDF file to convert: ").strip()
            if not pdf_file:
                logger.error("No file provided. Exiting.")
                sys.exit(1)
                
            base_name = os.path.splitext(os.path.basename(pdf_file))[0]
            default_dir = os.path.dirname(os.path.abspath(pdf_file))
            
            out_path = input(f"Please enter the directory path to save the file (press Enter to use '{default_dir}'): ").strip()
            if not out_path:
                out_path = default_dir
                
            if not os.path.exists(out_path):
                os.makedirs(out_path, exist_ok=True)
                
            excel_file = os.path.join(out_path, f"{base_name}.xlsx")
        else:
            pdf_file = sys.argv[1]
            base_name = os.path.splitext(os.path.basename(pdf_file))[0]
            
            if len(sys.argv) >= 3:
                out_path = sys.argv[2]
                if not os.path.exists(out_path):
                    os.makedirs(out_path, exist_ok=True)
                excel_file = os.path.join(out_path, f"{base_name}.xlsx")
            else:
                default_dir = os.path.dirname(os.path.abspath(pdf_file))
                excel_file = os.path.join(default_dir, f"{base_name}.xlsx")
            
        success = extract_tables_to_excel(pdf_file, excel_file)
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nProcess canceled by user.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"A critical crash occurred during execution: {e}")
        sys.exit(1)
