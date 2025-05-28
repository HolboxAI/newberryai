import unittest
import os
import pandas as pd
import numpy as np
from newberryai.cli import main
from unittest.mock import patch
from PIL import Image

class TestCLI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create test data files
        self.test_csv = 'test_data.csv'
        self.test_pdf = 'test_doc.pdf'
        self.test_image = 'test_bill.jpg'
        self.test_data = pd.DataFrame({
            'numeric_col': np.random.randn(10),
            'categorical_col': ['A', 'B', 'C'] * 3 + ['A'],
            'date_col': pd.date_range(start='2023-01-01', periods=10)
        })
        self.test_data.to_csv(self.test_csv, index=False)
        
        # Create a dummy PDF file
        with open(self.test_pdf, 'w') as f:
            f.write('Test PDF content')
            
        # Create a dummy image file
        img = Image.new('RGB', (100, 100), color='white')
        img.save(self.test_image)

    def tearDown(self):
        """Clean up after each test method."""
        # Remove test files
        for file in [self.test_csv, self.test_pdf, self.test_image]:
            if os.path.exists(file):
                os.remove(file)

    def test_eda_command(self):
        """Test EDA command functionality."""
        with patch('sys.argv', ['newberryai', 'eda', '--file_path', self.test_csv]):
            with patch('builtins.print') as mock_print:
                main()
                mock_print.assert_any_call(f"Loaded dataset: {self.test_csv}")

    def test_pdf_summarizer_command(self):
        """Test PDF summarizer command functionality."""
        with patch('sys.argv', ['newberryai', 'pdf_summarizer', '--file_path', self.test_pdf]):
            with patch('builtins.print') as mock_print:
                main()
                mock_print.assert_any_call(f"Analyzing document: {self.test_pdf}")

    def test_pii_extractor_command(self):
        """Test PII extractor command functionality."""
        test_text = "John Doe lives at 123 Main St, New York"
        with patch('sys.argv', ['newberryai', 'PII_extract', '--text', test_text]):
            with patch('builtins.print') as mock_print:
                main()
                self.assertTrue(any('PII' in str(call) for call in mock_print.call_args_list))

    def test_pii_redactor_command(self):
        """Test PII redactor command functionality."""
        test_text = "John Doe lives at 123 Main St, New York"
        with patch('sys.argv', ['newberryai', 'PII_Red', '--text', test_text]):
            with patch('builtins.print') as mock_print:
                main()
                self.assertTrue(any('Redacted' in str(call) for call in mock_print.call_args_list))

    def test_medical_bill_extractor_command(self):
        """Test medical bill extractor command functionality."""
        with patch('sys.argv', ['newberryai', 'bill_extract', '--file_path', self.test_image]):
            with patch('builtins.print') as mock_print:
                main()
                mock_print.assert_any_call(f"Analyzing medical bill image: {self.test_image}")

    def test_ddx_command(self):
        """Test differential diagnosis command functionality."""
        test_question = "Patient presents with fever and cough"
        with patch('sys.argv', ['newberryai', 'ddx', '--clinical_indication', test_question]):
            with patch('builtins.print') as mock_print:
                main()
                mock_print.assert_any_call(f"Question: {test_question}")

    def test_debugger_command(self):
        """Test code debugger command functionality."""
        test_code = "def hello(): print('world')"
        with patch('sys.argv', ['newberryai', 'Coder', '--code_query', test_code]):
            with patch('builtins.print') as mock_print:
                main()
                mock_print.assert_any_call(f"Question: {test_code}")

    def test_excel_command(self):
        """Test Excel formula command functionality."""
        test_query = "How to sum values in column A"
        with patch('sys.argv', ['newberryai', 'ExcelO', '--Excel_query', test_query]):
            with patch('builtins.print') as mock_print:
                main()
                mock_print.assert_any_call(f"Question: {test_query}")

if __name__ == '__main__':
    unittest.main()
