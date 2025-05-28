import unittest
from newberryai.ExcelO import ExcelExp

class TestExcelExp(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.excel = ExcelExp()

    def test_start_gradio(self):
        """Test the start_gradio method."""
        try:
            self.excel.start_gradio()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"start_gradio failed with error: {str(e)}")

    def test_ask_method(self):
        """Test Excel formula generation."""
        test_queries = [
            "How to sum values in column A",
            "Formula for calculating average",
            "How to use VLOOKUP"
        ]
        
        for query in test_queries:
            response = self.excel.ask(query)
            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)
            print(f"\nQuery: {query}")
            print(f"Response: {response}")

if __name__ == '__main__':
    unittest.main()
