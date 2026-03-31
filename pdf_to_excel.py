import pdfplumber
import pandas as pd
import sys
import os
import re

def extract_tables_to_excel(pdf_path, output_excel_path):
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return False

    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_tables = []
            
            for page_num, page in enumerate(pdf.pages):
                # Use find_tables to get bounding boxes to identify titles above them
                found_tables = page.find_tables()
                
                for table_num, table_obj in enumerate(found_tables):
                    table_data = table_obj.extract()
                    
                    # Attempt to find a title immediately above the table
                    table_top = table_obj.bbox[1]
                    
                    # Create a crop box spanning 60 units above the table
                    top_bound = max(0, table_top - 60)
                    bottom_bound = max(top_bound + 1, table_top - 2)
                    crop_box = (0, top_bound, page.width, bottom_bound)
                    
                    sheet_name = ""
                    try:
                        title_crop = page.crop(crop_box)
                        title_text = title_crop.extract_text()
                        if title_text and title_text.strip():
                            # Grab the last line above the table as the title
                            lines = [line.strip() for line in title_text.strip().split('\n') if line.strip()]
                            if lines:
                                raw_name = lines[-1]
                                # Clean up characters that Excel does not allow in sheet names
                                clean_name = re.sub(r'[\[\]:\*\?/\\]', '', raw_name).strip()
                                # Excel sheet names must be <= 31 chars
                                sheet_name = clean_name[:31]
                    except ValueError:
                        pass
                        
                    if not sheet_name or len(sheet_name) < 3:
                        # Fallback to intelligent numbering if no semantic name is found
                        sheet_name = f"Page_{page_num+1}_T{table_num+1}"

                    # Clean up the table data (remove newlines from cells)
                    cleaned_table = []
                    for row in table_data:
                        cleaned_row = [str(cell).replace('\n', ' ') if cell is not None else '' for cell in row]
                        cleaned_table.append(cleaned_row)
                    
                    df = None
                    if cleaned_table and len(cleaned_table) > 1:
                        # Use first row as header 
                        df = pd.DataFrame(cleaned_table[1:], columns=cleaned_table[0])
                    elif cleaned_table and len(cleaned_table) == 1:
                        df = pd.DataFrame(cleaned_table)
                        
                    if df is not None:
                        # Handle duplicate sheet names across multiple pages
                        base_sheet_name = sheet_name
                        counter = 1
                        while any(name == sheet_name for name, _ in all_tables):
                            suffix = f"_{counter}"
                            sheet_name = f"{base_sheet_name[:31-len(suffix)]}{suffix}"
                            counter += 1
                            
                        all_tables.append((sheet_name, df))

            if not all_tables:
                print(f"No tables found in {pdf_path}")
                return False

            print(f"Found {len(all_tables)} table(s). Saving to {output_excel_path}...")
            
            # Write all tables to different sheets in the same Excel file
            with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
                for sheet_name, df in all_tables:
                    # Excel worksheet names are limited to 31 characters
                    safe_sheet_name = sheet_name[:31]
                    df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
                    
            print(f"Done! Saved to {output_excel_path}")
            return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        pdf_file = input("Please enter the path or name of the PDF file to convert: ").strip()
        if not pdf_file:
            print("No file provided. Exiting.")
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
        
    extract_tables_to_excel(pdf_file, excel_file)
