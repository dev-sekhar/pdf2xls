import pdfplumber
import pandas as pd
import sys
import os

def extract_tables_to_excel(pdf_path, output_excel_path):
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return False

    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_tables = []
            
            for page_num, page in enumerate(pdf.pages):
                # Extract tables from the page
                tables = page.extract_tables()
                
                for table_num, table in enumerate(tables):
                    # Clean up the table data (remove newlines from cells)
                    cleaned_table = []
                    for row in table:
                        cleaned_row = [str(cell).replace('\n', ' ') if cell is not None else '' for cell in row]
                        cleaned_table.append(cleaned_row)
                    
                    if cleaned_table and len(cleaned_table) > 1:
                        # Use first row as header 
                        df = pd.DataFrame(cleaned_table[1:], columns=cleaned_table[0])
                        all_tables.append((f"Page_{page_num+1}_Table_{table_num+1}", df))
                    elif cleaned_table and len(cleaned_table) == 1:
                        df = pd.DataFrame(cleaned_table)
                        all_tables.append((f"Page_{page_num+1}_Table_{table_num+1}", df))

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
    else:
        pdf_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        excel_file = sys.argv[2]
    else:
        # Default output name
        base_name = os.path.splitext(pdf_file)[0]
        excel_file = f"{base_name}_tables.xlsx"
        
    extract_tables_to_excel(pdf_file, excel_file)
