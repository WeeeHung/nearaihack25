import openai
import json
from .base_agent import BaseAgent
from nearai.agents.environment import Environment
class CompetitorsAgent(BaseAgent):
    def __init__(self, env:Environment, name="CompetitorsAgent"):
        """
        Initialize the competitors agent with specific functionality.
        
        Args:
            name (str): Name of the agent
        """
        super().__init__(env, name=name)
        self.client = openai.OpenAI(api_key=self.api_keys["OPENAI_API_KEY"])
        self.env.add_system_log("CompetitorsAgent initialized")

    def prep(self, shared):
        """
        Prepare data for execution. Extract the company information from shared store.
        
        Args:
            shared (dict): Shared data store
            
        Returns:
            str: Company information to search for competitors
        """
        return shared.get("company_info", "")
    
    def run(self, company_info):
        """
        Execute a search for competitors using the OpenAI API.
        
        Args:
            company_info (str): Information about the company to find competitors for
        
        Returns:
            dict: Structured data about competitors
        """
        self.env.add_system_log("Running CompetitorsAgent")
        search_prompt = f"""
            I need to find comprehensive information about competitors for the following company:
            {company_info}

            Please identify AT LEAST 10 competitors, clearly categorizing them as:
            1. Direct competitors (same technology, same business vertical)
            2. Indirect competitors (similar technology but different vertical, or other combinations)

            For each competitor, include:
            - Company name
            - Year founded
            - Headquarters location
            - Company website
            - Funding stage
            - Last funded amount
            - Total funds raised
            - Last valuation (if available)
            - Key investors
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-search-preview",
            web_search_options={},
            messages=[{"role": "user", "content": search_prompt}],
        )
        
        competitors_data = response.choices[0].message.content
        return self._structure_competitors_data(competitors_data, company_info)
    
    def _structure_competitors_data(self, competitors_data, company_info):
        """
        Structure competitor data and get detailed comparisons
        
        Args:
            competitors_data (str): Initial search results with competitor information
            company_info (str): Original company information
            
        Returns:
            dict: Fully structured competitor data
        """
        extraction_prompt = f"""
            Given the following search results about competitors:
            {competitors_data}
            Extract the names of ALL competitors mentioned (both direct and indirect).
            Format the response as a JSON object with a single key "competitors" containing an array of strings with ONLY the company names.
        """
        
        gptmodel = self.get_4o_mini_model(temperature=0.7)
        response = gptmodel(extraction_prompt)

        response = json.loads(response.split("```json")[1].split("```")[0])

        print(response)

        competitor_names = response.get("competitors", [])
        
        result = {
            "direct_competitors": [],
            "indirect_competitors": []
        }
        
        for name in competitor_names:
            print("getting competitor details for:", name)
            competitor_info = self._get_competitor_details(name, company_info)
            print("done getting competitor details for:", name)
            if competitor_info:
                category = "direct_competitors" if competitor_info.get("is_direct", False) else "indirect_competitors"
                result[category].append(competitor_info)
        
        return result
    
    def _get_competitor_details(self, competitor_name, original_company_info):
        # STEP 1: Search for information using web search
        search_prompt = f"""
            Search for detailed information about {competitor_name} and compare it with this company:
            {original_company_info}
            
            Include the following details about {competitor_name}:
            - Year founded
            - Headquarters location
            - Company website
            - Funding stage
            - Last funded amount
            - Total funds raised
            - Last valuation (if available)
            - Key investors
            - Main products or services
            - Target market
            - Comparison with the original company
            
            Please provide comprehensive information about all these aspects.
        """
        
        # First call: With web search enabled
        search_response = self.client.chat.completions.create(
            model="gpt-4o-search-preview",
            web_search_options={},
            messages=[{"role": "user", "content": search_prompt}],
        )
        
        # Get the detailed information from the search
        detailed_info = search_response.choices[0].message.content
        
        # STEP 2: Parse the information into structured JSON
        parse_prompt = f"""
            Based on this detailed information about {competitor_name}:
            
            {detailed_info}
            
            Create a structured comparison with the original company:
            {original_company_info}
            
            Return ONLY a JSON object with EXACTLY this structure:
            {{
                "companyProfile": {{
                    "name": "{competitor_name}",
                    "yearFounded": "YEAR",
                    "headquarters": "LOCATION",
                    "website": "URL",
                    "fundingStage": "STAGE",
                    "lastFundedAmount": "AMOUNT",
                    "totalFundsRaised": "AMOUNT",
                    "lastValuation": "AMOUNT",
                    "investors": ["INVESTOR1", "INVESTOR2"]
                }},
                "description": "DESCRIPTION",
                "comparisons": {{
                    "similarities": ["SIMILARITY1", "SIMILARITY2", "SIMILARITY3"],
                    "differences": ["DIFFERENCE1", "DIFFERENCE2", "DIFFERENCE3"]
                }},
                "is_direct": true/false
            }}
            
            Ensure you include at least 3 specific similarities and 3 specific differences.
            The "is_direct" field should be true if {competitor_name} competes directly with the original company.
        """
        gptmodel = self.get_4o_mini_model(temperature=0.7)
        # Second call: With JSON response format (no web search)
        parse_response = gptmodel(parse_prompt)
        
        # Parse the structured JSON response
        competitor_details = json.loads(parse_response.split("```json")[1].split("```")[0])
        return competitor_details
    
    def post(self, shared, prep_res, exec_res):
        """
        Process and store the competitor information.
        
        Args:
            shared (dict): Shared data store
            prep_res (str): Input company information
            exec_res (dict): Structured competitor data
            
        Returns:
            str: Action string for flow control
        """
        shared["competitors"] = exec_res
        total_direct = len(exec_res.get("direct_competitors", []))
        total_indirect = len(exec_res.get("indirect_competitors", []))
        
        print(f"Found {total_direct} direct competitors and {total_indirect} indirect competitors.")
        return "default"