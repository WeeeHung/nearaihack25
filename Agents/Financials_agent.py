"""
Financial Agent for Multi-Agent Due Diligence System

This file provides a high-level interface to the Financial Agent implementation.
It focuses on financial analysis and can receive data from other agents.
"""

from typing import Dict, Any, Optional
from pocketflow import Flow, Node
from .financial_agent.agent import FinancialAgent
from .screening_agent.agent import ScreeningAgent
from .base_agent import AgentContext

# Try to import related agents
try:
    from .Market_analysis_agent import analyze_market
    HAS_MARKET_ANALYSIS = True
except ImportError:
    HAS_MARKET_ANALYSIS = False

try:
    from .Due_dillegence_report_agent import get_report_agent
    HAS_REPORT_AGENT = True
except ImportError:
    HAS_REPORT_AGENT = False

class FinancialAnalysisNode(Node):
    """Node for executing financial analysis"""
    
    def __init__(self, screening_agent: Optional[ScreeningAgent] = None, market_data: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.screening_agent = screening_agent
        self.market_data = market_data
        
    def prep(self, shared):
        """Prepare for financial analysis"""
        company_name = shared.get("company_name", "Unknown")
        
        # Get screening agent from shared if available
        if self.screening_agent is None and "screening_agent" in shared:
            self.screening_agent = shared["screening_agent"]
            
        # Get market data from shared if available
        if self.market_data is None and "market_data" in shared:
            self.market_data = shared["market_data"]
            
        return company_name
    
    def exec(self, company_name):
        """Execute financial analysis"""
        # Create financial agent
        financial_agent = FinancialAgent(
            screening_agent=self.screening_agent,
            market_data=self.market_data
        )
        
        # Execute financial analysis
        return financial_agent.execute(company_name)
    
    def post(self, shared, prep_res, exec_res):
        """Process analysis results"""
        shared["financial_analysis"] = exec_res
        
        # Send data to Due Diligence Report Agent if available
        if HAS_REPORT_AGENT and exec_res:
            try:
                report_agent = get_report_agent()
                if report_agent:
                    report_agent.add_financial_data(exec_res)
                    print("Financial analysis data sent to Due Diligence Report Agent")
            except Exception as e:
                print(f"Warning: Failed to send data to Due Diligence Report Agent: {str(e)}")
                
        return "default"

class ReportGenerationNode(Node):
    """Node for generating financial reports"""
    
    def __init__(self, output_path: Optional[str] = None):
        super().__init__()
        self.output_path = output_path
    
    def prep(self, shared):
        """Prepare for report generation"""
        analysis_result = shared.get("financial_analysis", {})
        company_name = shared.get("company_name", "Unknown")
        return analysis_result, company_name
    
    def exec(self, inputs):
        """Generate financial report"""
        analysis_result, company_name = inputs
        financial_agent = FinancialAgent()
        
        if not analysis_result:
            return "No financial analysis data available."
            
        return financial_agent.generate_markdown_report(analysis_result)
    
    def post(self, shared, prep_res, exec_res):
        """Save generated report"""
        analysis_result, company_name = prep_res
        shared["report_content"] = exec_res
        
        if self.output_path:
            # Save to specified path
            with open(self.output_path, "w") as f:
                f.write(exec_res)
            shared["report_path"] = self.output_path
        else:
            # Generate default filename if no path specified
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"financial_report_{company_name}_{timestamp}.md"
            
            with open(filename, "w") as f:
                f.write(exec_res)
            shared["report_path"] = filename
        
        return "default"

def analyze_financials(company_name: str, screening_agent=None, market_data=None, output_path=None, send_to_report=True) -> Dict[str, Any]:
    """
    Analyze company financials and generate a report.
    
    Args:
        company_name (str): Name of the company to analyze
        screening_agent (ScreeningAgent, optional): Screening agent with company data
        market_data (dict, optional): Market analysis data 
        output_path (str, optional): Path to save the report
        send_to_report (bool): Whether to send data to the Due Diligence Report Agent
        
    Returns:
        Dict containing the financial analysis results
    """
    # Create shared data store
    shared = {
        "company_name": company_name,
        "send_to_report": send_to_report
    }
    
    # Add screening agent if provided
    if screening_agent:
        shared["screening_agent"] = screening_agent
    
    # Add market data if provided
    if market_data:
        shared["market_data"] = market_data
    
    # Create analysis and report nodes
    financial = FinancialAnalysisNode()
    report = ReportGenerationNode(output_path=output_path)
    
    # Connect nodes
    financial >> report
    
    # Create and run flow
    flow = Flow(start=financial)
    flow.run(shared)
    
    # Return analysis results
    return shared.get("financial_analysis", {})

def get_financial_data(company_name: str = None) -> Dict[str, Any]:
    """
    Get the last financial analysis results for a company.
    
    This function can be called by other agents (e.g., Due Diligence Report Agent)
    to get financial analysis data.
    
    Args:
        company_name: Optional company name filter
        
    Returns:
        Dict containing the financial analysis results
    """
    # In a production environment, this would retrieve data from a database
    # For simplicity, we'll check if we have an already-created FinancialAgent
    # with analysis results, or create a new one if needed
    financial_agent = FinancialAgent()
    
    # Check if we have saved analysis for this company
    if hasattr(financial_agent, 'last_analysis') and financial_agent.last_analysis:
        if company_name is None or financial_agent.last_analysis.get('company_name') == company_name:
            return financial_agent.last_analysis
    
    # If no saved analysis or doesn't match company, create a new analysis
    if company_name:
        return analyze_financials(company_name, send_to_report=False)
    
    # Return empty dict if no company name and no saved analysis
    return {}

# Main function for CLI usage
if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python Financials_agent.py <company_name> [output_path]")
        sys.exit(1)
        
    company_name = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Try to get market data if available
    market_data = None
    if HAS_MARKET_ANALYSIS:
        try:
            print(f"Retrieving market analysis data for {company_name}...")
            market_data = analyze_market(company_name)
        except Exception as e:
            print(f"Warning: Could not retrieve market analysis: {str(e)}")
    
    # Run financial analysis
    print(f"Analyzing financials for {company_name}...")
    analysis = analyze_financials(company_name, market_data=market_data, output_path=output_path)
    
    # Report output location
    if output_path:
        print(f"Financial report saved to: {output_path}")
    else:
        print(json.dumps(analysis, indent=2))
