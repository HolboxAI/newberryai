import unittest
from newberryai.PII_extractor import PII_extraction

class TestPIIExtraction(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.extractor = PII_extraction()

    def test_start_gradio(self):
        """Test the start_gradio method."""
        try:
            self.extractor.start_gradio()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"start_gradio failed with error: {str(e)}")

    def test_ask_method(self):
        """Test PII extraction functionality."""
        test_texts = [
            "John Doe lives at 123 Main St, New York",
            "Contact: jane.smith@email.com, (555) 123-4567",
            "Patient ID: 12345, DOB: 01/01/1990"
        ]
        
        for text in test_texts:
            response = self.extractor.ask(text)
            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)
            print(f"\nText: {text}")
            print(f"Extracted PII: {response}")

if __name__ == '__main__':
    unittest.main()
