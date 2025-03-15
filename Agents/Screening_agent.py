from base_agent import BaseAgent
from typing import List, Dict, Any
import json
from format import output_format_screening

class ScreeningAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from the given text."""
        # Implement URL extraction logic here
        return []
        
    def run(self, texts: List[str]) -> Dict[str, Any]:
        """Process input texts and extract structured information."""
        
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
        urls = self.extract_urls(context)
        for url in urls:
            self.scrape(url)

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
            print(f"Error parsing LLM response: {e}")
            return {}


if __name__ == "__main__":
    agent = ScreeningAgent()
    # Simulate pitch deck content for testing
    sample_pitch = """
    # INNOVATECH AI SOLUTIONS
    ## Revolutionizing Enterprise Decision Making
    
    ### Market Opportunity
    $50B global market for AI decision support systems with 25% YoY growth
    Enterprise clients spending avg. $2.5M annually on outdated solutions
    
    ### Our Solution
    Proprietary ML algorithm with 85% improved accuracy over competitors
    Reduces decision-making time by 60% and operational costs by 30%
    
    ### Team
    Dr. Sarah Chen, CEO - Former ML Director at Google, Stanford PhD
    Michael Rodriguez, CTO - 15 years at Microsoft, 12 patents
    
    ### Financials
    $2.5M ARR with 140% growth rate
    $8M seed funding secured, seeking Series A of $15M
    Projected $50M revenue by 2025
    
    ### Competition
    Current solutions lack real-time processing and have 40% higher error rates
    Our proprietary technology has 3 pending patents
    """
    
    # Test the agent with the sample pitch content
    result = agent.run([sample_pitch])
    print(json.dumps(result, indent=2))