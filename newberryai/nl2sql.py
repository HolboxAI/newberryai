import pandas as pd
import decimal
import json
import datetime
import mysql.connector
from typing import Optional, Dict, Any, List, Tuple
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import gradio as gr
import os
import openai  # Add OpenAI for NL2SQL conversion

# Load environment variables
load_dotenv()

class DatabaseConfig(BaseModel):
    """Configuration for database connection"""
    host: str
    user: str
    password: str
    database: str
    port: int = 3306

class NL2SQLRequest(BaseModel):
    """Request model for NL2SQL processing"""
    question: str = Field(..., min_length=1, description="Natural language question to convert to SQL")
    db_config: Optional[DatabaseConfig] = None

class NL2SQLResponse(BaseModel):
    """Response model for NL2SQL processing"""
    generated_sql: Optional[str] = None
    data: List[Dict[str, Any]] = []
    best_chart: Optional[str] = None
    selected_columns: Dict[str, Any] = {}
    summary: str = ""

def decimal_to_float(obj):
    """Convert decimal objects to float for JSON serialization"""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

class NL2SQL:
    """
    A class for Natural Language to SQL conversion with visualization and summarization.
    This class provides functionality to convert natural language questions to SQL queries,
    execute them, and generate visualizations and summaries.
    """
    
    def __init__(self):
        """Initialize the NL2SQL processor with default configuration."""
        self.db_config = None
        self.connection = None
        self.schema_info = None
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI()

    def get_database_schema(self) -> Dict[str, Any]:
        """
        Get database schema information including tables and columns.
        """
        if not self.connection:
            raise Exception("No database connection established")

        schema_info = {}
        cursor = self.connection.cursor(dictionary=True)
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = list(table.values())[0]
            # Get column information
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            schema_info[table_name] = {
                'columns': [col['Field'] for col in columns],
                'types': {col['Field']: col['Type'] for col in columns}
            }
        
        cursor.close()
        return schema_info

    def connect_to_database(self, config: DatabaseConfig) -> None:
        """
        Connect to the MySQL database and fetch schema information.
        """
        try:
            self.connection = mysql.connector.connect(
                host=config.host,
                user=config.user,
                password=config.password,
                database=config.database,
                port=config.port
            )
            self.db_config = config
            # Fetch schema information after connection
            self.schema_info = self.get_database_schema()
        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")

    def generate_sql(self, question: str) -> str:
        """
        Generate SQL query from natural language question using OpenAI.
        """
        if not self.schema_info:
            raise Exception("Database schema not loaded")

        # Create schema description for the prompt
        schema_description = "Database Schema:\n"
        for table, info in self.schema_info.items():
            schema_description += f"\nTable: {table}\n"
            schema_description += "Columns:\n"
            for col, col_type in info['types'].items():
                schema_description += f"- {col} ({col_type})\n"

        # Create prompt for OpenAI
        prompt = f"""Given the following database schema:
{schema_description}

Convert this natural language question to SQL:
{question}

Return only the SQL query without any explanation."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Convert natural language questions to SQL queries."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Failed to generate SQL: {str(e)}")

    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results.
        
        Args:
            sql_query (str): SQL query to execute
            
        Returns:
            List[Dict[str, Any]]: Query results
            
        Raises:
            Exception: If query execution fails
        """
        if not self.connection:
            raise Exception("No database connection established")

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(sql_query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")

    def suggest_chart(self, question: str, df: pd.DataFrame) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        """
        Suggest appropriate chart type based on data and question.
        """
        if df.empty:
            return None, {}, {}

        # Analyze data types
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        date_cols = df.select_dtypes(include=['datetime64']).columns

        # Determine chart type based on data and question
        if len(numeric_cols) >= 2:
            return "scatter", {"x": numeric_cols[0], "y": numeric_cols[1]}, {"title": "Scatter Plot"}
        elif len(numeric_cols) == 1 and len(categorical_cols) >= 1:
            return "bar", {"x": categorical_cols[0], "y": numeric_cols[0]}, {"title": "Bar Chart"}
        elif len(date_cols) >= 1 and len(numeric_cols) >= 1:
            return "line", {"x": date_cols[0], "y": numeric_cols[0]}, {"title": "Time Series"}
        else:
            return "table", {}, {"title": "Data Table"}

    def generate_summary(self, question: str, sql_query: str, df: pd.DataFrame) -> str:
        """
        Generate meaningful summary of the query results.
        """
        if df.empty:
            return "No data found for your query."

        # Basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        summary_parts = []

        if len(numeric_cols) > 0:
            for col in numeric_cols:
                summary_parts.append(f"{col}: min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}")

        # Count for categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            for col in categorical_cols:
                summary_parts.append(f"{col}: {df[col].nunique()} unique values")

        return f"Found {len(df)} results. " + ". ".join(summary_parts)

    def process_query(self, request: NL2SQLRequest) -> NL2SQLResponse:
        """
        Process natural language question and return full response.
        
        Args:
            request (NL2SQLRequest): The NL2SQL request parameters
            
        Returns:
            NL2SQLResponse: Complete response with SQL, data, chart, and summary
        """
        try:
            # Connect to database if config provided
            if request.db_config:
                self.connect_to_database(request.db_config)

            # Generate SQL
            sql_query = self.generate_sql(request.question)
            if not sql_query:
                raise Exception("SQL query generation failed")

            # Execute query
            result_data = self.execute_query(sql_query)
            if not result_data:
                return NL2SQLResponse(
                    generated_sql=sql_query,
                    data=[],
                    best_chart=None,
                    selected_columns={},
                    summary="No data available for this query."
                )

            # Convert to DataFrame
            df = pd.DataFrame(result_data)

            # Suggest chart
            best_chart, selected_columns, other_settings = self.suggest_chart(request.question, df)

            # Generate summary
            summary = self.generate_summary(request.question, sql_query, df)

            return NL2SQLResponse(
                generated_sql=sql_query,
                data=result_data,
                best_chart=best_chart,
                selected_columns=selected_columns,
                summary=summary
            )

        except Exception as e:
            return NL2SQLResponse(
                generated_sql=None,
                data=[],
                best_chart=None,
                selected_columns={},
                summary=f"Error occurred: {str(e)}"
            )

    def start_gradio(self):
        """
        Start a Gradio interface for NL2SQL processing.
        This provides a web-based UI for natural language to SQL conversion.
        """
        # Load environment variables for default values in Gradio interface
        default_host = os.getenv("DB_HOST", "localhost")
        default_user = os.getenv("DB_USER", "")
        default_password = os.getenv("DB_PASSWORD", "")
        default_database = os.getenv("DB_NAME", "")
        default_port = int(os.getenv("DB_PORT", 3306))

        def process_query_interface(question: str, host: str, user: str, password: str, 
                                 database: str, port: int) -> Tuple[Optional[str], str, Optional[str], str, str]:
            """Gradio interface function for NL2SQL processing"""
            try:
                db_config = DatabaseConfig(
                    host=host,
                    user=user,
                    password=password,
                    database=database,
                    port=port
                )
                
                request = NL2SQLRequest(
                    question=question,
                    db_config=db_config
                )
                
                response = self.process_query(request)
                return (
                    response.generated_sql,
                    json.dumps(response.data, indent=2, default=decimal_to_float),
                    response.summary
                )
            except Exception as e:
                return (
                    None,
                    "[]",
                    f"Error: {str(e)}"
                )

        # Create Gradio interface
        with gr.Blocks(title="NL2SQL Processor") as interface:
            gr.Markdown("# Natural Language to SQL Converter")
            
            with gr.Row():
                with gr.Column():
                    question = gr.Textbox(label="Enter your question", placeholder="Ask a question about your data...")
                    
                    gr.Markdown("### Database Configuration")
                    host = gr.Textbox(label="Host", value=default_host)
                    user = gr.Textbox(label="Username", value=default_user)
                    password = gr.Textbox(label="Password", type="password", value=default_password)
                    database = gr.Textbox(label="Database Name", value=default_database)
                    port = gr.Number(label="Port", value=default_port)
                    
                    process_button = gr.Button("Process Query")
            
            with gr.Row():
                with gr.Column():
                    sql_output = gr.Textbox(label="Generated SQL Query")
                    data_output = gr.Textbox(label="Query Results")
                    summary_output = gr.Textbox(label="Summary")
            
            process_button.click(
                fn=process_query_interface,
                inputs=[question, host, user, password, database, port],
                outputs=[sql_output, data_output, summary_output]
            )
        
        return interface.launch(share=True)

    def run_cli(self):
        """
        Run an interactive command-line interface for NL2SQL processing.
        """
        print("NL2SQL Processor initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        print("\nFirst, let's set up the database connection:")
        
        try:
            host = input("Database host [localhost]: ") or "localhost"
            user = input("Username: ")
            password = input("Password: ")
            database = input("Database name: ")
            port = int(input("Port [3306]: ") or "3306")
            
            db_config = DatabaseConfig(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            
            self.connect_to_database(db_config)
            print("\nDatabase connection established successfully!")
            
        except Exception as e:
            print(f"Error setting up database connection: {str(e)}")
            return
        
        print("\nYou can now ask questions about your data.")
        print("Example: 'Show me the total sales by region'")
        
        while True:
            question = input("\nEnter your question: ")
            if question.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            try:
                request = NL2SQLRequest(question=question)
                response = self.process_query(request)
                
                print("\nResults:")
                print(f"Generated SQL: {response.generated_sql}")
                print(f"Data: {json.dumps(response.data, indent=2)}")
                print(f"Summary: {response.summary}")
                
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    nl2sql = NL2SQL()
    nl2sql.run_cli()
