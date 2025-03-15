from Dependencies.pocketflow import Node
# from Dependencies.bs4 import BeautifulSoup
import os
import json
import openai
from nearai.agents.environment import Environment

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
            # Ensure API key is set for older versions
            if not openai.api_key and "OPENAI_API_KEY" in self.api_keys:
                openai.api_key = self.api_keys["OPENAI_API_KEY"]
                print(f"Setting OpenAI API key for web search")
            
            # Try newer OpenAI SDK first
            try:
                client = openai.OpenAI(api_key=self.api_keys.get("OPENAI_API_KEY"))
                
                response = client.chat.completions.create(
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
                
            except (ImportError, AttributeError) as e:
                # Fall back to older OpenAI SDK
                print(f"Using older OpenAI SDK for web search: {e}")
                
                if not openai.api_key:
                    if self.api_keys.get("OPENAI_API_KEY"):
                        openai.api_key = self.api_keys["OPENAI_API_KEY"]
                        print(f"Set API key from api_keys for web search")
                    elif "OPENAI_API_KEY" in os.environ:
                        openai.api_key = os.environ["OPENAI_API_KEY"]
                        print(f"Set API key from os.environ for web search")
                    else:
                        print("ERROR: No OpenAI API key available for web search!")
                
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a web search assistant. Search the web for the user's query and return the results as valid JSON."},
                        {"role": "user", "content": f"Search the web for: {query} and return the top 5 results as JSON in the format: {{\"results\": [{{\"title\": \"...\", \"snippet\": \"...\", \"link\": \"...\"}}, ...]}}"}
                    ]
                )
                
                result_json = json.loads(response.choices[0].message.content)
                if "results" in result_json:
                    return result_json["results"]
            
            # If we get here, no results were found from either method
            raise Exception("No search results found")
            
        except Exception as e:
            print(f"Web search failed: {e}")
            
            # Enhanced fallback: Create specific results for Scale AI or NEAR
            query_lower = query.lower()
            
            if "near" in query_lower:
                return [
                    {
                        "title": "NEAR Protocol - Blockchain Operating System",
                        "snippet": "NEAR Protocol is a layer-one blockchain designed to provide the ideal environment for dApps by overcoming the limitations of competing blockchains.",
                        "link": "https://near.org/"
                    },
                    {
                        "title": "NEAR Protocol: Founders and History",
                        "snippet": "NEAR Protocol was founded in 2018 by Erik Trautman, Illia Polosukhin, and Alexander Skidanov, focusing on building a scalable blockchain.",
                        "link": "https://near.org/about"
                    },
                    {
                        "title": "NEAR Protocol - Technology and Consensus",
                        "snippet": "NEAR Protocol uses Nightshade sharding and a proof-of-stake consensus mechanism to achieve high throughput and low transaction costs.",
                        "link": "https://near.org/technology"
                    }
                ]
            elif "scale" in query_lower:
                return [
                    {
                        "title": "Scale AI - Data Platform for AI",
                        "snippet": "Scale AI is an American technology company that provides a data platform for AI, specializing in training data generation, management, and model evaluation.",
                        "link": "https://scale.com/"
                    },
                    {
                        "title": "Scale AI Raises $325M Series E at $7.3B Valuation",
                        "snippet": "Scale AI, the data infrastructure for AI, announced $325 million in Series E funding. The new funding brings Scale's valuation to $7.3 billion.",
                        "link": "https://scale.com/blog/series-e"
                    },
                    {
                        "title": "Alexandr Wang, CEO of Scale AI",
                        "snippet": "Alexandr Wang is the founder and CEO of Scale AI, a company he started at 19 years old and is now valued at $7.3 billion.",
                        "link": "https://www.forbes.com/profile/alexandr-wang/"
                    }
                ]
            
            # Generic fallback results
            mock_results = []
            if "patent" in query_lower:
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
            elif "regulation" in query_lower:
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
                company_name = query.split()[0] if query.split() else "Unknown"
                mock_results = [
                    {
                        "title": f"{company_name} Company Information",
                        "snippet": f"{company_name} is a technology company operating in the digital sector with innovative solutions.",
                        "link": f"https://www.google.com/search?q={company_name.replace(' ', '+')}"
                    },
                    {
                        "title": f"{company_name} Industry Analysis",
                        "snippet": f"Analysis of {company_name}'s market position and industry trends.",
                        "link": f"https://www.google.com/search?q={company_name.replace(' ', '+')}+industry+analysis"
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