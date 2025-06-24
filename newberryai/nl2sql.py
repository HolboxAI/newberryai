import pandas as pd
import decimal
import json
import datetime
import mysql.connector
from typing import Optional, Dict, Any, List, Tuple
from dotenv import load_dotenv
import gradio as gr
import os
import openai  # Add OpenAI for NL2SQL conversion

# Load environment variables
load_dotenv()

class NL2SQL:
    """
    A class for Natural Language to SQL conversion.
    This class provides functionality to convert natural language questions to SQL queries,
    execute them, and provide results with summaries.
    """
    
    def __init__(self):
        """Initialize the NL2SQL processor with default configuration."""
        self.host = None
        self.user = None
        self.password = None
        self.database = None
        self.port = 3306
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

    def connect_to_database(self, host: str, user: str, password: str, database: str, port: int = 3306) -> None:
        """
        Connect to the MySQL database and fetch schema information.
        """
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            self.host = host
            self.user = user
            self.password = password
            self.database = database
            self.port = port
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

Return only the raw SQL query without any markdown formatting, code blocks, or explanation."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Convert natural language questions to SQL queries. Return only the raw SQL query without any markdown formatting, code blocks, or explanation."},
                    {"role": "user", "content": prompt}
                ]
            )
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up any markdown formatting
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            
            return sql_query
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
            # Convert decimal and datetime objects for JSON serialization
            for row in results:
                for key, value in row.items():
                    if isinstance(value, decimal.Decimal):
                        row[key] = float(value)
                    elif isinstance(value, datetime.datetime):
                        row[key] = value.isoformat()
            return results
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")

    def generate_summary(self, df: pd.DataFrame) -> str:
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

    def process_query(self, question: str) -> Dict[str, Any]:
        """
        Process natural language question and return full response.
        
        Args:
            question (str): The natural language question to process
            
        Returns:
            Dict[str, Any]: Complete response with SQL, data, and summary
        """
        try:
            # Generate SQL
            sql_query = self.generate_sql(question)
            if not sql_query:
                return {
                    "success": False,
                    "message": "SQL query generation failed",
                    "sql_query": None,
                    "data": [],
                    "summary": "Failed to generate SQL query"
                }

            # Execute query
            result_data = self.execute_query(sql_query)
            if not result_data:
                return {
                    "success": True,
                    "message": "Query executed successfully but returned no data",
                    "sql_query": sql_query,
                    "data": [],
                    "summary": "No data available for this query."
                }

            # Convert to DataFrame for summary generation
            df = pd.DataFrame(result_data)

            # Generate summary
            summary = self.generate_summary(df)

            return {
                "success": True,
                "message": "Query processed successfully",
                "sql_query": sql_query,
                "data": result_data,
                "summary": summary
            }

        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "sql_query": None,
                "data": [],
                "summary": f"Error occurred: {str(e)}"
            }

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
                                 database: str, port: int) -> Tuple[str, str, str]:
            """Gradio interface function for NL2SQL processing"""
            try:
                self.connect_to_database(
                    host=host,
                    user=user,
                    password=password,
                    database=database,
                    port=port
                )
                
                response = self.process_query(question)
                return (
                    response["sql_query"] or "",
                    json.dumps(response["data"], indent=2),
                    response["summary"]
                )
            except Exception as e:
                return (
                    "",
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
            
            self.connect_to_database(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
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
                response = self.process_query(question)
                
                print("\nResults:")
                if response["success"]:
                    print(f"Generated SQL: {response['sql_query']}")
                    print(f"Data: {json.dumps(response['data'], indent=2)}")
                    print(f"Summary: {response['summary']}")
                else:
                    print(f"Error: {response['message']}")
                
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    nl2sql = NL2SQL()
    nl2sql.run_cli()
