import unittest
import os
import pandas as pd
import numpy as np
from newberryai.eda import EDA
from unittest.mock import patch

class TestEDACLI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.eda = EDA()
        # Create a temporary test CSV file
        self.test_data = pd.DataFrame({
            'numeric_col': np.random.randn(10),
            'categorical_col': ['A', 'B', 'C'] * 3 + ['A'],
            'date_col': pd.date_range(start='2023-01-01', periods=10)
        })
        self.test_file = 'test_data.csv'
        self.test_data.to_csv(self.test_file, index=False)

    def tearDown(self):
        """Clean up after each test method."""
        # Remove the temporary test file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_file_loading(self):
        """Test loading a CSV file through the CLI."""
        
        # Test loading the file
        self.eda.current_data = pd.read_csv(self.test_file)
        self.assertEqual(self.eda.current_data.shape, (10, 3))
        self.assertListEqual(list(self.eda.current_data.columns), 
                           ['numeric_col', 'categorical_col', 'date_col'])

    def test_visualization_commands(self):
        """Test visualization commands with actual data."""
        self.eda.current_data = self.test_data
        
        # Test all visualization types
        viz_types = [None, 'dist', 'corr', 'cat', 'time']
        for viz_type in viz_types:
            result = self.eda.visualize_data(viz_type)
            self.assertIsInstance(result, str)
            # Verify we get a response message
            self.assertTrue(len(result) > 0)
            print(f"Visualization type {viz_type}: {result}")

    def test_ask_method(self):
        """Test asking questions about the data."""
        self.eda.current_data = self.test_data
        
        # Test basic questions
        questions = [
            "What is the shape of the data?",
            "What are the column names?",
            "Show me the summary statistics"
        ]
        
        for question in questions:
            response = self.eda.ask(question)
            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)
            if response:
                print(response)

    def test_start_gradio(self):
        """Test the start_gradio method."""
        try:
            # This will actually launch the Gradio interface
            self.eda.start_gradio()
            # If we reach here, the interface launched successfully
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"start_gradio failed with error: {str(e)}")

    def test_run_cli_actual(self):
        """Test the actual run_cli method with real CLI interaction."""
        # First load the test data
        self.eda.current_data = pd.read_csv(self.test_file)
        
        # Test the CLI initialization messages
        with patch('builtins.print') as mock_print:
            self.eda.run_cli()
            # Verify initialization messages
            mock_print.assert_any_call("EDA AI Assistant initialized")
            mock_print.assert_any_call("Type 'exit' or 'quit' to end the conversation.")
            mock_print.assert_any_call("To analyze a CSV file, type 'file:' followed by the path to your CSV file")

        # Test file loading through CLI
        with patch('builtins.input', side_effect=['file:test_data.csv', 'exit']):
            with patch('builtins.print') as mock_print:
                self.eda.run_cli()
                mock_print.assert_any_call("Successfully loaded CSV file: test_data.csv")
                mock_print.assert_any_call("Dataset shape: (10, 3)")

        # Test visualization commands
        with patch('builtins.input', side_effect=['visualize', 'exit']):
            with patch('builtins.print') as mock_print:
                self.eda.run_cli()
                mock_print.assert_any_call("Visualizations have been generated. Check the plots window.")

        # Test asking questions
        with patch('builtins.input', side_effect=['What is the shape of the data?', 'exit']):
            with patch('builtins.print') as mock_print:
                self.eda.run_cli()
                # Verify that the assistant responded
                self.assertTrue(any('EDA Assistant:' in str(call) for call in mock_print.call_args_list))

        # Test exit command
        with patch('builtins.input', return_value='exit'):
            with patch('builtins.print') as mock_print:
                self.eda.run_cli()
                mock_print.assert_any_call("Goodbye!")


if __name__ == '__main__':
    unittest.main()
