from Dependencies.pocketflow import Node
from Dependencies.bs4 import BeautifulSoup
import os
import json
import openai
from nearai.agents.environment import Environment
from pocketflow import Node
from bs4 import BeautifulSoup

class BaseAgent(Node):
    def __init__(self, env: Environment, name="BaseAgent"):
        """
        Initialize the base agent with common functionality.
        
        Args:
            name (str): Name of the agent
            max_retries (int): Maximum number of retries for exec()
            wait (int): Wait time between retries in seconds
        """
        self.name = name
        self.env = env
        self.api_keys = {}
        self.max_retries = 1
        self.wait = 0
        self.cur_retry = 0
        self.successors = {}
        
        # Load API keys from environment variables
        self._load_api_keys()
    
    def _load_api_keys(self):
        """Load API keys from environment variables."""
        # Common API keys that might be needed
        possible_keys = [
            "OPENAI_API_KEY",
        ]

        for key in possible_keys:
            # if key in os.environ:
            if key in self.env.env_vars:
                # self.api_keys[key] = os.environ[key]
                self.api_keys[key] = self.env.env_vars[key]
                print(f"Loaded API key: {key} (length: {len(self.api_keys[key])})")
            else:
                print(f"WARNING: {key} not found in environment variables!")
    
    def get_4o_mini_model(self, temperature=0.7):
        """
        Get the GPT-4o mini model instance.
        
        Args:
            temperature (float): The temperature to use for generation
            
        Returns:
            function: A function that can be used to generate text with the model
        """
        # Ensure client is initialized
        if not hasattr(self, 'client'):
            try:
                self.client = openai.Client(api_key=self.api_keys.get("OPENAI_API_KEY"))
            except Exception as e:
                print(f"Warning: Failed to initialize OpenAI client: {e}")
                self.client = None
        
        def generate_text(prompt):
            try:
                # Try using client if available
                if self.client:
                    response = self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        max_tokens=2000,
                        temperature=temperature,
                    )
                    return response.choices[0].message.content
            except Exception as e:
                print(f"Error generating text: {e}")
                return None
        
        return generate_text
    # Node methods that can be overridden by child agents
    def prep(self, shared):
        """
        Prepare data for execution.
        Override this in child classes to customize behavior.
        """
        return shared.get("input", "")
    
    def exec(self, prep_res):
        """
        Execute agent logic.
        Override this in child classes to implement agent-specific behavior.
        """
        return f"BaseAgent {self.name} received: {prep_res}"
    
    def post(self, shared, prep_res, exec_res):
        """
        Process execution results.
        Override this in child classes to customize behavior.
        """
        shared["output"] = exec_res
        return "default"