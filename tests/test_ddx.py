import unittest
from newberryai.ddx import DDxChat

class TestDDxChat(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.ddx = DDxChat()

    def test_start_gradio(self):
        """Test the start_gradio method."""
        try:
            self.ddx.start_gradio()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"start_gradio failed with error: {str(e)}")

    def test_ask_method(self):
        """Test asking questions about differential diagnosis."""
        test_questions = [
            "Patient presents with fever and cough",
            "What are the possible causes of chest pain?",
            "Differential diagnosis for headache"
        ]
        
        for question in test_questions:
            response = self.ddx.ask(question)
            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)
            print(f"\nQuestion: {question}")
            print(f"Response: {response}")

if __name__ == '__main__':
    unittest.main()
