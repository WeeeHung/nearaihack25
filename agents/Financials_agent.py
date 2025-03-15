from .base_agent import BaseAgent
from nearai.agents.environment import Environment

class FinancialsAgent(BaseAgent):
    def __init__(self, env:Environment, name="FinancialsAgent"):
        """
        Initialize the financials agent with specific functionality.
        
        Args:
            env (Environment): Environment of the agent
            name (str): Name of the agent
        """
        super().__init__(env, name=name)
        self.env.add_system_log("FinancialsAgent initialized")
    
    def prep(self, shared):
        """
        Prepare data for execution. Extra   ct the company information from shared store.
        
        Args:
            shared (dict): Shared data store
            
        Returns:
            str: Company information to search for financials
        """
        return shared.get("company_info", "")
    
    def run(self, company_info):
        """
        Execute a search for financials using the OpenAI API.
        
        Args:
            company_info (str): Information about the company to find financials for
        
        Returns:
            dict: Structured data about financials
        """
        self.env.add_system_log("Running FinancialsAgent")
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
            return_value = {{{{
                "revenue_model": {{{{
                    "business_model": "",
                    "pricing": "",
                    "revenue_streams": []
                }}}},
                "historical_financials": {{{{  
                    "revenue": {{{{
                        "year_1": "",
                        "year_2": "",
                        "year_3": ""
                    }}}},
                    "profits": {{{{
                        "year_1": "",
                        "year_2": "",
                        "year_3": ""
                    }}}},
                    "expenses": {{{{
                        "cost_of_goods_sold": "",
                        "operating_expenses": ""
                    }}}}
                }}}},
                "cap_table": {{{{
                    "founders": [
                        {{{{
                            "name": "",
                            "background": "",
                            "shares": ""
                        }}}}
                    ],
                    "investors": [
                        {{{{
                            "name": "",
                            "investment_amount": "",
                            "shares": ""
                        }}}}
                    ],
                    "advisors": [
                        {{{{
                            "name": "",
                            "role": "",
                            "shares": ""
                        }}}}
                    ],
                    "employees": [
                        {{{{
                            "name": "",
                            "role": "",
                            "shares": ""
                        }}}}
                    ]
                }}}}
            }}}}
        """
        gptmodel = self.get_4o_mini_model(temperature=0.7)
        response = gptmodel(search_prompt)
        
        return response