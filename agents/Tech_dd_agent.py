import openai
import json
from base_agent import BaseAgent
from dotenv import load_dotenv
import os
from openai import OpenAI

class TechDdAgent(BaseAgent):
    load_dotenv()
    def __init__(self, name="TechDdAgent"):
        """Initialize the tech DD agent."""
        # Initialize any attributes before calling super().__init__
        self.env = type('obj', (object,), {'env_vars': os.environ})
        
        # Now call the parent constructor
        super().__init__(name)
        
        # Initialize OpenAI client
        self._load_api_keys()
        self.client = openai.Client(api_key=self.api_keys.get("OPENAI_API_KEY"))

    def prep(self, shared):
        """Extract relevant company data from shared store."""
        return {
            "company_info": shared.get("company_info", ""),
            "team_data": shared.get("team_profiles", {})
        }

    def exec(self, data):
        """Perform technical due diligence analysis."""

        print("data", data)
        
        prompt = f"""
        You are a technical due diligence agent. You are given a company's information and team profiles.
        You need to research the company's technical architecture, technical differentiation, team technical assessment, and engineering factors.
        You need to generate a technical due diligence report.

        Specifically, you need to analyze the following:
        - Company's technical architecture
        - Company's technical differentiation
        - Company's technical feasibility
        - Team technical assessment, and whether the team's background is suitable to execute on the company's technical architecture and differentiation
        - Other potential engineering risks and mitigations

        If you need more information, search the web for those information. Do not ask for more information from the user.
        Give a summary about what the tech is about, what the product is, what the market is,
        how the tech works, how the product is used, and what the market demand is.

        You need to generate a technical due diligence report.

        Here is the company information: {data}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-search-preview",
            web_search_options={},
            messages=[
                {"role": "system", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    def post(self, shared, prep_res, exec_res):
        """Save results to shared store."""
        shared["tech_dd_results"] = exec_res
        
        # Save to file
        with open("tech_dd_report.json", "w") as f:
            json.dump(exec_res, f, indent=2)
            
        print(f"Technical DD report saved to tech_dd_report.json")
        return "default"