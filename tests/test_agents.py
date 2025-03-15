import pytest
import json
import os
from unittest.mock import patch, MagicMock

# Import agent classes (update these paths based on your actual project structure)
try:
    from agents.base_agent import BaseAgent
    from agents.screening_agent import ScreeningAgent
    from agents.market_analysis_agent import MarketAnalysisAgent
    from agents.competitors_agent import CompetitorsAgent
    from agents.tech_dd_agent import TechDDAgent
    HAS_AGENTS = True
except ImportError:
    HAS_AGENTS = False

# Skip all tests if agents are not available
pytestmark = pytest.mark.skipif(not HAS_AGENTS, reason="Agent modules not available")

class TestBaseAgent:
    """Tests for the base agent functionality."""
    
    def test_base_agent_initialization(self):
        """Test that BaseAgent initializes correctly."""
        agent = BaseAgent(company_name="Test Company")
        assert agent.company_name == "Test Company"
        
    def test_base_agent_methods(self):
        """Test that BaseAgent has required methods."""
        agent = BaseAgent(company_name="Test Company")
        assert hasattr(agent, "analyze")
        assert callable(getattr(agent, "analyze"))


class TestScreeningAgent:
    """Tests for the Screening Agent."""
    
    @patch("agents.screening_agent.ScreeningAgent._call_llm")
    def test_screening_analysis(self, mock_call_llm, sample_company_data):
        """Test that ScreeningAgent performs initial screening correctly."""
        # Mock LLM response
        mock_call_llm.return_value = json.dumps({
            "initial_assessment": "Promising",
            "key_areas_to_investigate": [
                "Market growth potential",
                "Technical differentiation",
                "Team experience"
            ],
            "risk_level": "Medium"
        })
        
        agent = ScreeningAgent(company_name=sample_company_data["name"])
        result = agent.analyze(sample_company_data)
        
        # Verify the result structure
        assert "initial_assessment" in result
        assert "key_areas_to_investigate" in result
        assert isinstance(result["key_areas_to_investigate"], list)
        assert "risk_level" in result
        
        # Verify the agent called the LLM
        mock_call_llm.assert_called_once()


class TestMarketAnalysisAgent:
    """Tests for the Market Analysis Agent."""
    
    @patch("agents.market_analysis_agent.MarketAnalysisAgent._call_llm")
    def test_market_analysis(self, mock_call_llm, sample_company_data):
        """Test that MarketAnalysisAgent analyzes the market correctly."""
        # Mock LLM response
        mock_call_llm.return_value = json.dumps({
            "market_size": "$12.5B",
            "growth_rate": "18% CAGR",
            "key_trends": [
                "Increasing adoption of AI in enterprise workflows",
                "Shift towards low-code/no-code solutions"
            ],
            "competitive_landscape": "Moderately competitive"
        })
        
        agent = MarketAnalysisAgent(company_name=sample_company_data["name"])
        result = agent.analyze(sample_company_data)
        
        # Verify the result structure
        assert "market_size" in result
        assert "growth_rate" in result
        assert "key_trends" in result
        assert "competitive_landscape" in result
        
        # Verify the agent called the LLM
        mock_call_llm.assert_called_once()


class TestCompetitorsAgent:
    """Tests for the Competitors Agent."""
    
    @patch("agents.competitors_agent.CompetitorsAgent._call_llm")
    def test_competitors_analysis(self, mock_call_llm, sample_company_data):
        """Test that CompetitorsAgent analyzes competitors correctly."""
        # Mock LLM response
        mock_call_llm.return_value = json.dumps({
            "main_competitors": [
                {"name": "CompetitorA", "strengths": ["Established brand"], "weaknesses": ["Legacy technology"]},
                {"name": "CompetitorB", "strengths": ["Strong funding"], "weaknesses": ["Limited market reach"]}
            ],
            "competitive_advantages": ["Innovative technology", "Superior UX"],
            "competitive_threats": ["New market entrants", "Regulatory changes"]
        })
        
        agent = CompetitorsAgent(company_name=sample_company_data["name"])
        result = agent.analyze(sample_company_data)
        
        # Verify the result structure
        assert "main_competitors" in result
        assert isinstance(result["main_competitors"], list)
        assert "competitive_advantages" in result
        assert "competitive_threats" in result
        
        # Verify the agent called the LLM
        mock_call_llm.assert_called_once()


class TestTechDDAgent:
    """Tests for the Technical Due Diligence Agent."""
    
    @patch("agents.tech_dd_agent.TechDDAgent._call_llm")
    def test_tech_dd_analysis(self, mock_call_llm, sample_company_data):
        """Test that TechDDAgent performs technical due diligence correctly."""
        # Mock LLM response
        mock_call_llm.return_value = json.dumps({
            "technology_stack": ["Python", "TensorFlow", "AWS"],
            "technical_innovations": ["Custom NLP model", "Automated workflow engine"],
            "technical_debt": "Low to Medium",
            "scalability_assessment": "Good"
        })
        
        agent = TechDDAgent(company_name=sample_company_data["name"])
        result = agent.analyze(sample_company_data)
        
        # Verify the result structure
        assert "technology_stack" in result
        assert "technical_innovations" in result
        assert "technical_debt" in result
        assert "scalability_assessment" in result
        
        # Verify the agent called the LLM
        mock_call_llm.assert_called_once()
