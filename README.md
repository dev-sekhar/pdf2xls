# PDF to Excel Table Extractor

This module contains a Python script (`pdf_to_excel.py`) that uses `pdfplumber` to extract tables from PDF documents and save them directly into multiple sheets of an Excel file.

## Prerequisites

Before running the script, make sure you have the required Python modules installed. It is recommended to use a virtual environment.

```bash
# Set up virtual environment
python -m venv venv

# Activate it (on Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## How to execute

You can run the script in two ways:

### 1. Interactive Mode
Run the script without any arguments. It will prompt you to type in the name of your PDF file:
```bash
python pdf_to_excel.py
```
**Example output:**
```
Please enter the path or name of the PDF file to convert: ASM_41447.pdf
Found 1 table(s). Saving to ASM_41447_tables.xlsx...
Done! Saved to ASM_41447_tables.xlsx
```

### 2. Command Line Mode
Pass the PDF filename (and optionally an output Excel filename) as command line arguments for quicker execution:
```bash
python pdf_to_excel.py your_document.pdf
```
```bash
# With a custom output file name:
python pdf_to_excel.py your_document.pdf custom_output_name.xlsx
```

## Automated Testing

If you want to verify that the extraction logic is working as expected, an automated test suit is provided in `test_pdf_to_excel_auto.py`. 
You can run the test like this:
```bash
python -m unittest test_pdf_to_excel_auto.py
```
This test will generate a dummy PDF table on the fly and verify that it parses cleanly into Excel.
# pdf2xls
