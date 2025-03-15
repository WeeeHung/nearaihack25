"""
Financial Agent for Multi-Agent Due Diligence System

This file provides a high-level interface to the Financial Agent implementation.
See the financial_agent package for the detailed implementation.
"""

from typing import Dict, Any, Optional
from .financial_agent import FinancialAgent
from .screening_agent.agent import ScreeningAgent
from .base_agent import AgentContext

# Try to import market analysis
try:
    from .Market_analysis_agent import analyze_market
    HAS_MARKET_ANALYSIS = True
except ImportError:
    HAS_MARKET_ANALYSIS = False

def analyze_financials(
    company_name: str, 
    screening_agent: Optional[ScreeningAgent] = None,
    market_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze the financials of a startup or company.
    
    Args:
        company_name: Name of the company to analyze
        screening_agent: Optional ScreeningAgent to get data from
        market_data: Optional market analysis data to incorporate
        
    Returns:
        Financial analysis report
    """
    # Create financial agent
    financial_agent = FinancialAgent(screening_agent=screening_agent, market_data=market_data)
    
    # Execute financial analysis
    return financial_agent.execute(company_name)

def generate_report(analysis_result: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """
    Generate a markdown report from financial analysis.
    
    Args:
        analysis_result: Financial analysis from analyze_financials()
        output_path: Optional path to save the report
        
    Returns:
        Path to the saved report
    """
    financial_agent = FinancialAgent()
    return financial_agent.save_markdown_report(analysis_result, output_path)

# Main function for CLI usage
if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python Financials_agent.py <company_name> [output_path]")
        sys.exit(1)
        
    company_name = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Set up context and agents
    context = AgentContext(company_name=company_name)
    screening_agent = ScreeningAgent(context=context)
    
    # Run screening first
    print(f"Running screening for {company_name}...")
    screening_agent.execute(company_name)
    
    # Try to get market analysis data if available
    market_data = None
    if HAS_MARKET_ANALYSIS:
        try:
            print(f"Getting market analysis for {company_name}...")
            market_data = analyze_market(company_name)
        except Exception as e:
            print(f"Warning: Failed to get market analysis: {str(e)}")
    
    # Run financial analysis
    print(f"Analyzing financials for {company_name}...")
    report = analyze_financials(company_name, screening_agent, market_data)
    
    # Save report
    if output_path:
        report_path = generate_report(report, output_path)
        print(f"Financial report saved to: {report_path}")
    else:
        print(json.dumps(report, indent=2))
