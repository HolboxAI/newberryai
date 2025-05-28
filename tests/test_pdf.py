import unittest
import os
from newberryai.pdf_summarizer import DocSummarizer

class TestDocSummarizer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.summarizer = DocSummarizer()
        # Create a test PDF
        self.test_pdf = 'test_doc.pdf'
        with open(self.test_pdf, 'w') as f:
            f.write('Test PDF content')

    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_pdf):
            os.remove(self.test_pdf)

    def test_start_gradio(self):
        """Test the start_gradio method."""
        try:
            self.summarizer.start_gradio()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"start_gradio failed with error: {str(e)}")

    def test_ask_method(self):
        """Test document summarization."""
        response = self.summarizer.ask(self.test_pdf)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
        print(f"\nSummary: {response}")

if __name__ == '__main__':
    unittest.main()
