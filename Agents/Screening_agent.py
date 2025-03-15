from .base_agent import BaseAgent
from typing import List, Dict, Any
import json
from .format import output_format_screening
from nearai.agents.environment import Environment
class ScreeningAgent(BaseAgent):
    def __init__(self, env: Environment):
        super().__init__(env, name="ScreeningAgent")
        self.env.add_system_log("ScreeningAgent initialized")

    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from the given text."""
        # Implement URL extraction logic here
        return []
        
    def run(self, texts: List[str]) -> Dict[str, Any]:
        """Process input texts and extract structured information."""
        
        # self.env.add_system_log("Running ScreeningAgent")
        # Combine texts into single context
        context = "\n\n".join(texts)
        
        # Create LLM prompt to extract information
        prompt = f"""
        Extract key information from the following text and format it according to the structure below.
        Only include factual information present in the text - leave fields empty if information is not provided.
        
        Text:
        {context}
        
        Output the information in JSON format:
        ```json
        {output_format_screening}
        ```
        """

        # Retreive any URLS from the text and do scraping 
        # urls = self.extract_urls(context)
        # for url in urls:
        #     self.scrape(url)

        response = self.get_4o_mini_model(
            temperature=0.0,
        )(
            prompt,
        )
        
        try:
            # Extract JSON between code fences
            json_str = response.split("```json")[1].split("```")[0].strip()
            
            # Parse JSON to dict
            structured_data = json.loads(json_str)
            
            # Validate required top-level keys exist
            required_keys = ["market_analysis", "team_eval", "financial", 
                           "tech_deep_dive", "legal", "competition"]
            
            for key in required_keys:
                if key not in structured_data:
                    structured_data[key] = {}
                    
            return structured_data
            
        except Exception as e:
            self.env.add_system_log(f"Error parsing LLM response: {e}")
            return {}
