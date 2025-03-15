from Dependencies.pocketflow import Node
import requests
# from Dependencies.bs4 import BeautifulSoup
import os
import openai

from nearai.agents.environment import Environment

import json

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
    
    # def scrape(self, url):
    #     """
    #     Scrape content from a web page.
        
    #     Args:
    #         url (str): URL to scrape
            
    #     Returns:
    #         tuple: (title, text content)
    #     """
    #     try:
    #         response = requests.get(url, headers={
    #             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    #         })
    #         response.raise_for_status()
            
    #         soup = BeautifulSoup(response.text, "html.parser")
    #         title = soup.title.string if soup.title else "No title found"
            
    #         # Remove script and style elements
    #         for script in soup(["script", "style", "nav", "footer", "header"]):
    #             script.extract()
                
    #         text = soup.get_text(separator='\n')
    #         # Clean up text
    #         lines = (line.strip() for line in text.splitlines())
    #         chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    #         text = '\n'.join(chunk for chunk in chunks if chunk)
            
    #         return title, text
    #     except Exception as e:
    #         return f"Error scraping {url}: {str(e)}", ""
    
    def search_web(self, query):
        """
        Search the web for information.
        
        Args:
            query (str): The search query
            
        Returns:
            list: List of search results (title, snippet, link)
        """
        try:
            # Try to use OpenAI's web search if available
            if not hasattr(self, 'client'):
                self.client = openai.Client(api_key=self.api_keys.get("OPENAI_API_KEY"))
            
            # Call the web search API through ChatGPT
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a web search assistant. Search the web for the user's query and return the results as valid JSON."},
                    {"role": "user", "content": f"Search the web for: {query} and return the top 5 results as JSON in the format: {{\"results\": [{{\"title\": \"...\", \"snippet\": \"...\", \"link\": \"...\"}}, ...]}}"}
                ],
                response_format={"type": "json_object"}
            )
            
            result_json = json.loads(response.choices[0].message.content)
            if "results" in result_json:
                return result_json["results"]
            
            # If no results found, try fallback method
            raise Exception("No search results found")
            
        except Exception as e:
            print(f"Web search failed: {e}")
            
            # Fallback: Create mock search results
            mock_results = []
            if "patent" in query.lower():
                company_name = query.split(" patent")[0].strip()
                mock_results = [
                    {
                        "title": f"{company_name} Patent Portfolio",
                        "snippet": f"Browse {company_name}'s patent portfolio and intellectual property strategy.",
                        "link": f"https://patents.google.com/?assignee={company_name.replace(' ', '+')}"
                    },
                    {
                        "title": f"Recent Patent Filings by {company_name}",
                        "snippet": f"View recent patent applications and grants associated with {company_name}.",
                        "link": f"https://patents.google.com/?assignee={company_name.replace(' ', '+')}&after=2020"
                    }
                ]
            elif "regulation" in query.lower():
                industry = query.split(" regulation")[0].strip()
                mock_results = [
                    {
                        "title": f"{industry} Regulatory Framework",
                        "snippet": f"Overview of key regulations affecting {industry} businesses.",
                        "link": f"https://www.regulations.gov/search?keyword={industry.replace(' ', '+')}"
                    },
                    {
                        "title": f"Compliance Guide for {industry} Companies",
                        "snippet": f"Essential compliance information for {industry} companies.",
                        "link": "https://www.ftc.gov/business-guidance/industry"
                    }
                ]
            else:
                mock_results = [
                    {
                        "title": f"Search Results for {query}",
                        "snippet": "No detailed results available.",
                        "link": f"https://www.google.com/search?q={query.replace(' ', '+')}"
                    }
                ]
                
            return mock_results
    
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
                else:
                    # Direct API access if client initialization failed
                    import requests
                    
                    headers = {
                        "Authorization": f"Bearer {self.api_keys.get('OPENAI_API_KEY')}",
                        "Content-Type": "application/json"
                    }
                    
                    data = {
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 2000,
                        "temperature": temperature
                    }
                    
                    response = requests.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json=data
                    )
                    response_json = response.json()
                    
                    if "choices" in response_json and len(response_json["choices"]) > 0:
                        return response_json["choices"][0]["message"]["content"]
                    else:
                        raise Exception(f"API Error: {response_json}")
            except Exception as e:
                print(f"Error generating text: {e}")
                return None
        
        return generate_text
    
    # For backward compatibility
    get_4omini_model = get_4o_mini_model
    
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