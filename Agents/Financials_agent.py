"""
Financial Agent for Multi-Agent Due Diligence System

This file provides a high-level interface to the Financial Agent implementation
using PocketFlow's node-based architecture.
"""

from typing import Dict, Any, Optional
from pocketflow import Flow, Node
from .financial_agent.agent import FinancialAgent
from .screening_agent.agent import ScreeningAgent
from .base_agent import AgentContext

# Try to import market analysis
try:
    from .Market_analysis_agent import analyze_market
    HAS_MARKET_ANALYSIS = True
except ImportError:
    HAS_MARKET_ANALYSIS = False

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

class ScreeningNode(Node):
    """Node for running screening process"""
    
    def __init__(self, context: Optional[AgentContext] = None):
        super().__init__()
        self.context = context
        self.screening_agent = None
        
    def prep(self, shared):
        """Prepare for screening"""
        company_name = shared.get("company_name", "Unknown")
        context = self.context or AgentContext(company_name=company_name)
        self.screening_agent = ScreeningAgent(context=context)
        return company_name
    
    def exec(self, company_name):
        """Execute screening process"""
        return self.screening_agent.execute(company_name)
    
    def post(self, shared, prep_res, exec_res):
        """Process screening results"""
        shared["screening_results"] = exec_res
        shared["screening_agent"] = self.screening_agent
        return "default"

class MarketAnalysisNode(Node):
    """Node for running market analysis"""
    
    def prep(self, shared):
        """Prepare for market analysis"""
        if not HAS_MARKET_ANALYSIS:
            return None
        return shared.get("company_name", "Unknown")
    
    def exec(self, company_name):
        """Execute market analysis"""
        if company_name is None:
            return None
        try:
            return analyze_market(company_name)
        except Exception as e:
            print(f"Warning: Failed to get market analysis: {str(e)}")
            return None
    
    def post(self, shared, prep_res, exec_res):
        """Process market analysis results"""
        if exec_res:
            shared["market_data"] = exec_res
        return "default"

# Main function for CLI usage
if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python Financials_agent.py <company_name> [output_path]")
        sys.exit(1)
        
    company_name = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Create shared data store
    shared = {"company_name": company_name}
    
    print(f"Starting financial analysis flow for {company_name}...")
    print("1. Running initial screening process...")
    
    # Create nodes with progress updates
    screening = ScreeningNode()
    market = MarketAnalysisNode()
    financial = FinancialAnalysisNode()
    report = ReportGenerationNode(output_path=output_path)
    
    # Create callbacks for progress updates
    def after_screening(node, shared):
        print("2. Gathering market analysis data...")
        
    def after_market(node, shared):
        print("3. Performing financial analysis...")
        
    def after_financial(node, shared):
        print("4. Generating financial report...")
    
    # Connect nodes with callbacks
    screening >> after_screening >> market >> after_market >> financial >> after_financial >> report
    
    # Create and run flow
    flow = Flow(start=screening)
    flow.run(shared)
    
    print("5. Analysis complete!")
    
    # Output results
    if "report_path" in shared:
        print(f"Financial report saved to: {shared['report_path']}")
    elif "financial_analysis" in shared:
        print(json.dumps(shared["financial_analysis"], indent=2))
    else:
        print("No analysis results generated.")
