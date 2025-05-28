import unittest
from newberryai.PII_masking import PII_Redaction

class TestPIIRedaction(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.redactor = PII_Redaction()

    def test_start_gradio(self):
        """Test the start_gradio method."""
        try:
            self.redactor.start_gradio()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"start_gradio failed with error: {str(e)}")

    def test_ask_method(self):
        """Test PII redaction functionality."""
        test_texts = [
            "John Doe lives at 123 Main St, New York",
            "Contact: jane.smith@email.com, (555) 123-4567",
            "Patient ID: 12345, DOB: 01/01/1990"
        ]
        
        for text in test_texts:
            response = self.redactor.ask(text)
            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)
            print(f"\nOriginal: {text}")
            print(f"Redacted: {response}")

if __name__ == '__main__':
    unittest.main()
