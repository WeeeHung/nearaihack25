"""
Financial Agent for Multi-Agent Due Diligence System

This agent is responsible for analyzing the financial health and metrics of startups.
It receives input from the screening agent and provides detailed financial analysis.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import random
from ..base_agent import BaseAgent
from ..screening_agent.agent import ScreeningAgent

# Import Market Analysis agent if available
try:
    from ..Market_analysis_agent import analyze_market
    HAS_MARKET_ANALYSIS = True
except ImportError:
    HAS_MARKET_ANALYSIS = False

class FundingStage(str, Enum):
    """Possible funding stages for startups."""
    PRE_SEED = "Pre-seed"
    SEED = "Seed"
    SERIES_A = "Series A"
    SERIES_B = "Series B"
    SERIES_C = "Series C"
    SERIES_D_PLUS = "Series D+"
    BOOTSTRAPPED = "Bootstrapped"
    PROFITABLE = "Profitable/No External Funding"

class BusinessModel(str, Enum):
    """Common business models for startups."""
    SAAS = "Software as a Service (SaaS)"
    MARKETPLACE = "Marketplace"
    ECOMMERCE = "E-commerce"
    SUBSCRIPTION = "Subscription"
    FREEMIUM = "Freemium"
    ADVERTISING = "Advertising"
    TRANSACTION_FEE = "Transaction Fee"
    LICENSING = "Licensing"
    PROFESSIONAL_SERVICES = "Professional Services"
    HARDWARE = "Hardware/Device Sales"
    USAGE_BASED = "Usage-based"

@dataclass
class FinancialMetrics:
    """Core financial metrics for startup analysis."""
    revenue: float  # Annual revenue in millions USD
    revenue_growth: float  # YoY growth rate as percentage
    gross_margin: float  # Gross margin percentage
    burn_rate: float  # Monthly burn rate in millions USD
    runway_months: int  # Months of runway remaining
    ltv: float  # Lifetime Value in USD
    cac: float  # Customer Acquisition Cost in USD
    ltv_cac_ratio: float  # LTV/CAC ratio
    arpu: float  # Average Revenue Per User in USD
    mrr: float  # Monthly Recurring Revenue in millions USD (if applicable)
    churn_rate: float  # Monthly churn rate as percentage
    funding_stage: FundingStage  # Current funding stage
    total_funding: float  # Total funding raised in millions USD
    business_model: BusinessModel  # Business model

@dataclass
class FinancialAnalysis:
    """Complete financial analysis for a startup."""
    metrics: FinancialMetrics
    unit_economics_analysis: Dict[str, Any]
    cash_flow_analysis: Dict[str, Any]
    funding_history: List[Dict[str, Any]]
    valuation_estimate: Dict[str, Any]
    financial_health_score: float  # 0-1 score
    fundraising_readiness: float  # 0-1 score
    risk_factors: Dict[str, float]
    opportunities: List[str]
    recommendations: List[str]

class FinancialAgent(BaseAgent):
    """Agent responsible for conducting financial analysis of startups."""
    
    def __init__(self, screening_agent: Optional[ScreeningAgent] = None, market_data: Optional[Dict[str, Any]] = None):
        """
        Initialize the Financial Agent.
        
        Args:
            screening_agent: Optional ScreeningAgent instance to get data from
            market_data: Optional market analysis data to incorporate
        """
        super().__init__("financial")
        self.screening_agent = screening_agent
        self.market_data = market_data
        self.last_analysis = None
    
    def execute(self, company_name: str) -> Dict[str, Any]:
        """
        Execute financial analysis on a startup.
        
        Args:
            company_name: Name of the company to analyze
            
        Returns:
            Dict containing financial analysis results
        """
        try:
            # Get financial data from screening agent if available
            financial_data = self._get_financial_data(company_name)
            
            # Perform in-depth financial analysis
            analysis_result = self._analyze_financials(financial_data)
            
            # Generate a report from the analysis
            report = self._generate_report(analysis_result, company_name)
            
            # Store the analysis for later retrieval
            self.last_analysis = report
            
            return report
            
        except Exception as e:
            raise RuntimeError(f"Failed to analyze financials for {company_name}: {str(e)}")
    
    def get_last_analysis(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent financial analysis results.
        
        Returns:
            The last financial analysis or None if no analysis has been performed
        """
        return self.last_analysis
    
    def _get_financial_data(self, company_name: str) -> Dict[str, Any]:
        """
        Get financial data either from screening agent or by generating mock data.
        
        Args:
            company_name: Company name to analyze
            
        Returns:
            Financial data for analysis
        """
        financial_data = {}
        
        # If we have a screening agent, use it to get data
        if self.screening_agent:
            financial_data = self.screening_agent.get_financial_data()
        
        # If we have market analysis data, incorporate it
        if self.market_data:
            # Create or update the market_analysis section in financial data
            if "market_analysis" not in financial_data:
                financial_data["market_analysis"] = {}
            
            # Add market data to the financial data
            financial_data["market_analysis"].update(self.market_data)
        
        # If no data from either source, generate mock data
        if not financial_data:
            financial_data = self._generate_mock_financial_data(company_name)
            
        # Add market data if we have access to the market analysis module
        if HAS_MARKET_ANALYSIS and not self.market_data:
            try:
                # Try to get market analysis data
                market_data = analyze_market(company_name)
                if market_data:
                    if "market_analysis" not in financial_data:
                        financial_data["market_analysis"] = {}
                    financial_data["market_analysis"].update(market_data)
            except Exception as e:
                print(f"Warning: Failed to get market analysis data: {str(e)}")
        
        return financial_data
    
    def _generate_mock_financial_data(self, company_name: str) -> Dict[str, Any]:
        """Generate realistic mock financial data for development purposes."""
        # Set random seed based on company name for consistent results
        random.seed(hash(company_name) % 10000)
        
        # Generate basic financial metrics
        revenue = random.uniform(0.5, 20.0)  # $0.5M to $20M annual revenue
        growth_rate = random.uniform(15.0, 150.0)  # 15% to 150% YoY growth
        funding_stage = random.choice(list(FundingStage))
        
        # Generate funding amount based on stage
        if funding_stage == FundingStage.PRE_SEED:
            funding = random.uniform(0.1, 0.5)
        elif funding_stage == FundingStage.SEED:
            funding = random.uniform(0.5, 3.0)
        elif funding_stage == FundingStage.SERIES_A:
            funding = random.uniform(3.0, 15.0)
        elif funding_stage == FundingStage.SERIES_B:
            funding = random.uniform(15.0, 50.0)
        else:
            funding = random.uniform(30.0, 100.0)
        
        return {
            "metadata": {
                "company_name": company_name,
                "analysis_date": datetime.now().isoformat()
            },
            "financial": {
                "revenue": revenue,
                "growth_rate": growth_rate,
                "funding_stage": funding_stage.value,
                "total_funding": funding,
                "last_funding_round": {
                    "date": f"2023-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                    "amount": funding / random.uniform(1.5, 3.0),
                    "valuation": funding * random.uniform(3.0, 8.0)
                }
            }
        }
    
    def _analyze_financials(self, financial_data: Dict[str, Any]) -> FinancialAnalysis:
        """
        Analyze financial data to produce comprehensive insights.
        
        Args:
            financial_data: Financial data dictionary
            
        Returns:
            FinancialAnalysis object with detailed metrics
        """
        # Extract data from input
        metadata = financial_data.get("metadata", {})
        financial = financial_data.get("financial", {})
        market_analysis = financial_data.get("market_analysis", {})
        
        # Extract basic metrics with defaults for missing data
        revenue = financial.get("revenue", 1.0)  # Default to 1.0 to avoid division by zero
        growth_rate = financial.get("growth_rate", 10.0)  # Default to 10%
        funding_stage_str = financial.get("funding_stage", "Seed")
        total_funding = financial.get("total_funding", 1.0)  # Default to 1.0M
        
        # Use market data to enhance financial analysis if available
        market_size_str = market_analysis.get("market_size", "")
        try:
            # Try to parse market size (e.g., "$50B" -> 50.0)
            if isinstance(market_size_str, str) and market_size_str.startswith("$") and market_size_str.endswith("B"):
                market_size = float(market_size_str.replace("$", "").replace("B", ""))
            else:
                market_size = 0.0
        except:
            market_size = 0.0
            
        # Use market growth rate if available
        market_growth = market_analysis.get("growth_rate", 0.0)
        if isinstance(market_growth, str) and market_growth.endswith("%"):
            try:
                market_growth = float(market_growth.replace("%", ""))
            except:
                market_growth = 0.0
        
        # Convert string to enum
        try:
            funding_stage = FundingStage(funding_stage_str)
        except ValueError:
            funding_stage = FundingStage.SEED
        
        # Generate derived metrics
        burn_rate = revenue * random.uniform(0.05, 0.3)  # 5-30% of revenue as monthly burn
        runway_months = int((total_funding) / max(burn_rate, 0.001))  # Avoid division by zero
        gross_margin = random.uniform(0.4, 0.8) if revenue > 0 else 0.0
        business_model = random.choice(list(BusinessModel))
        
        # SaaS-specific metrics
        ltv = random.uniform(1000, 50000)
        cac = ltv / random.uniform(2, 5)  # Healthy LTV/CAC between 2-5
        ltv_cac_ratio = ltv / max(cac, 0.001)  # Avoid division by zero
        arpu = random.uniform(50, 500)
        mrr = revenue / 12.0
        churn_rate = random.uniform(0.01, 0.05)  # 1-5% monthly churn
        
        # Create financial metrics object
        metrics = FinancialMetrics(
            revenue=revenue,
            revenue_growth=growth_rate,
            gross_margin=gross_margin * 100,  # Convert to percentage
            burn_rate=burn_rate,
            runway_months=runway_months,
            ltv=ltv,
            cac=cac,
            ltv_cac_ratio=ltv_cac_ratio,
            arpu=arpu,
            mrr=mrr,
            churn_rate=churn_rate * 100,  # Convert to percentage
            funding_stage=funding_stage,
            total_funding=total_funding,
            business_model=business_model
        )
        
        # Generate unit economics analysis
        unit_economics = {
            "ltv_analysis": {
                "current_ltv": ltv,
                "optimal_ltv": ltv * random.uniform(1.2, 1.5),
                "improvement_potential": random.uniform(0.2, 0.5)
            },
            "cac_analysis": {
                "current_cac": cac,
                "optimal_cac": cac * random.uniform(0.6, 0.9),
                "improvement_potential": random.uniform(0.1, 0.4)
            },
            "payback_period": {
                "months": int(cac / max(arpu * gross_margin, 0.001)),  # Avoid division by zero
                "is_healthy": True if cac / max(arpu * gross_margin, 0.001) < 12 else False  # Avoid division by zero
            }
        }
        
        # Generate cash flow analysis
        cash_flow = {
            "current_runway": {
                "months": runway_months,
                "is_critical": runway_months < 6
            },
            "burn_analysis": {
                "monthly_burn": burn_rate,
                "quarterly_burn": burn_rate * 3,
                "annual_burn": burn_rate * 12,
                "efficiency_score": random.uniform(0.4, 0.9)
            },
            "cash_efficiency": {
                "revenue_to_funding_ratio": revenue / total_funding if total_funding > 0 else 0,
                "burn_multiple": (burn_rate * 12) / (revenue * (growth_rate / 100)) if (revenue * (growth_rate / 100)) > 0 else 0
            }
        }
        
        # Generate funding history
        funding_history = []
        if total_funding > 0:
            # Work backwards from the latest round
            remaining_funding = total_funding
            stages = [FundingStage.PRE_SEED, FundingStage.SEED, FundingStage.SERIES_A, 
                     FundingStage.SERIES_B, FundingStage.SERIES_C]
            current_index = stages.index(funding_stage) if funding_stage in stages else 0
            
            for i in range(current_index, -1, -1):
                stage = stages[i]
                if i == current_index:
                    amount = remaining_funding * random.uniform(0.4, 0.6)
                else:
                    amount = remaining_funding * random.uniform(0.2, 0.5)
                
                remaining_funding -= amount
                
                if amount > 0.05:  # Only add rounds with significant funding
                    months_ago = (current_index - i) * random.randint(6, 18)
                    funding_history.append({
                        "stage": stage.value,
                        "amount": amount,
                        "date": f"{months_ago} months ago",
                        "valuation": amount * random.uniform(3.0, 6.0),
                        "investors": random.randint(1, 5)
                    })
            
            funding_history.reverse()  # Put in chronological order
        
        # Calculate valuation based on revenue multiple and growth
        revenue_multiple = 5 + (growth_rate / 10)  # Higher growth = higher multiple
        valuation_estimate = {
            "current_valuation": revenue * revenue_multiple,
            "valuation_methodology": "Revenue Multiple",
            "revenue_multiple": revenue_multiple,
            "comparable_companies_multiple": revenue_multiple * random.uniform(0.8, 1.2),
            "projected_valuation_next_round": revenue * revenue_multiple * (1 + (growth_rate / 100))
        }
        
        # Calculate financial health and fundraising scores
        financial_health_components = {
            "runway": min(1.0, runway_months / 18),
            "growth": min(1.0, growth_rate / 100),
            "margins": gross_margin,
            "ltv_cac": min(1.0, ltv_cac_ratio / 5)
        }
        financial_health_score = sum(financial_health_components.values()) / len(financial_health_components)
        
        fundraising_components = {
            "growth": min(1.0, growth_rate / 100),
            "runway_timing": 0.8 if 3 <= runway_months <= 12 else 0.4,
            "unit_economics": min(1.0, ltv_cac_ratio / 4),
            "previous_funding": min(1.0, total_funding / 10)
        }
        fundraising_readiness = sum(fundraising_components.values()) / len(fundraising_components)
        
        # Risk factors
        risk_factors = {
            "runway_risk": 1.0 - min(1.0, runway_months / 18),
            "burn_rate_risk": 1.0 - min(1.0, (revenue / (burn_rate * 12)) / 0.5) if burn_rate > 0 else 0.0,
            "growth_sustainability_risk": 1.0 - min(1.0, revenue / 10),
            "business_model_risk": 0.3 if business_model in [BusinessModel.SAAS, BusinessModel.SUBSCRIPTION] else 0.6,
            "funding_market_risk": 0.5  # Default market risk
        }
        
        # Generate recommendations based on analysis
        recommendations = []
        
        if runway_months < 6:
            recommendations.append("Urgent: Reduce burn rate or secure bridge funding to extend runway")
        elif runway_months < 12:
            recommendations.append("Begin fundraising process within the next 3 months")
            
        if ltv_cac_ratio < 3:
            recommendations.append("Focus on improving unit economics by reducing CAC or increasing LTV")
            
        if growth_rate < 30 and revenue < 5:
            recommendations.append("Accelerate growth to reach milestones required for next funding round")
            
        if gross_margin < 50:
            recommendations.append("Investigate options to improve gross margins through pricing or cost optimization")
            
        if financial_health_score > 0.7:
            recommendations.append("Consider raising a larger round to accelerate growth")
            
        if fundraising_readiness > 0.8:
            recommendations.append("Company is well-positioned for fundraising with strong metrics")
            
        # Generate opportunities
        opportunities = []
        
        if growth_rate > 100:
            opportunities.append("High growth rate indicates strong product-market fit")
            
        if gross_margin > 70:
            opportunities.append("Excellent gross margins provide flexibility for growth investment")
            
        if ltv_cac_ratio > 4:
            opportunities.append("Strong unit economics enable aggressive customer acquisition")
            
        if runway_months > 18:
            opportunities.append("Extended runway allows focus on strategic initiatives rather than fundraising")
            
        # Final analysis object
        analysis = FinancialAnalysis(
            metrics=metrics,
            unit_economics_analysis=unit_economics,
            cash_flow_analysis=cash_flow,
            funding_history=funding_history,
            valuation_estimate=valuation_estimate,
            financial_health_score=financial_health_score,
            fundraising_readiness=fundraising_readiness,
            risk_factors=risk_factors,
            opportunities=opportunities,
            recommendations=recommendations
        )
        
        return analysis
    
    def _generate_report(self, analysis: FinancialAnalysis, company_name: str) -> Dict[str, Any]:
        """
        Generate a structured report from the financial analysis.
        
        Args:
            analysis: FinancialAnalysis object with detailed metrics
            company_name: Name of the company being analyzed
            
        Returns:
            Dictionary with structured report data
        """
        return {
            "company_name": company_name,
            "analysis_date": datetime.now().isoformat(),
            "financial_health_score": analysis.financial_health_score,
            "fundraising_readiness": analysis.fundraising_readiness,
            "summary": {
                "revenue": f"${analysis.metrics.revenue:.2f}M",
                "growth_rate": f"{analysis.metrics.revenue_growth:.1f}%",
                "burn_rate": f"${analysis.metrics.burn_rate:.2f}M/month",
                "runway": f"{analysis.metrics.runway_months} months",
                "funding_stage": analysis.metrics.funding_stage.value,
                "total_funding": f"${analysis.metrics.total_funding:.2f}M",
                "business_model": analysis.metrics.business_model.value
            },
            "unit_economics": {
                "ltv": f"${analysis.metrics.ltv:.2f}",
                "cac": f"${analysis.metrics.cac:.2f}",
                "ltv_cac_ratio": f"{analysis.metrics.ltv_cac_ratio:.2f}",
                "arpu": f"${analysis.metrics.arpu:.2f}",
                "mrr": f"${analysis.metrics.mrr:.2f}M",
                "churn_rate": f"{analysis.metrics.churn_rate:.2f}%",
                "gross_margin": f"{analysis.metrics.gross_margin:.1f}%",
                "payback_period": f"{analysis.unit_economics_analysis['payback_period']['months']} months"
            },
            "cash_flow": {
                "burn_rate": f"${analysis.metrics.burn_rate:.2f}M/month",
                "runway": f"{analysis.metrics.runway_months} months",
                "burn_multiple": f"{analysis.cash_flow_analysis['cash_efficiency']['burn_multiple']:.2f}",
                "efficiency_score": f"{analysis.cash_flow_analysis['burn_analysis']['efficiency_score']:.2f}"
            },
            "funding_history": analysis.funding_history,
            "valuation": {
                "current": f"${analysis.valuation_estimate['current_valuation']:.2f}M",
                "methodology": analysis.valuation_estimate['valuation_methodology'],
                "multiple": f"{analysis.valuation_estimate['revenue_multiple']:.2f}x revenue",
                "next_round_projection": f"${analysis.valuation_estimate['projected_valuation_next_round']:.2f}M"
            },
            "risk_assessment": {
                factor: f"{score:.2f}" for factor, score in analysis.risk_factors.items()
            },
            "opportunities": analysis.opportunities,
            "recommendations": analysis.recommendations
        }
    
    def generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """
        Generate a markdown-formatted report from the financial analysis.
        
        Args:
            report: Financial analysis report dictionary
            
        Returns:
            Markdown-formatted report string
        """
        md = f"""# Financial Analysis: {report['company_name']}

*Generated on: {report['analysis_date']}*

## Executive Summary

**Financial Health Score:** {report['financial_health_score']:.2f}/1.00  
**Fundraising Readiness:** {report['fundraising_readiness']:.2f}/1.00

### Key Metrics
- **Revenue:** {report['summary']['revenue']}
- **Growth Rate:** {report['summary']['growth_rate']}
- **Burn Rate:** {report['summary']['burn_rate']}
- **Runway:** {report['summary']['runway']}
- **Funding Stage:** {report['summary']['funding_stage']}
- **Total Funding:** {report['summary']['total_funding']}
- **Business Model:** {report['summary']['business_model']}

## Unit Economics

| Metric | Value |
|--------|-------|
| **LTV** | {report['unit_economics']['ltv']} |
| **CAC** | {report['unit_economics']['cac']} |
| **LTV/CAC Ratio** | {report['unit_economics']['ltv_cac_ratio']} |
| **ARPU** | {report['unit_economics']['arpu']} |
| **MRR** | {report['unit_economics']['mrr']} |
| **Churn Rate** | {report['unit_economics']['churn_rate']} |
| **Gross Margin** | {report['unit_economics']['gross_margin']} |
| **Payback Period** | {report['unit_economics']['payback_period']} |

## Cash Flow Analysis

- **Monthly Burn Rate:** {report['cash_flow']['burn_rate']}
- **Runway:** {report['cash_flow']['runway']}
- **Burn Multiple:** {report['cash_flow']['burn_multiple']}
- **Cash Efficiency Score:** {report['cash_flow']['efficiency_score']}

## Funding History

{self._format_funding_history_table(report['funding_history'])}

## Valuation Analysis

- **Current Valuation:** {report['valuation']['current']}
- **Valuation Methodology:** {report['valuation']['methodology']}
- **Revenue Multiple:** {report['valuation']['multiple']}
- **Next Round Projection:** {report['valuation']['next_round_projection']}

## Risk Assessment

{self._format_risk_table(report['risk_assessment'])}

## Growth Opportunities

{self._format_bullets(report['opportunities'])}

## Recommendations

{self._format_bullets(report['recommendations'])}

---

*This report was generated by the Financial Analysis Agent. Data should be verified with primary sources.*
"""
        return md
    
    def _format_funding_history_table(self, funding_history: List[Dict[str, Any]]) -> str:
        """Format funding history as a markdown table."""
        if not funding_history:
            return "No funding history available."
        
        table = "| Round | Amount | Date | Valuation | Investors |\n"
        table += "|-------|--------|------|-----------|----------|\n"
        
        for round_data in funding_history:
            table += f"| {round_data['stage']} | ${round_data['amount']:.2f}M | {round_data['date']} | "
            table += f"${round_data['valuation']:.2f}M | {round_data['investors']} |\n"
        
        return table
    
    def _format_risk_table(self, risks: Dict[str, Any]) -> str:
        """Format risk assessment as a markdown table."""
        if not risks:
            return "No risk assessment data available."
        
        table = "| Risk Factor | Score | Severity |\n"
        table += "|------------|-------|----------|\n"
        
        for factor, score_str in risks.items():
            score = float(score_str)
            severity = "High" if score > 0.7 else "Medium" if score > 0.4 else "Low"
            factor_name = factor.replace("_", " ").title()
            table += f"| {factor_name} | {score:.2f} | {severity} |\n"
        
        return table
    
    def _format_bullets(self, items: List[str]) -> str:
        """Format a list as markdown bullet points."""
        if not items:
            return "No data available."
        return "\n".join([f"- {item}" for item in items])
    
    def save_markdown_report(self, report: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate and save a markdown report to a file.
        
        Args:
            report: Financial analysis report dictionary
            output_path: Path to save the report (default: current directory)
            
        Returns:
            str: Path to the saved report
        """
        md_content = self.generate_markdown_report(report)
        
        if output_path is None:
            company_name = report['company_name'].lower().replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d")
            output_path = f"financial_analysis_{company_name}_{timestamp}.md"
        
        with open(output_path, "w") as f:
            f.write(md_content)
        
        return output_path 