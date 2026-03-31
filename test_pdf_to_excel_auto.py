import unittest
import os
import pandas as pd
from pdf_to_excel import extract_tables_to_excel
from create_dummy_pdf import create_pdf_with_table

class TestPDFToExcel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a dummy PDF for testing
        cls.test_pdf = "test_table_auto.pdf"
        cls.test_excel = "test_output_auto.xlsx"
        create_pdf_with_table(cls.test_pdf)

    @classmethod
    def tearDownClass(cls):
        # Clean up files after testing
        for file in [cls.test_pdf, cls.test_excel]:
            if os.path.exists(file):
                os.remove(file)

    def test_extraction(self):
        # Run the extraction programmatically
        result = extract_tables_to_excel(self.test_pdf, self.test_excel)
        self.assertTrue(result, "Extraction function should return True on success")
        
        # Check that the Excel file was created
        self.assertTrue(os.path.exists(self.test_excel), "Excel file was not created")
        
        # Verify the contents of the Excel file
        df = pd.read_excel(self.test_excel, sheet_name=0)
        
        # Our dummy table has 3 columns and 3 data rows
        self.assertEqual(df.shape, (3, 3), "Data frame should have 3 rows and 3 columns")
        
        # Check one of the headers and values
        self.assertIn('Header 1', df.columns)
        self.assertEqual(df.iloc[0]['Header 1'], 'Row 1, Col 1')

if __name__ == "__main__":
    unittest.main()
