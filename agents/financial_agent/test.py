"""
Test script for Financial Agent

This script demonstrates how to use the Financial Agent with and without the Screening Agent.
"""

import json
import os
from typing import Dict, Any
from .agent import FinancialAgent
from ..screening_agent.agent import ScreeningAgent
from ..base_agent import AgentContext

# Try to import market analysis
try:
    from ..Market_analysis_agent import analyze_market
    HAS_MARKET_ANALYSIS = True
except ImportError:
    HAS_MARKET_ANALYSIS = False

def test_with_screening_agent():
    """Test Financial Agent with Screening Agent integration."""
    print("\n=== Testing Financial Agent with Screening Agent Integration ===\n")
    
    # Set up screening agent
    context = AgentContext(company_name="TechStartup123")
    screening_agent = ScreeningAgent(context=context)
    
    # Run screening first
    print("Running Screening Agent...")
    screening_agent.execute("TechStartup123")
    
    # Set up financial agent with screening agent
    financial_agent = FinancialAgent(screening_agent=screening_agent)
    
    # Run financial analysis
    print("Running Financial Agent with data from Screening Agent...")
    report = financial_agent.execute("TechStartup123")
    
    # Save the report as markdown
    report_path = financial_agent.save_markdown_report(report, "financial_analysis_with_screening.md")
    print(f"Financial report saved to: {report_path}")
    
    print("\nSummary:")
    print(f"Revenue: {report['summary']['revenue']}")
    print(f"Growth Rate: {report['summary']['growth_rate']}")
    print(f"Financial Health Score: {report['financial_health_score']:.2f}")
    print(f"Fundraising Readiness: {report['fundraising_readiness']:.2f}")
    
    return report

def test_with_market_data():
    """Test Financial Agent with Market Analysis integration."""
    if not HAS_MARKET_ANALYSIS:
        print("\n=== Cannot test Market Analysis integration - module not available ===\n")
        return None
        
    print("\n=== Testing Financial Agent with Market Analysis Integration ===\n")
    
    # Get market analysis data
    company_name = "MarketAwareStartup"
    print(f"Getting market analysis for {company_name}...")
    try:
        market_data = analyze_market(company_name)
        
        # Set up financial agent with market data
        financial_agent = FinancialAgent(market_data=market_data)
        
        # Run financial analysis
        print("Running Financial Agent with market analysis data...")
        report = financial_agent.execute(company_name)
        
        # Save the report as markdown
        report_path = financial_agent.save_markdown_report(report, "financial_analysis_with_market_data.md")
        print(f"Financial report saved to: {report_path}")
        
        print("\nSummary:")
        print(f"Revenue: {report['summary']['revenue']}")
        print(f"Growth Rate: {report['summary']['growth_rate']}")
        print(f"Financial Health Score: {report['financial_health_score']:.2f}")
        print(f"Fundraising Readiness: {report['fundraising_readiness']:.2f}")
        
        return report
    except Exception as e:
        print(f"Error testing with market data: {str(e)}")
        return None

def test_standalone():
    """Test Financial Agent in standalone mode with mock data."""
    print("\n=== Testing Financial Agent in Standalone Mode ===\n")
    
    # Set up financial agent without screening agent
    financial_agent = FinancialAgent()
    
    # Run financial analysis (will use mock data)
    print("Running Financial Agent with mock data...")
    report = financial_agent.execute("AnotherStartup456")
    
    # Save the report as markdown
    report_path = financial_agent.save_markdown_report(report, "financial_analysis_standalone.md")
    print(f"Financial report saved to: {report_path}")
    
    print("\nSummary:")
    print(f"Revenue: {report['summary']['revenue']}")
    print(f"Growth Rate: {report['summary']['growth_rate']}")
    print(f"Financial Health Score: {report['financial_health_score']:.2f}")
    print(f"Fundraising Readiness: {report['fundraising_readiness']:.2f}")
    
    return report

def test_complete_integration():
    """Test Financial Agent with both Screening and Market Analysis data."""
    if not HAS_MARKET_ANALYSIS:
        print("\n=== Cannot test complete integration - Market Analysis module not available ===\n")
        return None
        
    print("\n=== Testing Financial Agent with Complete Integration ===\n")
    
    company_name = "FullIntegrationCorp"
    
    # Set up screening agent
    context = AgentContext(company_name=company_name)
    screening_agent = ScreeningAgent(context=context)
    
    # Run screening first
    print("Running Screening Agent...")
    screening_agent.execute(company_name)
    
    # Get market analysis data
    print(f"Getting market analysis for {company_name}...")
    try:
        market_data = analyze_market(company_name)
        
        # Set up financial agent with both data sources
        financial_agent = FinancialAgent(
            screening_agent=screening_agent,
            market_data=market_data
        )
        
        # Run financial analysis
        print("Running Financial Agent with complete integration...")
        report = financial_agent.execute(company_name)
        
        # Save the report as markdown
        report_path = financial_agent.save_markdown_report(report, "financial_analysis_complete.md")
        print(f"Financial report saved to: {report_path}")
        
        print("\nSummary:")
        print(f"Revenue: {report['summary']['revenue']}")
        print(f"Growth Rate: {report['summary']['growth_rate']}")
        print(f"Financial Health Score: {report['financial_health_score']:.2f}")
        print(f"Fundraising Readiness: {report['fundraising_readiness']:.2f}")
        
        return report
    except Exception as e:
        print(f"Error testing complete integration: {str(e)}")
        return None

if __name__ == "__main__":
    # Run tests
    try:
        # Try with screening agent
        with_screening = test_with_screening_agent()
        print("\n" + "="*50 + "\n")
        
        # Try with market data
        with_market = test_with_market_data()
        if with_market:
            print("\n" + "="*50 + "\n")
        
        # Try standalone
        standalone = test_standalone()
        print("\n" + "="*50 + "\n")
        
        # Try complete integration
        complete = test_complete_integration()
        
        print("\nTests completed successfully!")
    except Exception as e:
        print(f"Error during testing: {str(e)}") 