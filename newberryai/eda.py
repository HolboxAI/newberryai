import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from newberryai.health_chat import HealthChat


Sys_Prompt = """
You are a data science assistant specialized in Exploratory Data Analysis (EDA). Your primary role is to PERFORM analysis, not suggest code.

1. DIRECT ANALYSIS:
- When asked for analysis, PERFORM the actual analysis using the provided data
- Show actual values, statistics, and insights from the data
- DO NOT suggest code or explain how to do the analysis
- Example: Instead of suggesting code for mean calculation, show the actual mean value

2. HYPOTHESIS TESTING:
- You can perform statistical hypothesis tests (e.g., t-test, chi-square, ANOVA, etc.) on the dataset when requested
- Clearly state the test performed, the hypothesis, the test statistic, p-value, and interpretation of the result

3. SQL QUERIES:
- You can execute SQL queries directly on the loaded dataset when requested
- Show the actual query result as a table or summary, not the code

4. RESPONSE FORMAT:
For simple queries:
- Direct answer with actual values
- Example: "The mean price is $445.86"

For analysis requests:
- Show actual statistics and values
- Present real insights from the data
- Include actual numbers and percentages
- Example: "Electronics category has the highest average price at $899.99"

5. DATA CONTEXT:
- Use the provided dataset information
- Reference actual column names and values
- Show real calculations and results
- Example: "The correlation between price and rating is 0.75"

6. VISUALIZATION REQUESTS:
- When asked for visualizations, describe the actual patterns
- Example: "The price distribution shows a right-skew with most products priced between $50-$200"

7. SAFETY AND ETHICS:
- Never store or share user data
- Clarify that insights are based on the current dataset
- Recommend validation through domain expertise

Remember: PERFORM the analysis, don't suggest how to do it. Show actual values and insights from the data.
"""

class EDA:
    def __init__(self):
        self.sys_prompt = Sys_Prompt
        self.assistant = HealthChat(system_prompt=Sys_Prompt)
        self.current_data = None
        self.analysis_results = {}
        plt.style.use('seaborn-v0_8')
    def start_gradio(self):
        self.assistant.launch_gradio(
            title="EDA AI Assistant",
            description="Upload your CSV file or enter your data analysis question",
            input_text_label="Enter your question or data description",
            input_image_label="Upload CSV file (optional)",
            output_label="EDA Analysis"
        )  
    def visualize_data(self, plot_type=None):
        """Generate visualizations for the dataset"""
        if self.current_data is None:
            return "No dataset loaded. Please load a CSV file first."

        if plot_type is None:
            # Generate all visualizations
            self._plot_distributions()
            self._plot_correlations()
            self._plot_categorical()
            self._plot_time_series()
            return "Visualizations have been generated. Check the plots window."
        elif plot_type == "dist":
            return self._plot_distributions()
        elif plot_type == "corr":
            return self._plot_correlations()
        elif plot_type == "cat":
            return self._plot_categorical()
        elif plot_type == "time":
            return self._plot_time_series()
        else:
            return f"Unknown plot type: {plot_type}. Available types: dist, corr, cat, time"

    def _plot_distributions(self):
        """Plot distributions of numeric columns"""
        numeric_cols = self.current_data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return "No numeric columns found for distribution plots."

        n_cols = len(numeric_cols)
        fig, axes = plt.subplots(n_cols, 2, figsize=(15, 5*n_cols))
        if n_cols == 1:
            axes = axes.reshape(1, -1)

        for idx, col in enumerate(numeric_cols):
            # Histogram
            sns.histplot(data=self.current_data, x=col, ax=axes[idx, 0])
            axes[idx, 0].set_title(f'Distribution of {col}')
            
            # Scatter plot (index vs. value)
            axes[idx, 1].scatter(self.current_data.index, self.current_data[col], alpha=0.7)
            axes[idx, 1].set_title(f'Scatter Plot of {col} (Index vs. Value)')
            axes[idx, 1].set_xlabel('Index')
            axes[idx, 1].set_ylabel(col)

        plt.tight_layout()
        plt.show()
        return "Distribution and scatter plots generated."

    def _plot_correlations(self):
        """Plot correlation heatmap for numeric columns"""
        numeric_cols = self.current_data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return "Need at least 2 numeric columns for correlation plot."

        plt.figure(figsize=(10, 8))
        corr_matrix = self.current_data[numeric_cols].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('Correlation Heatmap')
        plt.tight_layout()
        plt.show()
        return "Correlation heatmap generated."

    def _plot_categorical(self):
        """Plot categorical data distributions"""
        cat_cols = self.current_data.select_dtypes(include=['object']).columns
        if len(cat_cols) == 0:
            return "No categorical columns found."

        n_cols = len(cat_cols)
        fig, axes = plt.subplots(n_cols, 1, figsize=(10, 5*n_cols))
        if n_cols == 1:
            axes = [axes]

        for idx, col in enumerate(cat_cols):
            value_counts = self.current_data[col].value_counts()
            sns.barplot(x=value_counts.index, y=value_counts.values, ax=axes[idx])
            axes[idx].set_title(f'Distribution of {col}')
            axes[idx].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.show()
        return "Categorical plots generated."

    def _plot_time_series(self):
        """Plot time series data if available"""
        date_cols = self.current_data.select_dtypes(include=['datetime64']).columns
        if len(date_cols) == 0:
            return "No datetime columns found for time series plots."

        numeric_cols = self.current_data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return "No numeric columns found for time series plots."

        for date_col in date_cols:
            plt.figure(figsize=(15, 5))
            for num_col in numeric_cols:
                plt.plot(self.current_data[date_col], self.current_data[num_col], label=num_col)
            plt.title(f'Time Series Plot for {date_col}')
            plt.xlabel(date_col)
            plt.ylabel('Value')
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()

        return "Time series plots generated."

    def run_cli(self):
        print("EDA AI Assistant initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        print("To analyze a CSV file, type 'file:' followed by the path to your CSV file")
        print("Example: file:path/to/your/data.csv")
        print("\nVisualization commands:")
        print("  - visualize or viz: Show all visualizations")
        print("  - visualize dist or viz dist: Show distribution plots")
        print("  - visualize corr or viz corr: Show correlation heatmap")
        print("  - visualize cat or viz cat: Show categorical plots")
        print("  - visualize time or viz time: Show time series plots")
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
                
            if user_input.startswith("file:"):
                file_path = user_input[5:].strip()
                try:
                    self.current_data = pd.read_csv(file_path)
                    print(f"Successfully loaded CSV file: {file_path}")
                    print(f"Dataset shape: {self.current_data.shape}")
                    print("You can now ask questions about the data.")
                except Exception as e:
                    print(f"Error loading CSV file: {str(e)}")
                continue
            
            # Handle visualization commands
            if any(user_input.lower().startswith(cmd) for cmd in ['visualize', 'viz', 'visual', 'v']):
                if self.current_data is not None:
                    # Extract plot type if specified
                    parts = user_input.lower().split()
                    plot_type = parts[1] if len(parts) > 1 else None
                    print(self.visualize_data(plot_type))
                else:
                    print("No dataset loaded. Please load a CSV file first.")
                continue
            
            # Process all other inputs through the HealthChat assistant
            answer = self.ask(user_input)
            print("\nEDA Assistant:", end=" ")
            print(answer)

    def ask(self, question, **kwargs):
        """
        Ask a question to the EDA assistant.
        
        Args:
            question (str): The question to process
            
        Returns:
            str: The assistant's response
        """
        # Enforce text-only input
        if not isinstance(question, str):
            return "Error: This EDA assistant only accepts text questions."
        
        # If we have data loaded, include it in the context
        if self.current_data is not None:
            # Create a comprehensive data summary
            data_info = {
                "shape": self.current_data.shape,
                "columns": list(self.current_data.columns),
                "dtypes": self.current_data.dtypes.to_dict(),
                "summary_stats": self.current_data.describe().to_dict(),
                "categorical_stats": {
                    col: self.current_data[col].value_counts().to_dict()
                    for col in self.current_data.select_dtypes(include=['object']).columns
                },
                "correlations": self.current_data.select_dtypes(include=[np.number]).corr().to_dict(),
                "missing_values": self.current_data.isnull().sum().to_dict()
            }
            
            # Convert the data summary to a string format
            data_context = f"""
Current dataset information:
- Shape: {data_info['shape']}
- Columns: {', '.join(data_info['columns'])}
- Data Types: {data_info['dtypes']}
- Summary Statistics: {data_info['summary_stats']}
- Categorical Statistics: {data_info['categorical_stats']}
- Correlations: {data_info['correlations']}
- Missing Values: {data_info['missing_values']}
"""
            question = data_context + "\n" + question
        
        # Use the ChatQA ask method with only the question parameter
        return self.assistant.ask(question=question, image_path=None, **kwargs)

