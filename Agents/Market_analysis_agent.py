import requests
import os
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

load_dotenv()

MIZU_API_KEY = os.getenv("MIZU_API_KEY")
MIZU_API_URL = "https://api.mizu.ai/v1/model/inference"

class MarketSegment(str, Enum):
    B2B = "B2B"
    B2C = "B2C"
    B2B2C = "B2B2C"
    D2C = "D2C"
    ENTERPRISE = "Enterprise"

class MarketMaturity(str, Enum):
    EMERGING = "Emerging"
    GROWING = "Growing"
    MATURE = "Mature"
    DECLINING = "Declining"
    DISRUPTED = "Disrupted"

@dataclass
class MarketMetrics:
    tam: float  # Total Addressable Market in billions USD
    sam: float  # Serviceable Addressable Market in billions USD
    som: float  # Serviceable Obtainable Market in billions USD
    growth_rate: float  # Market CAGR
    market_maturity: MarketMaturity
    market_segments: List[MarketSegment]
    market_drivers: List[str]
    market_challenges: List[str]
    regulatory_environment: str
    entry_barriers: List[str]
    exit_barriers: List[str]

@dataclass
class CompetitorAnalysis:
    name: str
    funding_stage: str
    total_funding: float
    market_share: float
    strengths: List[str]
    weaknesses: List[str]
    key_differentiators: List[str]
    pricing_strategy: str
    go_to_market: str
    recent_developments: List[str]

@dataclass
class MarketTrends:
    current_trends: List[str]
    future_predictions: List[str]
    technology_advancements: List[str]
    consumer_behavior_changes: List[str]
    regulatory_changes: List[str]
    investment_trends: List[str]
    industry_consolidation: List[str]
    emerging_opportunities: List[str]

@dataclass
class MarketReport:
    market_metrics: MarketMetrics
    competitors: List[CompetitorAnalysis]
    trends: MarketTrends
    market_attractiveness_score: float  # 0-1 score
    investment_timing_score: float  # 0-1 score
    risk_assessment: Dict[str, float]  # Risk scores for different aspects
    recommendations: List[str]
    
    def generate_markdown(self, startup_info: Dict[str, Any]) -> str:
        """
        Generate a comprehensive markdown report for the market analysis.
        
        Args:
            startup_info: Dictionary containing basic startup information
            
        Returns:
            str: Markdown formatted report
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format markdown report
        md = f"""# Market Analysis Report: {startup_info.get('name', 'Startup')}

*Generated on: {timestamp}*

## Executive Summary

**Sector:** {startup_info.get('sector', 'N/A')}
**Product Type:** {startup_info.get('product_type', 'N/A')}
**Target Market:** {startup_info.get('target_market', 'N/A')}
**Business Model:** {startup_info.get('business_model', 'N/A')}
**Geographic Focus:** {', '.join(startup_info.get('geographic_focus', ['Global']))}

### Key Metrics
- **Market Attractiveness Score:** {self.market_attractiveness_score:.2f}/1.00
- **Investment Timing Score:** {self.investment_timing_score:.2f}/1.00
- **Overall Recommendation:** {self.recommendations[0] if self.recommendations else 'No recommendation available'}

## Market Size & Opportunity

| Metric | Value |
|--------|-------|
| **Total Addressable Market (TAM)** | ${self.market_metrics.tam:.2f}B |
| **Serviceable Addressable Market (SAM)** | ${self.market_metrics.sam:.2f}B |
| **Serviceable Obtainable Market (SOM)** | ${self.market_metrics.som:.2f}B |
| **Market CAGR** | {self.market_metrics.growth_rate:.1f}% |
| **Market Maturity** | {self.market_metrics.market_maturity.value} |

### Target Market Segments
{self._format_list_as_md([seg.value for seg in self.market_metrics.market_segments])}

### Market Drivers
{self._format_list_as_md(self.market_metrics.market_drivers)}

### Market Challenges
{self._format_list_as_md(self.market_metrics.market_challenges)}

## Competitive Landscape Analysis

{self._format_competitors_table()}

### Market Entry Barriers
{self._format_list_as_md(self.market_metrics.entry_barriers)}

### Market Exit Barriers
{self._format_list_as_md(self.market_metrics.exit_barriers)}

### Regulatory Environment
{self.market_metrics.regulatory_environment}

## Market Trends & Future Outlook

### Current Trends
{self._format_list_as_md(self.trends.current_trends)}

### Future Predictions
{self._format_list_as_md(self.trends.future_predictions)}

### Technology Advancements
{self._format_list_as_md(self.trends.technology_advancements)}

### Consumer Behavior Shifts
{self._format_list_as_md(self.trends.consumer_behavior_changes)}

### Investment Climate
{self._format_list_as_md(self.trends.investment_trends)}

### Industry Consolidation Trends
{self._format_list_as_md(self.trends.industry_consolidation)}

### Emerging Opportunities
{self._format_list_as_md(self.trends.emerging_opportunities)}

## Risk Assessment

{self._format_risk_table()}

## Investment Recommendations

{self._format_list_as_md(self.recommendations)}

---

*This report was generated by the MIZU Market Analysis AI tool. Data should be verified with primary sources.*
"""
        return md
    
    def _format_list_as_md(self, items: List[str]) -> str:
        """Format a list as markdown bullet points."""
        if not items:
            return "No data available."
        return "\n".join([f"- {item}" for item in items])
    
    def _format_competitors_table(self) -> str:
        """Format competitors as a markdown table."""
        if not self.competitors:
            return "No competitor data available."
        
        table = "| Competitor | Funding Stage | Total Funding | Market Share | Key Differentiators |\n"
        table += "|------------|--------------|--------------|--------------|---------------------|\n"
        
        for comp in self.competitors:
            differentiators = ", ".join(comp.key_differentiators[:2]) if comp.key_differentiators else "N/A"
            table += f"| {comp.name} | {comp.funding_stage} | ${comp.total_funding:.1f}M | {comp.market_share:.1f}% | {differentiators} |\n"
        
        return table
    
    def _format_risk_table(self) -> str:
        """Format risk assessment as a markdown table."""
        if not self.risk_assessment:
            return "No risk assessment data available."
        
        table = "| Risk Category | Risk Score (0-1) | Severity |\n"
        table += "|--------------|-----------------|----------|\n"
        
        for risk, score in self.risk_assessment.items():
            severity = "High" if score > 0.7 else "Medium" if score > 0.4 else "Low"
            table += f"| {risk.replace('_', ' ').title()} | {score:.2f} | {severity} |\n"
        
        return table
    
    def save_markdown_report(self, startup_info: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate and save a markdown report to a file.
        
        Args:
            startup_info: Dictionary containing basic startup information
            output_path: Path to save the report (default: current directory)
            
        Returns:
            str: Path to the saved report
        """
        md_content = self.generate_markdown(startup_info)
        
        if output_path is None:
            company_name = startup_info.get('name', 'startup').lower().replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d")
            output_path = f"market_analysis_{company_name}_{timestamp}.md"
        
        with open(output_path, "w") as f:
            f.write(md_content)
        
        return output_path

class MarketAnalysisAgent:
    def __init__(self):
        self.mizuApiKey = MIZU_API_KEY
        self.mizuApiUrl = MIZU_API_URL
        
        self.marketSegments = {
            "B2B": "Business to Business",
            "B2C": "Business to Consumer",
            "B2B2C": "Business to Business to Consumer",
            "D2C": "Direct to Consumer",
            "ENTERPRISE": "Enterprise",
            "SAAS": "Software as a Service",
            "MARKETPLACE": "Marketplace",
            "HARDWARE": "Hardware",
            "CONSUMER_APPS": "Consumer Apps",
            "FINTECH": "Financial Technology",
            "HEALTHTECH": "Health Technology",
            "EDTECH": "Education Technology",
            "CLEANTECH": "Clean Technology",
            "BIOTECH": "Biotechnology",
            "AGTECH": "Agricultural Technology",
            "RETAILTECH": "Retail Technology"
        }
        
        self.marketMaturityStages = {
            "EMERGING": "Emerging",
            "GROWING": "Growing",
            "MATURE": "Mature",
            "DECLINING": "Declining",
            "DISRUPTED": "Disrupted"
        }
        
    def run(self, shortlist: Dict[str, Any]) -> Dict[str, Any]:
        try:
            payload = {
                "model_id": "market_analysis_v1",
                "data": {
                    "startupId": shortlist.get("startupId", ""),
                    "sector": shortlist.get("sector", "AI"),
                    "productType": shortlist.get("productType", ""),
                    "targetMarket": shortlist.get("targetMarket", ""),
                    "geographicFocus": shortlist.get("geographicFocus", ["Global"]),
                    "businessModel": shortlist.get("businessModel", ""),
                    "foundedYear": shortlist.get("foundedYear", 0),
                    "founderBackgrounds": shortlist.get("founderBackgrounds", []),
                    "currentRevenue": shortlist.get("currentRevenue", 0.0),
                    "currentValuation": shortlist.get("currentValuation", 0.0),
                    "totalFundingRaised": shortlist.get("totalFundingRaised", 0.0),
                    "lastFundingRound": shortlist.get("lastFundingRound", ""),
                    "competitorNames": shortlist.get("competitorNames", [])
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.mizuApiKey}",
                "Content-Type": "application/json"
            }

            response = requests.post(self.mizuApiUrl, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            
            marketReport = self.createMarketReport(result)
            return marketReport

        except requests.RequestException as e:
            errorMessage = f"Error in Market Analysis Agent: {e}"
            print(errorMessage)
            return self.createEmptyMarketReport()

    def createMarketReport(self, apiResponse: Dict[str, Any]) -> Dict[str, Any]:
        marketMetrics = {
            "marketSize": {
                "tam": apiResponse.get("tam", 0.0),
                "tamGrowthRate": apiResponse.get("tamGrowthRate", 0.0),
                "tamForecast5Year": apiResponse.get("tamForecast5Year", 0.0),
                "sam": apiResponse.get("sam", 0.0),
                "samGrowthRate": apiResponse.get("samGrowthRate", 0.0),
                "som": apiResponse.get("som", 0.0),
                "somGrowthRate": apiResponse.get("somGrowthRate", 0.0),
                "marketPenetrationRate": apiResponse.get("marketPenetrationRate", 0.0),
                "growthCeiling": apiResponse.get("growthCeiling", 0.0),
                "regionalBreakdown": apiResponse.get("regionalBreakdown", {})
            },
            "marketDynamics": {
                "maturityStage": apiResponse.get("marketMaturity", "EMERGING"),
                "marketSegments": apiResponse.get("marketSegments", []),
                "volatility": apiResponse.get("volatility", 0.0),
                "cyclicality": apiResponse.get("cyclicality", "None"),
                "seasonality": apiResponse.get("seasonality", "None"),
                "marketConcentration": apiResponse.get("marketConcentration", 0.0),
                "priceElasticity": apiResponse.get("priceElasticity", 0.0),
                "switchingCosts": apiResponse.get("switchingCosts", "Low"),
                "networkEffects": apiResponse.get("networkEffects", "None")
            },
            "marketForces": {
                "drivers": apiResponse.get("marketDrivers", []),
                "challenges": apiResponse.get("marketChallenges", []),
                "enablers": apiResponse.get("marketEnablers", []),
                "disruptors": apiResponse.get("marketDisruptors", []),
                "catalysts": apiResponse.get("marketCatalysts", [])
            },
            "marketAccess": {
                "entryBarriers": apiResponse.get("entryBarriers", []),
                "exitBarriers": apiResponse.get("exitBarriers", []),
                "regulatoryEnvironment": apiResponse.get("regulatoryEnvironment", "Unknown"),
                "regulatoryTrends": apiResponse.get("regulatoryTrends", []),
                "complianceRequirements": apiResponse.get("complianceRequirements", []),
                "certificationNeeds": apiResponse.get("certificationNeeds", []),
                "geographicRestrictions": apiResponse.get("geographicRestrictions", [])
            },
            "customerInsights": {
                "buyerTypes": apiResponse.get("buyerTypes", []),
                "buyerPersonas": apiResponse.get("buyerPersonas", []),
                "decisionMakers": apiResponse.get("decisionMakers", []),
                "buyingCriteria": apiResponse.get("buyingCriteria", []),
                "customerAcquisitionCost": apiResponse.get("customerAcquisitionCost", 0.0),
                "customerLifetimeValue": apiResponse.get("customerLifetimeValue", 0.0),
                "salesCycleDuration": apiResponse.get("salesCycleDuration", 0.0),
                "netPromoterScore": apiResponse.get("netPromoterScore", 0.0),
                "churnRate": apiResponse.get("churnRate", 0.0),
                "retentionStrategies": apiResponse.get("retentionStrategies", [])
            }
        }
        
        competitors = []
        for comp in apiResponse.get("competitors", []):
            competitor = {
                "name": comp.get("name", ""),
                "overview": {
                    "description": comp.get("description", ""),
                    "founded": comp.get("founded", 0),
                    "headquarters": comp.get("headquarters", ""),
                    "privatePubic": comp.get("privatePublic", "Private"),
                    "employeeCount": comp.get("employeeCount", 0)
                },
                "financials": {
                    "fundingStage": comp.get("fundingStage", ""),
                    "totalFunding": comp.get("totalFunding", 0.0),
                    "lastRoundDate": comp.get("lastRoundDate", ""),
                    "lastRoundAmount": comp.get("lastRoundAmount", 0.0),
                    "keyInvestors": comp.get("keyInvestors", []),
                    "revenue": comp.get("revenue", 0.0),
                    "revenueGrowth": comp.get("revenueGrowth", 0.0),
                    "valuation": comp.get("valuation", 0.0),
                    "profitability": comp.get("profitability", False)
                },
                "market": {
                    "marketShare": comp.get("marketShare", 0.0),
                    "marketShareTrend": comp.get("marketShareTrend", "Stable"),
                    "targetSegments": comp.get("targetSegments", []),
                    "geographicPresence": comp.get("geographicPresence", [])
                },
                "product": {
                    "offerings": comp.get("offerings", []),
                    "keyFeatures": comp.get("keyFeatures", []),
                    "pricingStrategy": comp.get("pricingStrategy", ""),
                    "pricingTiers": comp.get("pricingTiers", []),
                    "productMaturity": comp.get("productMaturity", "")
                },
                "strategy": {
                    "strengths": comp.get("strengths", []),
                    "weaknesses": comp.get("weaknesses", []),
                    "keyDifferentiators": comp.get("keyDifferentiators", []),
                    "goToMarket": comp.get("goToMarket", ""),
                    "partnerStrategy": comp.get("partnerStrategy", ""),
                    "acquisitionTargets": comp.get("acquisitionTargets", []),
                    "exitStrategy": comp.get("exitStrategy", "")
                },
                "recentDevelopments": comp.get("recentDevelopments", []),
                "customers": {
                    "keyCustomers": comp.get("keyCustomers", []),
                    "customerSegmentation": comp.get("customerSegmentation", {}),
                    "customerSatisfaction": comp.get("customerSatisfaction", 0.0)
                }
            }
            competitors.append(competitor)
        
        trends = {
            "currentTrends": apiResponse.get("currentTrends", []),
            "futurePredictions": apiResponse.get("futurePredictions", []),
            "technologyAdvancements": apiResponse.get("technologyAdvancements", []),
            "consumerBehaviorChanges": apiResponse.get("consumerBehaviorChanges", []),
            "regulatoryChanges": apiResponse.get("regulatoryChanges", []),
            "investmentTrends": apiResponse.get("investmentTrends", []),
            "industryConsolidation": apiResponse.get("industryConsolidation", []),
            "emergingOpportunities": apiResponse.get("emergingOpportunities", []),
            "emergingThreats": apiResponse.get("emergingThreats", []),
            "timelines": {
                "shortTerm": apiResponse.get("shortTermTrends", []),
                "mediumTerm": apiResponse.get("mediumTermTrends", []),
                "longTerm": apiResponse.get("longTermTrends", [])
            },
            "technologyAdoption": {
                "adoptionCurve": apiResponse.get("adoptionCurve", ""),
                "earlyAdopters": apiResponse.get("earlyAdopters", []),
                "massDiffusionRate": apiResponse.get("massDiffusionRate", 0.0),
                "technologicalReadiness": apiResponse.get("technologicalReadiness", 0)
            }
        }
        
        investmentMetrics = {
            "marketAttractivenessScore": apiResponse.get("marketAttractivenessScore", 0.0),
            "investmentTimingScore": apiResponse.get("investmentTimingScore", 0.0),
            "marketOpportunityScore": apiResponse.get("marketOpportunityScore", 0.0),
            "competitivePositioningScore": apiResponse.get("competitivePositioningScore", 0.0),
            "growthPotentialScore": apiResponse.get("growthPotentialScore", 0.0),
            "scalabilityScore": apiResponse.get("scalabilityScore", 0.0),
            "expectedROI": {
                "bestCase": apiResponse.get("roiBestCase", 0.0),
                "expectedCase": apiResponse.get("roiExpectedCase", 0.0),
                "worstCase": apiResponse.get("roiWorstCase", 0.0)
            },
            "investmentTimeframe": {
                "expectedTimeToExit": apiResponse.get("expectedTimeToExit", 0),
                "expectedExitMultiple": apiResponse.get("expectedExitMultiple", 0.0),
                "potentialExitPaths": apiResponse.get("potentialExitPaths", [])
            },
            "fundingRequirements": {
                "currentRound": apiResponse.get("currentRoundNeeds", 0.0),
                "nextRound": apiResponse.get("nextRoundNeeds", 0.0),
                "pathToProfitability": apiResponse.get("pathToProfitability", "")
            },
            "keyMetricsToTrack": apiResponse.get("keyMetricsToTrack", [])
        }
        
        riskAssessment = {
            "marketRisks": apiResponse.get("marketRisks", {}),
            "competitiveRisks": apiResponse.get("competitiveRisks", {}),
            "executionRisks": apiResponse.get("executionRisks", {}),
            "financialRisks": apiResponse.get("financialRisks", {}),
            "regulatoryRisks": apiResponse.get("regulatoryRisks", {}),
            "technologyRisks": apiResponse.get("technologyRisks", {}),
            "teamRisks": apiResponse.get("teamRisks", {}),
            "overallRiskProfile": apiResponse.get("overallRiskProfile", 0.0),
            "riskMitigationStrategies": apiResponse.get("riskMitigationStrategies", [])
        }
        
        strategicImplications = {
            "competitiveStrategy": {
                "recommendations": apiResponse.get("competitiveRecommendations", []),
                "differentiationOpportunities": apiResponse.get("differentiationOpportunities", []),
                "potentialAlliances": apiResponse.get("potentialAlliances", [])
            },
            "goToMarketStrategy": {
                "recommendations": apiResponse.get("goToMarketRecommendations", []),
                "channelStrategy": apiResponse.get("channelStrategyRecommendations", []),
                "pricingStrategy": apiResponse.get("pricingStrategyRecommendations", [])
            },
            "productStrategy": {
                "recommendations": apiResponse.get("productRecommendations", []),
                "featureRoadmap": apiResponse.get("featureRoadmapRecommendations", []),
                "innovationOpportunities": apiResponse.get("innovationOpportunities", [])
            },
            "geographicExpansion": {
                "recommendations": apiResponse.get("geographicRecommendations", []),
                "prioritizedMarkets": apiResponse.get("prioritizedMarkets", []),
                "entryStrategies": apiResponse.get("marketEntryStrategies", [])
            }
        }
        
        recommendations = {
            "investmentDecision": apiResponse.get("investmentDecision", ""),
            "valuationGuidance": apiResponse.get("valuationGuidance", ""),
            "termSheetNotes": apiResponse.get("termSheetNotes", []),
            "nextStepsForDueDiligence": apiResponse.get("nextStepsForDueDiligence", []),
            "shortTermRecommendations": apiResponse.get("shortTermRecommendations", []),
            "mediumTermRecommendations": apiResponse.get("mediumTermRecommendations", []),
            "longTermRecommendations": apiResponse.get("longTermRecommendations", []),
            "keySuccessFactors": apiResponse.get("keySuccessFactors", []),
            "valueCreationOpportunities": apiResponse.get("valueCreationOpportunities", [])
        }
        
        marketReport = {
            "marketMetrics": marketMetrics,
            "competitors": competitors,
            "trends": trends,
            "investmentMetrics": investmentMetrics,
            "riskAssessment": riskAssessment,
            "strategicImplications": strategicImplications,
            "recommendations": recommendations,
            "dataQuality": {
                "confidenceScore": apiResponse.get("dataConfidenceScore", 0.0),
                "dataSources": apiResponse.get("dataSources", []),
                "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "dataGaps": apiResponse.get("dataGaps", [])
            }
        }
        
        return marketReport
        
    def createEmptyMarketReport(self) -> Dict[str, Any]:
        return {
            "marketMetrics": {
                "marketSize": {"tam": 0.0, "sam": 0.0, "som": 0.0},
                "marketDynamics": {"maturityStage": "EMERGING", "marketSegments": []},
                "marketForces": {"drivers": ["Error in market analysis"], "challenges": ["API connection failed"]},
                "marketAccess": {"entryBarriers": [], "regulatoryEnvironment": "Unknown"},
                "customerInsights": {}
            },
            "competitors": [],
            "trends": {
                "currentTrends": ["Error in trend analysis"],
                "futurePredictions": [],
                "technologyAdvancements": []
            },
            "investmentMetrics": {
                "marketAttractivenessScore": 0.0,
                "investmentTimingScore": 0.0
            },
            "riskAssessment": {"marketRisks": {"api_error": 1.0}},
            "strategicImplications": {},
            "recommendations": {"investmentDecision": "Fix API connection and retry analysis"},
            "dataQuality": {"confidenceScore": 0.0, "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        }
    
    def generateMarkdownReport(self, marketReport: Dict[str, Any], startupInfo: Dict[str, Any]) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md = f"""# Market Analysis Report: {startupInfo.get('name', 'Startup')}

*Generated on: {timestamp}*

## Executive Summary

**Sector:** {startupInfo.get('sector', 'N/A')}
**Product Type:** {startupInfo.get('productType', 'N/A')}
**Target Market:** {startupInfo.get('targetMarket', 'N/A')}
**Business Model:** {startupInfo.get('businessModel', 'N/A')}
**Geographic Focus:** {', '.join(startupInfo.get('geographicFocus', ['Global']))}

### Key Investment Metrics
- **Market Attractiveness Score:** {marketReport['investmentMetrics']['marketAttractivenessScore']:.2f}/1.00
- **Investment Timing Score:** {marketReport['investmentMetrics']['investmentTimingScore']:.2f}/1.00
- **Market Opportunity Score:** {marketReport['investmentMetrics']['marketOpportunityScore']:.2f}/1.00
- **Competitive Positioning Score:** {marketReport['investmentMetrics']['competitivePositioningScore']:.2f}/1.00
- **Growth Potential Score:** {marketReport['investmentMetrics']['growthPotentialScore']:.2f}/1.00
- **Scalability Score:** {marketReport['investmentMetrics']['scalabilityScore']:.2f}/1.00
- **Investment Decision:** {marketReport['recommendations']['investmentDecision']}

## Market Size & Opportunity

| Metric | Current Value | Growth Rate | 5-Year Forecast |
|--------|--------------|-------------|-----------------|
| **Total Addressable Market (TAM)** | ${marketReport['marketMetrics']['marketSize']['tam']:.2f}B | {marketReport['marketMetrics']['marketSize']['tamGrowthRate']:.1f}% | ${marketReport['marketMetrics']['marketSize']['tamForecast5Year']:.2f}B |
| **Serviceable Addressable Market (SAM)** | ${marketReport['marketMetrics']['marketSize']['sam']:.2f}B | {marketReport['marketMetrics']['marketSize']['samGrowthRate']:.1f}% | N/A |
| **Serviceable Obtainable Market (SOM)** | ${marketReport['marketMetrics']['marketSize']['som']:.2f}B | {marketReport['marketMetrics']['marketSize']['somGrowthRate']:.1f}% | N/A |

**Market Penetration Rate:** {marketReport['marketMetrics']['marketSize']['marketPenetrationRate']:.1f}%
**Growth Ceiling:** {marketReport['marketMetrics']['marketSize']['growthCeiling']:.1f}%
**Market Maturity:** {self.marketMaturityStages.get(marketReport['marketMetrics']['marketDynamics']['maturityStage'], 'Unknown')}

### Regional Market Breakdown
{self.formatDictAsTable(marketReport['marketMetrics']['marketSize'].get('regionalBreakdown', {}))}

### Target Market Segments
{self.formatListAsBullets([self.marketSegments.get(seg, seg) for seg in marketReport['marketMetrics']['marketDynamics']['marketSegments']])}

### Market Forces

**Key Market Drivers**
{self.formatListAsBullets(marketReport['marketMetrics']['marketForces']['drivers'])}

**Market Challenges**
{self.formatListAsBullets(marketReport['marketMetrics']['marketForces']['challenges'])}

**Market Enablers**
{self.formatListAsBullets(marketReport['marketMetrics']['marketForces']['enablers'])}

**Market Disruptors**
{self.formatListAsBullets(marketReport['marketMetrics']['marketForces']['disruptors'])}

**Market Catalysts**
{self.formatListAsBullets(marketReport['marketMetrics']['marketForces']['catalysts'])}

### Market Access

**Entry Barriers**
{self.formatListAsBullets(marketReport['marketMetrics']['marketAccess']['entryBarriers'])}

**Exit Barriers**
{self.formatListAsBullets(marketReport['marketMetrics']['marketAccess']['exitBarriers'])}

**Regulatory Environment:** {marketReport['marketMetrics']['marketAccess']['regulatoryEnvironment']}

**Regulatory Trends**
{self.formatListAsBullets(marketReport['marketMetrics']['marketAccess']['regulatoryTrends'])}

**Compliance Requirements**
{self.formatListAsBullets(marketReport['marketMetrics']['marketAccess']['complianceRequirements'])}

### Customer Insights

**Buyer Types**
{self.formatListAsBullets(marketReport['marketMetrics']['customerInsights'].get('buyerTypes', []))}

**Decision Makers**
{self.formatListAsBullets(marketReport['marketMetrics']['customerInsights'].get('decisionMakers', []))}

**Customer Economics**
- Customer Acquisition Cost: ${marketReport['marketMetrics']['customerInsights'].get('customerAcquisitionCost', 0.0):.2f}
- Customer Lifetime Value: ${marketReport['marketMetrics']['customerInsights'].get('customerLifetimeValue', 0.0):.2f}
- Sales Cycle Duration: {marketReport['marketMetrics']['customerInsights'].get('salesCycleDuration', 0.0):.1f} months
- Net Promoter Score: {marketReport['marketMetrics']['customerInsights'].get('netPromoterScore', 0.0):.1f}
- Churn Rate: {marketReport['marketMetrics']['customerInsights'].get('churnRate', 0.0):.1f}%

## Competitive Landscape Analysis

{self.formatCompetitorsTable(marketReport['competitors'])}

### Competitive Dynamics
- **Market Concentration:** {marketReport['marketMetrics']['marketDynamics'].get('marketConcentration', 0.0):.1f}%
- **Switching Costs:** {marketReport['marketMetrics']['marketDynamics'].get('switchingCosts', 'Low')}
- **Network Effects:** {marketReport['marketMetrics']['marketDynamics'].get('networkEffects', 'None')}
- **Price Elasticity:** {marketReport['marketMetrics']['marketDynamics'].get('priceElasticity', 0.0):.1f}

## Market Trends & Future Outlook

### Current Trends
{self.formatListAsBullets(marketReport['trends']['currentTrends'])}

### Future Predictions
{self.formatListAsBullets(marketReport['trends']['futurePredictions'])}

### Technology Advancements
{self.formatListAsBullets(marketReport['trends']['technologyAdvancements'])}

### Consumer Behavior Shifts
{self.formatListAsBullets(marketReport['trends']['consumerBehaviorChanges'])}

### Investment Climate
{self.formatListAsBullets(marketReport['trends']['investmentTrends'])}

### Industry Consolidation Trends
{self.formatListAsBullets(marketReport['trends']['industryConsolidation'])}

### Emerging Opportunities
{self.formatListAsBullets(marketReport['trends']['emergingOpportunities'])}

### Emerging Threats
{self.formatListAsBullets(marketReport['trends']['emergingThreats'])}

### Technology Adoption
- **Adoption Curve:** {marketReport['trends']['technologyAdoption'].get('adoptionCurve', 'N/A')}
- **Early Adopters:** {', '.join(marketReport['trends']['technologyAdoption'].get('earlyAdopters', ['N/A']))}
- **Mass Diffusion Rate:** {marketReport['trends']['technologyAdoption'].get('massDiffusionRate', 0.0):.1f}%
- **Technological Readiness Level:** {marketReport['trends']['technologyAdoption'].get('technologicalReadiness', 0)}/9

## Investment Analysis

### Expected ROI
- **Best Case Scenario:** {marketReport['investmentMetrics']['expectedROI'].get('bestCase', 0.0):.1f}x
- **Expected Case Scenario:** {marketReport['investmentMetrics']['expectedROI'].get('expectedCase', 0.0):.1f}x
- **Worst Case Scenario:** {marketReport['investmentMetrics']['expectedROI'].get('worstCase', 0.0):.1f}x

### Investment Timeframe
- **Expected Time to Exit:** {marketReport['investmentMetrics']['investmentTimeframe'].get('expectedTimeToExit', 0)} years
- **Expected Exit Multiple:** {marketReport['investmentMetrics']['investmentTimeframe'].get('expectedExitMultiple', 0.0):.1f}x
- **Potential Exit Paths:** {', '.join(marketReport['investmentMetrics']['investmentTimeframe'].get('potentialExitPaths', ['N/A']))}

### Funding Requirements
- **Current Round Needs:** ${marketReport['investmentMetrics']['fundingRequirements'].get('currentRound', 0.0):.1f}M
- **Next Round Projection:** ${marketReport['investmentMetrics']['fundingRequirements'].get('nextRound', 0.0):.1f}M
- **Path to Profitability:** {marketReport['investmentMetrics']['fundingRequirements'].get('pathToProfitability', 'N/A')}

### Key Metrics to Track
{self.formatListAsBullets(marketReport['investmentMetrics'].get('keyMetricsToTrack', []))}

## Risk Assessment

{self.formatRiskTable(marketReport['riskAssessment'])}

### Risk Mitigation Strategies
{self.formatListAsBullets(marketReport['riskAssessment'].get('riskMitigationStrategies', []))}

## Strategic Implications

### Competitive Strategy Recommendations
{self.formatListAsBullets(marketReport['strategicImplications']['competitiveStrategy'].get('recommendations', []))}

### Go-to-Market Strategy Recommendations
{self.formatListAsBullets(marketReport['strategicImplications']['goToMarketStrategy'].get('recommendations', []))}

### Product Strategy Recommendations
{self.formatListAsBullets(marketReport['strategicImplications']['productStrategy'].get('recommendations', []))}

### Geographic Expansion Recommendations
{self.formatListAsBullets(marketReport['strategicImplications']['geographicExpansion'].get('recommendations', []))}

## Investment Recommendations

### Investment Decision
{marketReport['recommendations'].get('investmentDecision', 'No recommendation available')}

### Valuation Guidance
{marketReport['recommendations'].get('valuationGuidance', 'No valuation guidance available')}

### Term Sheet Notes
{self.formatListAsBullets(marketReport['recommendations'].get('termSheetNotes', []))}

### Next Steps for Due Diligence
{self.formatListAsBullets(marketReport['recommendations'].get('nextStepsForDueDiligence', []))}

### Value Creation Opportunities
{self.formatListAsBullets(marketReport['recommendations'].get('valueCreationOpportunities', []))}

### Key Success Factors
{self.formatListAsBullets(marketReport['recommendations'].get('keySuccessFactors', []))}

## Data Quality

- **Confidence Score:** {marketReport['dataQuality'].get('confidenceScore', 0.0):.2f}/1.00
- **Last Updated:** {marketReport['dataQuality'].get('lastUpdated', 'Unknown')}
- **Data Sources:** {', '.join(marketReport['dataQuality'].get('dataSources', ['N/A']))}

---

*This report was generated by the MIZU Market Analysis AI tool. Data should be verified with primary sources.*
"""
        return md
    
    def formatListAsBullets(self, items: List[str]) -> str:
        if not items:
            return "No data available."
        result = ""
        for item in items:
            result += f"- {item}\n"
        return result
    
    def formatCompetitorsTable(self, competitors: List[Dict[str, Any]]) -> str:
        if not competitors:
            return "No competitor data available."
        
        table = "| Competitor | Funding Stage | Total Funding | Market Share | Key Differentiators |\n"
        table += "|------------|--------------|--------------|--------------|---------------------|\n"
        
        for comp in competitors:
            name = comp.get("name", "N/A")
            fundingStage = comp.get("financials", {}).get("fundingStage", "N/A")
            totalFunding = comp.get("financials", {}).get("totalFunding", 0.0)
            marketShare = comp.get("market", {}).get("marketShare", 0.0)
            
            keyDifferentiators = comp.get("strategy", {}).get("keyDifferentiators", [])
            differentiatorText = "N/A"
            if len(keyDifferentiators) > 0:
                if len(keyDifferentiators) == 1:
                    differentiatorText = keyDifferentiators[0]
                else:
                    differentiatorText = keyDifferentiators[0] + ", " + keyDifferentiators[1]
            
            table += f"| {name} | {fundingStage} | ${totalFunding:.1f}M | {marketShare:.1f}% | {differentiatorText} |\n"
        
        return table
    
    def formatRiskTable(self, riskAssessment: Dict[str, Any]) -> str:
        if not riskAssessment:
            return "No risk assessment data available."
        
        table = "| Risk Category | Risk Score (0-1) | Severity | Top Risk Factors |\n"
        table += "|--------------|-----------------|----------|------------------|\n"
        
        riskCategories = [
            ("marketRisks", "Market Risks"),
            ("competitiveRisks", "Competitive Risks"),
            ("executionRisks", "Execution Risks"),
            ("financialRisks", "Financial Risks"),
            ("regulatoryRisks", "Regulatory Risks"),
            ("technologyRisks", "Technology Risks"),
            ("teamRisks", "Team Risks")
        ]
        
        for key, label in riskCategories:
            risks = riskAssessment.get(key, {})
            if not risks:
                continue
                
            avgScore = sum(risks.values()) / len(risks) if risks else 0
            severity = "High" if avgScore > 0.7 else "Medium" if avgScore > 0.4 else "Low"
            
            topFactors = []
            for factor, score in risks.items():
                if len(topFactors) < 2:
                    factorName = factor.replace("_", " ").title()
                    topFactors.append(f"{factorName} ({score:.2f})")
            
            factorText = ", ".join(topFactors) if topFactors else "None identified"
            table += f"| {label} | {avgScore:.2f} | {severity} | {factorText} |\n"
        
        return table
    
    def formatDictAsTable(self, data: Dict[str, Any]) -> str:
        if not data:
            return "No data available."
        
        table = "| Region | Market Size | Growth Rate |\n"
        table += "|--------|-------------|-------------|\n"
        
        for region, details in data.items():
            if isinstance(details, dict):
                size = details.get("size", 0.0)
                growth = details.get("growth", 0.0)
                table += f"| {region} | ${size:.2f}B | {growth:.1f}% |\n"
            else:
                table += f"| {region} | {details} | N/A |\n"
        
        return table
    
    def saveMarkdownReport(self, marketReport: Dict[str, Any], startupInfo: Dict[str, Any], outputPath: str = None) -> str:
        mdContent = self.generateMarkdownReport(marketReport, startupInfo)
        
        if outputPath is None:
            companyName = startupInfo.get("name", "startup").lower().replace(" ", "_")
            timestamp = datetime.now().strftime("%Y%m%d")
            outputPath = f"market_analysis_{companyName}_{timestamp}.md"
        
        with open(outputPath, "w") as f:
            f.write(mdContent)
        
        return outputPath

if __name__ == "__main__":
    agent = MarketAnalysisAgent()
    
    testStartupInfo = {
        "startupId": "123",
        "score": 8.5,
        "name": "InnovateAI Health",
        "sector": "AI",
        "productType": "Enterprise SaaS",
        "targetMarket": "Healthcare",
        "geographicFocus": ["North America", "Europe"],
        "businessModel": "Subscription",
        "foundedYear": 2020,
        "founderBackgrounds": ["Healthcare", "AI Research"],
        "currentRevenue": 2.5,
        "currentValuation": 25.0,
        "totalFundingRaised": 8.5,
        "lastFundingRound": "Series A",
        "competitorNames": ["HealthAI", "MedTech Solutions", "Doctor AI"]
    }
    
    marketReport = agent.run(testStartupInfo)
    
    print(f"Market Analysis Report Summary:")
    print(f"TAM: ${marketReport['marketMetrics']['marketSize']['tam']}B")
    print(f"Market Maturity: {agent.marketMaturityStages.get(marketReport['marketMetrics']['marketDynamics']['maturityStage'], 'Unknown')}")
    print(f"Market Attractiveness Score: {marketReport['investmentMetrics']['marketAttractivenessScore']}")
    print(f"Investment Timing Score: {marketReport['investmentMetrics']['investmentTimingScore']}")
    print(f"Number of Competitors: {len(marketReport['competitors'])}")
    print(f"Investment Decision: {marketReport['recommendations'].get('investmentDecision', 'N/A')}")
    print("-" * 50)
    
    reportPath = agent.saveMarkdownReport(marketReport, testStartupInfo)
    print(f"Full markdown report saved to: {reportPath}")
    
    mdPreview = agent.generateMarkdownReport(marketReport, testStartupInfo).split("\n\n")[0:5]
    print("\nMarkdown Report Preview:")
    print("-" * 50)
    print("\n\n".join(mdPreview) + "\n...(full report in saved file)")