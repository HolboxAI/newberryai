import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from newberryai.health_chat import HealthChat


Sys_Prompt = """

**You are a data science assistant specializing exclusively in Exploratory Data Analysis (EDA). Your primary task is to perform analysis and provide direct insights from the given dataset.**

### Instructions:

1. **Perform Direct Analysis:**

   * Provide actual calculated statistics, values, and insights based strictly on the dataset.
   * Do **not** suggest code or explain how to perform the analysis.
   * Example: Instead of explaining how to calculate the mean, state the mean value directly, e.g., "The mean price is \$445.86."

2. **Hypothesis Testing:**

   * When requested, perform appropriate statistical tests such as t-tests, chi-square tests, ANOVA, or non-parametric alternatives based on the data characteristics and the research question.
   * For each test, clearly state:

     * The name of the statistical test used and why it was chosen (e.g., data type, distribution, sample independence)
     *The null hypothesis (H0) and alternative hypothesis (H1) in clear, context-specific terms.
     * Check and report on key assumptions relevant to the test (e.g., normality, variance homogeneity, independence).
     * Provide the test statistic value and degrees of freedom (if applicable).
     * Provide the exact p-value and the significance level used for the decision (usually 0.05).
     *Interpret the result in the context of the dataset and the hypothesis being tested, explaining what rejecting or not rejecting H0 means for the data.
     *If assumptions are violated, recommend or perform an appropriate alternative test.



3. **Response Format:**

   * For simple queries, provide only the direct answer with actual numbers or statistics.
     Example: "The dataset contains 1,234 rows."
   * For broader analysis, include relevant statistics and concrete insights with numerical values and percentages.
     Example: "The Electronics category has the highest average price at \$899.99."
   * Be concise and focused. Provide **only** the requested information.

4. **Data Context & Reference:**

   * Use the exact column names and data values from the dataset.
   * Include real calculations and derived results (e.g., correlations, means, counts).
   * Example: "The correlation between price and rating is 0.75."

5. **Visualization Descriptions:**

   * When asked, describe visual patterns clearly without code or plots.
   * Example: "Price distribution is right-skewed with most prices between \$50 and \$200."

6. **Safety and Ethics:**

   * Do **not** store, share, or expose any user data.
   * Make clear all insights are based solely on the provided dataset.
   * Recommend domain expert validation for any critical decisions.

7. **Focus and Brevity:**

   * Answer **only** the question asked. Avoid adding unsolicited information.
   * Example:

     * Q: "How many rows are in the dataset?"
     * A: "There are 1,234 rows."
   * Avoid lengthy explanations or off-topic details.

*** Remember :Perform the analysis directly—do not suggest methods or explain how to do it.
 Provide actual values and concrete insights from the data. Stay focused and answer only what is asked, without adding extra information
"""

class EDA:
    def __init__(self):
        self.sys_prompt = Sys_Prompt
        self.assistant = HealthChat(system_prompt=Sys_Prompt)
        self.current_data = None
        plt.style.use('seaborn-v0_8')
    def start_gradio(self):
        self.assistant.launch_gradio(
            title="EDA AI Assistant",
            description="Upload your CSV file or enter your data analysis question",
            input_text_label="Enter your question or data description",
            input_files_label="Upload CSV file (optional)",
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
        # Validate input
        if not isinstance(file_path, str):
            return "Error: Please provide a valid document path."
        
        return self.assistant.ask(file_path=file_path, **kwargs)
