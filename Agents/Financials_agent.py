import openai
import requests

from base_agent import BaseAgent

class FinancialsAgent(BaseAgent):
    def __init__(self, name="FinancialsAgent"):
        """
        Initialize the financials agent with specific functionality.
        
        Args:
            name (str): Name of the agent
        """
        super().__init__(name)
        
        # Load API keys from environment variables
        self._load_api_keys()
        
        # Initialize OpenAI client
        self.client = openai.Client(api_key=self.api_keys.get("OPENAI_API_KEY"))
    
    def prep(self, shared):
        """
        Prepare data for execution. Extract the company information from shared store.
        
        Args:
            shared (dict): Shared data store
            
        Returns:
            str: Company information to search for financials
        """
        return shared.get("company_info", "")
    
    def exec(self, company_info):
        """
        Execute a search for financials using the OpenAI API.
        
        Args:
            company_info (str): Information about the company to find financials for
        
        Returns:
            dict: Structured data about financials
        """
        search_prompt = f"""
            {company_info}

            The above contains information of a company - part of which is the financial info extracted from their financial data room.
            Using this, please provide a detailed analysis of the company's financials, including:
            - Revenue model
            - Current customers
            - Growth rate (if any)
            - Key partners (if any)
            - Funding stage
            - Last funded amount
            - Total funds raised

            Do also include their cap table, such as:
            - Founders
            - Investors
            - Advisors
            - Employees

            Put the information into a structured JSON format following the following template:
            return_value = {{
                "revenue_model": {
                    "business_model": "",
                    "pricing": "",
                    "revenue_streams": []
                },
                "historical_financials": {  
                    "revenue": {
                        "year_1": "",
                        "year_2": "",
                        "year_3": ""
                    },
                    "profits": {
                        "year_1": "",
                        "year_2": "",
                        "year_3": ""
                    },
                    "expenses": {
                        "cost_of_goods_sold": "",
                        "operating_expenses": ""
                    }
                },
                "cap table": {
                    "founders": {
                        "founder_name": "",
                        "background": "",
                        "number of shares": "",
                    },
                    "key_team_members": [
                        {
                            "name": "",
                            "role": "",
                            "number of shares": "",
                        }
                    ],
                },
            }}

        """
        gptmodel = self.get_4omini_model(temperature=0.7)
        response = gptmodel(search_prompt)
        
        return response