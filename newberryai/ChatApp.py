import os
import json
import boto3
import gradio as gr


class ChatQA:
    """
    A class for interacting with AI models via AWS Bedrock.
    
    Attributes:
        region (str): AWS region name
        aws_access_key_id (str): AWS access key ID
        aws_secret_access_key (str): AWS secret access key
        model_id (str): Bedrock model ID to use
        max_tokens (int): Maximum number of tokens in the response
        system_prompt (str): System prompt to guide Chatbot's behavior
    """
    
    def __init__(
        self,
        system_prompt: str = "",
        region: str = "us-east-1",
        # aws_access_key_id: Optional[str] = None,
        # aws_secret_access_key: Optional[str] = None,
        model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0",
        max_tokens: int = 1000
    ):
        """
        Initialize the AI Assistant.
        
        Args:
            system_prompt (str): System prompt to guide Chatbot's behavior
            region (str): AWS region name, defaults to 'us-east-1'
            aws_access_key_id (str, optional): AWS access key ID. If None, tries to get from environment
            aws_secret_access_key (str, optional): AWS secret access key. If None, tries to get from environment
            model_id (str): Bedrock model ID to use
            max_tokens (int): Maximum number of tokens in the response
        """
        self.region = region
        self.aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            raise ValueError("AWS credentials not found. Please provide them or set environment variables.")
        
        self.runtime = boto3.client(
            "bedrock-runtime",
            region_name=self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
    
    def ask(self, question: str) -> str:
        """
        Send a question to Chatbot and get a response.
        
        Args:
            question (str): The question to ask Chatbot
            
        Returns:
            str: Chatbot's response text
        """
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.max_tokens,
            "system": self.system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }
            ]
        })
        
        try:
            response = self.runtime.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]["text"]
        except Exception as e:
            return f"Error: {str(e)}"
    
    def launch_gradio(
        self,
        title: str = "AI Assistant",
        description: str = "Ask Chatbot a question",
        input_label: str = "Your question",
        output_label: str = "AI's response",
        theme: str = "default",
        share: bool = True
    ) -> None:
        """
        Launch a Gradio interface for interacting with Chatbot.
        
        Args:
            title (str): Title of the Gradio interface
            description (str): Description of the Gradio interface
            input_label (str): Label for the input text box
            output_label (str): Label for the output text box
            theme (str): Gradio theme
            share (bool): Whether to create a public link
        """
        def gradio_callback(query: str) -> str:
            return self.ask(query)
        
        iface = gr.Interface(
            fn=gradio_callback,
            inputs=gr.Textbox(label=input_label),
            outputs=gr.Textbox(label=output_label),
            title=title,
            description=description,
            theme=theme
        )
        
        iface.launch(share=share)
    
    def run_cli(self) -> None:
        """
        Run a simple command-line interface.
        """
        print(f"Chatbot Assistant initialized with model: {self.model_id}")
        print("Type 'exit' or 'quit' to end the conversation.")
        
        while True:
            query = input("\nYou: ")
            if query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            print("\nChatbot: ", end="")
            answer = self.ask(query)
            print(answer)
