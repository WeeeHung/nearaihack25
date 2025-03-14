from pocketflow import Node
import requests
from bs4 import BeautifulSoup
import os

class BaseAgent(Node):
    def __init__(self, name="BaseAgent"):
        """
        Initialize the base agent with common functionality.
        
        Args:
            name (str): Name of the agent
            max_retries (int): Maximum number of retries for exec()
            wait (int): Wait time between retries in seconds
        """
        self.name = name
        self.api_keys = {}
        
        # Load API keys from environment variables
        self._load_api_keys()
    
    def _load_api_keys(self):
        """Load API keys from environment variables."""
        # Common API keys that might be needed
        possible_keys = [
            "OPENAI_API_KEY",
        ]
        
        for key in possible_keys:
            if key in os.environ:
                self.api_keys[key] = os.environ[key]
    
    def scrape(self, url):
        """
        Scrape content from a web page.
        
        Args:
            url (str): URL to scrape
            
        Returns:
            tuple: (title, text content)
        """
        try:
            response = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "No title found"
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()
                
            text = soup.get_text(separator='\n')
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return title, text
        except Exception as e:
            return f"Error scraping {url}: {str(e)}", ""
    
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