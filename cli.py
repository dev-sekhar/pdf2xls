import os
import sys

"""
cli.py
------
Purpose: The main entrypoint for the Command Line Interface (CLI).
It bypasses the web UI entirely and provides terminal access to run the PDF 
extraction programmatically, supporting both strict scripts and user prompts.
"""

from src.extractor import get_tables_from_pdf
from src.exporter import save_tables_to_excel
from src.config import get_logger

logger = get_logger(__name__)

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
