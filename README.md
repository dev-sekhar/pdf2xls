# pdf2xls

This module contains a Python utility that uses `pdfplumber` to extract tables from PDF documents and save them directly into multiple sheets of an Excel file.

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

## Environment Configuration

You can fully customize the script's behavior by modifying the root `.env` file!

- `ENVIRONMENT`: Marks the execution context (`development`, `production`, `testing`).
- `LOG_LEVEL`: Changes exactly how much logging the script generates on the console (`DEBUG`, `INFO`, `WARNING`, `ERROR`). Set this to `DEBUG` when actively debugging!

## How to execute

You can run the script using either the Graphical Interface (Web App) or the Command Line Interface (CLI):

### 1. Graphical UI (Web App)
You can launch a clean, interactive GUI right in your browser!
```bash
streamlit run app.py
```
This will open a page where you can upload your PDF directly, extract its tables, and click a button to download the resulting Excel file straight to your machine.

### 2. Interactive CLI Mode
Run the script without any arguments. It will prompt you to type in the name of your PDF file and the output directory:
```bash
python pdf_to_excel.py
```

### 3. Command Line Arguments
Pass the PDF filename (and optionally an output directory path) as command line arguments for quicker execution:
```bash
python pdf_to_excel.py your_document.pdf
```
```bash
# With a custom output folder:
python pdf_to_excel.py your_document.pdf "C:/My/Output/Folder/"
```

## Automated Testing

If you want to verify that the extraction logic is working as expected, an automated test suit is provided in `test_pdf_to_excel_auto.py`. 
You can run the test like this:
```bash
python -m unittest test_pdf_to_excel_auto.py
```
This test will generate a dummy PDF table on the fly and verify that it parses cleanly into Excel.
