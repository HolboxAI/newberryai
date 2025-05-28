import unittest
from newberryai.debugger import CodeReviewAssistant

class TestCodeReviewAssistant(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.debugger = CodeReviewAssistant()

    def test_start_gradio(self):
        """Test the start_gradio method."""
        try:
            self.debugger.start_gradio()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"start_gradio failed with error: {str(e)}")

    def test_ask_method(self):
        """Test code review functionality."""
        test_codes = [
            "def hello(): print('world')",
            "for i in range(10): print(i)",
            "def calculate_sum(a, b): return a + b"
        ]
        
        for code in test_codes:
            response = self.debugger.ask(code)
            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)
            print(f"\nCode: {code}")
            print(f"Response: {response}")

if __name__ == '__main__':
    unittest.main()
