import argparse
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from newberryai.health_chat import HealthChat


Sys_Prompt = """
You are an Exploratory Data Analysis (EDA) assistant designed to help users understand their datasets. Your main tasks are:

1. Summarize the dataset's size, column types, and missing data.
2. Provide basic statistics for each column (means, counts, min/max, skewness).
3. Detect data issues like missing values, duplicates, outliers, and unusual entries.
4. Find and explain correlations between numeric columns.
5. Generate simple insights about the data patterns (e.g., skewed distributions, high cardinality).
6. Suggest useful visualizations (histograms, scatter plots, bar charts, heatmaps, time series).
7. Answer user questions clearly, referencing the data loaded and any previous analyses.

Always respond in a clear, concise, and organized way. Use bullet points and short paragraphs to help readability.

Remind users that these insights are preliminary and should be validated with further analysis and domain knowledge.

Never store or share user data outside this session.

If you receive a question without loaded data, ask the user to upload a CSV file first.

---

When responding, follow this structure:

- Dataset Summary: rows, columns, types, missing data  
- Descriptive Stats: key metrics by variable type  
- Data Quality: missing data, duplicates, outliers, inconsistencies  
- Correlations: numeric relationships  
- Insights: notable patterns and suggestions  
- Visualizations: recommend or generate plots  
- Disclaimer: remind this is exploratory, not final analysis  

"""

class EDA:
    def __init__(self):
        self.sys_prompt = Sys_Prompt
        self.assistant = HealthChat(system_prompt=Sys_Prompt)
        self.current_data = None
        self.analysis_results = {}
        plt.style.use('seaborn-v0_8')

    def analyze_dataset(self):
        """Perform comprehensive dataset analysis"""
        if self.current_data is None:
            return "No dataset loaded. Please load a CSV file first."

        results = {
            "structure": self._analyze_structure(),
            "descriptive_stats": self._generate_descriptive_stats(),
            "data_quality": self._check_data_quality(),
            "correlations": self._analyze_correlations(),
            "insights": self._generate_insights()
        }
        
        self.analysis_results = results
        return self._format_analysis_results(results)

    def _analyze_structure(self):
        """Analyze dataset structure"""
        return {
            "shape": self.current_data.shape,
            "dtypes": self.current_data.dtypes.to_dict(),
            "missing_values": self.current_data.isnull().sum().to_dict(),
            "memory_usage": self.current_data.memory_usage(deep=True).sum()
        }

    def _generate_descriptive_stats(self):
        """Generate descriptive statistics for all columns"""
        stats = {}
        
        for col in self.current_data.columns:
            if pd.api.types.is_numeric_dtype(self.current_data[col]):
                stats[col] = {
                    "type": "numeric",
                    "stats": self.current_data[col].describe().to_dict(),
                    "skewness": self.current_data[col].skew(),
                    "kurtosis": self.current_data[col].kurtosis()
                }
            elif pd.api.types.is_datetime64_dtype(self.current_data[col]):
                stats[col] = {
                    "type": "datetime",
                    "min": self.current_data[col].min(),
                    "max": self.current_data[col].max(),
                    "unique_dates": self.current_data[col].nunique()
                }
            else:
                stats[col] = {
                    "type": "categorical",
                    "unique_values": self.current_data[col].nunique(),
                    "value_counts": self.current_data[col].value_counts().to_dict()
                }
        
        return stats

    def _check_data_quality(self):
        """Check data quality issues"""
        quality_issues = {
            "missing_values": self.current_data.isnull().sum().to_dict(),
            "duplicates": self.current_data.duplicated().sum(),
            "outliers": self._detect_outliers(),
            "inconsistencies": self._check_inconsistencies()
        }
        return quality_issues

    def _detect_outliers(self):
        """Detect outliers in numeric columns"""
        outliers = {}
        for col in self.current_data.select_dtypes(include=[np.number]).columns:
            Q1 = self.current_data[col].quantile(0.25)
            Q3 = self.current_data[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers[col] = {
                "count": ((self.current_data[col] < (Q1 - 1.5 * IQR)) | 
                         (self.current_data[col] > (Q3 + 1.5 * IQR))).sum()
            }
        return outliers

    def _check_inconsistencies(self):
        """Check for data inconsistencies"""
        inconsistencies = {}
        for col in self.current_data.columns:
            if pd.api.types.is_numeric_dtype(self.current_data[col]):
                # Check for negative values where not expected
                if (self.current_data[col] < 0).any():
                    inconsistencies[col] = "Contains negative values"
            elif pd.api.types.is_datetime64_dtype(self.current_data[col]):
                # Check for future dates
                if (self.current_data[col] > datetime.now()).any():
                    inconsistencies[col] = "Contains future dates"
        return inconsistencies

    def _analyze_correlations(self):
        """Analyze correlations between numeric variables"""
        numeric_cols = self.current_data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = self.current_data[numeric_cols].corr()
            return {
                "pearson": corr_matrix.to_dict(),
                "spearman": self.current_data[numeric_cols].corr(method='spearman').to_dict()
            }
        return {}

    def _generate_insights(self):
        """Generate initial insights and hypotheses"""
        insights = []
        
        # Analyze numeric columns
        numeric_cols = self.current_data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            for col in numeric_cols:
                skewness = self.current_data[col].skew()
                if abs(skewness) > 1:
                    insights.append(f"{col} shows significant skewness ({skewness:.2f})")
        
        # Analyze categorical columns
        cat_cols = self.current_data.select_dtypes(include=['object']).columns
        for col in cat_cols:
            unique_ratio = self.current_data[col].nunique() / len(self.current_data)
            if unique_ratio > 0.5:
                insights.append(f"{col} has high cardinality ({unique_ratio:.2%} unique values)")
        
        return insights

    def _format_analysis_results(self, results):
        """Format analysis results into a readable string"""
        output = []
        
        # Dataset Structure
        output.append("=== Dataset Structure ===")
        output.append(f"Shape: {results['structure']['shape']}")
        output.append("\nData Types:")
        for col, dtype in results['structure']['dtypes'].items():
            output.append(f"- {col}: {dtype}")
        
        # Descriptive Statistics
        output.append("\n=== Descriptive Statistics ===")
        for col, stats in results['descriptive_stats'].items():
            output.append(f"\n{col} ({stats['type']}):")
            if stats['type'] == 'numeric':
                output.append(f"- Mean: {stats['stats']['mean']:.2f}")
                output.append(f"- Std: {stats['stats']['std']:.2f}")
                output.append(f"- Skewness: {stats['skewness']:.2f}")
            elif stats['type'] == 'categorical':
                output.append(f"- Unique values: {stats['unique_values']}")
        
        # Data Quality
        output.append("\n=== Data Quality Issues ===")
        for col, missing in results['data_quality']['missing_values'].items():
            if missing > 0:
                output.append(f"- {col}: {missing} missing values")
        if results['data_quality']['duplicates'] > 0:
            output.append(f"- {results['data_quality']['duplicates']} duplicate rows")
        
        # Insights
        output.append("\n=== Initial Insights ===")
        for insight in results['insights']:
            output.append(f"- {insight}")
        
        return "\n".join(output)

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
        print("To get comprehensive analysis, type 'analyze'")
        print("To visualize data, type 'visualize' or 'visualize [type]' where type is one of:")
        print("  - dist: distribution plots")
        print("  - corr: correlation heatmap")
        print("  - cat: categorical plots")
        print("  - time: time series plots")
        
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
                    print("You can now ask questions about the data or type 'analyze' for comprehensive analysis.")
                except Exception as e:
                    print(f"Error loading CSV file: {str(e)}")
                continue
            
            if user_input.lower() == "analyze":
                if self.current_data is not None:
                    print(self.analyze_dataset())
                else:
                    print("No dataset loaded. Please load a CSV file first.")
                continue

            if user_input.lower().startswith("visualize"):
                if self.current_data is not None:
                    plot_type = user_input.lower().split()[1] if len(user_input.split()) > 1 else None
                    print(self.visualize_data(plot_type))
                else:
                    print("No dataset loaded. Please load a CSV file first.")
                continue
                
            answer = self.ask(user_input)
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
            data_info = f"\nCurrent dataset info:\nShape: {self.current_data.shape}\nColumns: {', '.join(self.current_data.columns)}\n"
            if self.analysis_results:
                data_info += "\nPrevious analysis results:\n" + self._format_analysis_results(self.analysis_results)
            question = data_info + question
        
        # Use the ChatQA ask method with only the question parameter (no image)
        return self.assistant.ask(question=question, image_path=None, **kwargs)

