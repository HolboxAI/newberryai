import unittest
import os
from newberryai.medical_bill_extractor import Bill_extractor
from PIL import Image

class TestBillExtractor(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.extractor = Bill_extractor()
        # Create a test image document
        self.test_doc = 'test_bill.jpg'
        img = Image.new('RGB', (100, 100), color='white')
        img.save(self.test_doc)

    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_doc):
            os.remove(self.test_doc)

    def test_start_gradio(self):
        """Test the start_gradio method."""
        try:
            self.extractor.start_gradio()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"start_gradio failed with error: {str(e)}")

    def test_analyze_document(self):
        """Test document analysis functionality."""
        response = self.extractor.analyze_document(self.test_doc)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
        print(f"\nAnalysis: {response}")

if __name__ == '__main__':
    unittest.main()
