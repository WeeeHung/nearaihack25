from .base_agent import BaseAgent
import json
from typing import List, Dict, Any
from nearai.agents.environment import Environment
class DueDiligenceReportAgent(BaseAgent):
    def __init__(self, env: Environment, name="DueDiligenceReportAgent"):
        """
        Initialize the due diligence report agent.
        
        This agent takes results from other agents in JSON format and compiles
        them into a comprehensive, human-readable due diligence report.
        """
        super().__init__(env, name=name)
        self.env.add_system_log("DueDiligenceReportAgent initialized")

    def run(self, json_data_list: List[Dict[str, Any]]) -> str:
        """
        Compile the final due diligence report from the provided JSON data.
        
        Args:
            json_data_list: List of JSON data from various agents
            
        Returns:
            str: A well-formatted, comprehensive due diligence report
        """
        self.env.add_system_log("Running DueDiligenceReportAgent")
        # Combine all JSON data into a single comprehensive structure
        combined_data = self._combine_json_data(json_data_list)
        
        # Generate the report using OpenAI
        llm = self.get_4o_mini_model(temperature=0.4)
        
        prompt = f"""
        You are a professional due diligence report writer for a venture capital firm.
        
        Create a comprehensive, well-structured due diligence report based on the following data.
        The report should be 100% FACTUAL and based ONLY on the information provided.
        DO NOT make up any information or add speculative content.
        
        Use clear, professional language with proper formatting:
        - Use headers and subheaders to organize content
        - Include bullet points for lists where appropriate
        - Bold key findings and important metrics
        - Maintain a neutral, objective tone throughout
        
        Data to be included in the report:
        {json.dumps(combined_data, indent=2)}
        
        The report should include the following sections:
        1. Executive Summary
        2. Market Analysis
           - Industry Overview
           - Target Audience
           - Market Opportunity
        3. Team Evaluation
           - Founders
           - Key Team Members
           - Organizational Structure
        4. Financial Analysis
           - Revenue Model
           - Historical Financials
           - Projections
           - Investment Structure
        5. Technology Assessment
           - Technology Stack
           - Product Roadmap
           - Technical Challenges
           - Intellectual Property
        6. Legal Review
           - Corporate Structure
           - Contracts & Agreements
           - Compliance & Regulations
        7. Competitive Landscape
           - Market Landscape
           - Competitive Analysis
           - Market Share
        8. Risk Assessment
           - Key Risks
           - Mitigation Strategies
        9. Final Recommendation

        Format the report in clean Markdown, with proper sections and subsections.
        It should be 100% factual and based ONLY on the information provided. 
        It should be like a professional report.
        """
        
        report = llm(prompt)
        return report
    
    def _combine_json_data(self, json_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine multiple JSON objects into a single comprehensive structure.
        
        Args:
            json_data_list: List of JSON data from various agents
            
        Returns:
            Dict: Combined data structure
        """
        combined_data = {}
        for data in json_data_list:
            if isinstance(data, dict):
                self._deep_merge(combined_data, data)
            else:
                # Handle non-dict data appropriately, maybe by adding to a special key
                if 'non_dict_data' not in combined_data:
                    combined_data['non_dict_data'] = []
                combined_data['non_dict_data'].append(data)
            
        return combined_data
    
    def _deep_merge(self, target: Dict, source: Dict) -> None:
        """
        Recursively merge source dictionary into target dictionary.
        
        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """

        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            elif key in target and isinstance(target[key], list) and isinstance(value, list):
                # Combine lists without duplicates
                target[key].extend([item for item in value if item not in target[key]])
            else:
                # Override or add the value
                target[key] = value
    
    def prep(self, shared):
        """
        Prepare data for execution.
        
        Args:
            shared: Shared data containing JSON inputs
            
        Returns:
            List[Dict]: List of JSON data to be processed
        """
        # Extract JSON data from shared store
        json_data_list = shared.get("agent_results", [])
        
        if not json_data_list:
            raise ValueError("No agent results found in shared data")
            
        return json_data_list
    
    def post(self, shared, prep_res, exec_res):
        """
        Process execution results and update shared data.
        
        Args:
            shared: Shared data
            prep_res: Input JSON data
            exec_res: Generated report
            
        Returns:
            str: Action identifier
        """
        # Store the generated report in shared data
        shared["due_diligence_report"] = exec_res
        # self.env.add_system_log("Due diligence report generated successfully")
        return "default"