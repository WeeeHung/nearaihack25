"""Mock Questflow client for development purposes."""

from typing import Dict, Any
import random

class QuestflowClient:
    """Mock client for Questflow API integration."""
    
    def __init__(self):
        self.mock_industries = [
            "Technology", "Healthcare", "Finance", "AI/ML",
            "E-commerce", "SaaS", "Biotech", "Clean Energy"
        ]
        
        self.mock_criteria_metrics = [
            "Revenue Growth", "Market Size", "Team Experience",
            "Technology Stack", "Product Market Fit", "Competition Analysis",
            "Business Model", "Financial Health"
        ]
    
    def screen_company(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock implementation of company screening.
        
        Args:
            request: Dictionary containing screening parameters
            
        Returns:
            Mock screening results
        """
        identifier = request["identifier"]
        criteria = request.get("criteria", {})
        
        # Generate mock data
        mock_revenue = random.uniform(5.0, 50.0)
        mock_growth = random.uniform(10.0, 100.0)
        mock_team_size = random.randint(3, 100)
        mock_industry = random.choice(self.mock_industries)
        
        # Calculate qualification based on criteria
        meets_revenue = mock_revenue >= criteria.get("min_revenue", 10.0)
        meets_growth = mock_growth >= criteria.get("min_growth_rate", 20.0)
        meets_team_size = mock_team_size >= criteria.get("min_team_size", 5)
        meets_industry = mock_industry in criteria.get("target_industries", [])
        
        # Generate criteria results
        criteria_met = []
        criteria_missed = []
        
        if meets_revenue:
            criteria_met.append("Revenue Threshold")
        else:
            criteria_missed.append("Revenue Threshold")
            
        if meets_growth:
            criteria_met.append("Growth Rate")
        else:
            criteria_missed.append("Growth Rate")
            
        if meets_team_size:
            criteria_met.append("Team Size")
        else:
            criteria_missed.append("Team Size")
            
        if meets_industry:
            criteria_met.append("Target Industry")
        else:
            criteria_missed.append("Target Industry")
        
        # Add some random criteria for completeness
        for _ in range(3):
            metric = random.choice(self.mock_criteria_metrics)
            if random.random() > 0.3:
                if metric not in criteria_met:
                    criteria_met.append(metric)
            else:
                if metric not in criteria_missed:
                    criteria_missed.append(metric)
        
        # Calculate overall qualification and score
        qualified = (
            meets_revenue and
            meets_growth and
            meets_team_size and
            meets_industry and
            len(criteria_met) > len(criteria_missed)
        )
        
        score = len(criteria_met) / (len(criteria_met) + len(criteria_missed))
        
        return {
            "name": f"Company {identifier}",
            "identifier": identifier,
            "industry": mock_industry,
            "revenue": mock_revenue,
            "growth_rate": mock_growth,
            "team_size": mock_team_size,
            "pitch_deck_url": f"https://example.com/pitch/{identifier}.pdf",
            "qualified": qualified,
            "score": score,
            "criteria_met": criteria_met,
            "criteria_missed": criteria_missed,
            "confidence_score": random.uniform(0.7, 1.0),
            "additional_data": {
                "market_size": f"${random.randint(1, 100)}B",
                "competitors": random.randint(3, 15),
                "funding_stage": random.choice(["Seed", "Series A", "Series B", "Series C"]),
                "last_funding": f"${random.randint(1, 50)}M"
            }
        } 