from .base_agent import BaseAgent
from typing import List, Dict, Any
import json
from format import output_format_screening

class ScreeningAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        
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
        
        # Get structured response from LLM
        response = self.call_llm(prompt)
        
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
