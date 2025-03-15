import pytest
import json
import os
from unittest.mock import patch, MagicMock

# Import required modules (update based on your project structure)
try:
    from agents.base_agent import BaseAgent
    from agents.screening_agent import ScreeningAgent
    from agents.market_analysis_agent import MarketAnalysisAgent
    from agents.competitors_agent import CompetitorsAgent
    from agents.tech_dd_agent import TechDDAgent
    from agents.due_diligence_report_agent import DueDiligenceReportAgent
    HAS_AGENTS = True
except ImportError:
    HAS_AGENTS = False

# Skip all tests if agents are not available
pytestmark = pytest.mark.skipif(not HAS_AGENTS, reason="Agent modules not available")

class TestAgentIntegration:
    """Test the integration between different agents."""
    
    @patch("agents.screening_agent.ScreeningAgent._call_llm")
    @patch("agents.market_analysis_agent.MarketAnalysisAgent._call_llm")
    def test_screening_to_market_analysis(self, mock_market_llm, mock_screening_llm, sample_company_data):
        """Test the flow from screening to market analysis."""
        # Mock screening response
        mock_screening_llm.return_value = json.dumps({
            "initial_assessment": "Promising",
            "key_areas_to_investigate": [
                "Market growth potential",
                "Technical differentiation"
            ],
            "risk_level": "Medium"
        })
        
        # Mock market analysis response
        mock_market_llm.return_value = json.dumps({
            "market_size": "$12.5B",
            "growth_rate": "18% CAGR",
            "key_trends": ["AI adoption"],
            "competitive_landscape": "Moderately competitive"
        })
        
        # Run the integration flow
        screening_agent = ScreeningAgent(company_name=sample_company_data["name"])
        screening_result = screening_agent.analyze(sample_company_data)
        
        # Pass screening result to market analysis
        market_agent = MarketAnalysisAgent(company_name=sample_company_data["name"])
        combined_data = {**sample_company_data, "screening_results": screening_result}
        market_result = market_agent.analyze(combined_data)
        
        # Assertions
        assert screening_result["initial_assessment"] == "Promising"
        assert market_result["market_size"] == "$12.5B"
        
        # Verify both agents called their respective LLMs
        mock_screening_llm.assert_called_once()
        mock_market_llm.assert_called_once()
    
    @patch("agents.market_analysis_agent.MarketAnalysisAgent._call_llm")
    @patch("agents.competitors_agent.CompetitorsAgent._call_llm")
    def test_market_to_competitors(self, mock_competitors_llm, mock_market_llm, sample_company_data):
        """Test the flow from market analysis to competitors analysis."""
        # Mock market analysis response
        mock_market_llm.return_value = json.dumps({
            "market_size": "$12.5B",
            "growth_rate": "18% CAGR",
            "key_trends": ["AI adoption"],
            "competitive_landscape": "Moderately competitive"
        })
        
        # Mock competitors response
        mock_competitors_llm.return_value = json.dumps({
            "main_competitors": [
                {"name": "CompetitorA", "strengths": ["Established brand"]}
            ],
            "competitive_advantages": ["Innovative technology"],
            "competitive_threats": ["New market entrants"]
        })
        
        # Run the integration flow
        market_agent = MarketAnalysisAgent(company_name=sample_company_data["name"])
        market_result = market_agent.analyze(sample_company_data)
        
        # Pass market result to competitors analysis
        competitors_agent = CompetitorsAgent(company_name=sample_company_data["name"])
        combined_data = {**sample_company_data, "market_analysis": market_result}
        competitors_result = competitors_agent.analyze(combined_data)
        
        # Assertions
        assert market_result["competitive_landscape"] == "Moderately competitive"
        assert len(competitors_result["main_competitors"]) == 1
        
        # Verify both agents called their respective LLMs
        mock_market_llm.assert_called_once()
        mock_competitors_llm.assert_called_once()

    @patch("agents.due_diligence_report_agent.DueDiligenceReportAgent._call_llm")
    def test_final_report_integration(self, mock_report_llm, sample_company_data, mock_agent_output):
        """Test the integration of all agent outputs into a final report."""
        # Mock report generation response
        mock_report_llm.return_value = json.dumps({
            "executive_summary": "TechInnovate Inc. is a promising investment target...",
            "key_findings": [
                "Strong market position in growing industry",
                "Solid technical foundation with innovative approach"
            ],
            "risk_assessment": "Medium",
            "recommendation": "Proceed with investment consideration pending further technical validation"
        })
        
        # Combine all agent outputs
        combined_data = {
            **sample_company_data,
            **mock_agent_output
        }
        
        # Generate the final report
        report_agent = DueDiligenceReportAgent(company_name=sample_company_data["name"])
        report = report_agent.analyze(combined_data)
        
        # Assertions
        assert "executive_summary" in report
        assert "key_findings" in report
        assert "risk_assessment" in report
        assert "recommendation" in report
        
        # Verify report agent called the LLM
        mock_report_llm.assert_called_once()
