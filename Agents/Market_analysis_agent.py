import os
import json
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from pocketflow import Node, Flow
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import openai


from base_agent import BaseAgent


load_dotenv()


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
   growthRate: float  # Market CAGR
   marketMaturity: MarketMaturity
   marketSegments: List[MarketSegment]
   marketDrivers: List[str]
   marketChallenges: List[str]
   regulatoryEnvironment: str
   entryBarriers: List[str]
   exitBarriers: List[str]


@dataclass
class CompetitorAnalysis:
   name: str
   fundingStage: str
   totalFunding: float
   marketShare: float
   strengths: List[str]
   weaknesses: List[str]
   keyDifferentiators: List[str]
   pricingStrategy: str
   goToMarket: str
   recentDevelopments: List[str]


@dataclass
class MarketTrends:
   currentTrends: List[str]
   futurePredictions: List[str]
   technologyAdvancements: List[str]
   consumerBehaviorChanges: List[str]
   regulatoryChanges: List[str]
   investmentTrends: List[str]
   industryConsolidation: List[str]
   emergingOpportunities: List[str]


@dataclass
class MarketReport:
   marketMetrics: MarketMetrics
   competitors: List[CompetitorAnalysis]
   trends: MarketTrends
   marketAttractivenessScore: float  # 0-1 score
   investmentTimingScore: float  # 0-1 score
   riskAssessment: Dict[str, float]  # Risk scores for different aspects
   recommendations: List[str]
   references: List[Dict[str, str]]  # References for information sources
  
   def generateMarkdown(self, startupInfo: Dict[str, Any]) -> str:
       """
       Generate a comprehensive markdown report for the market analysis.
      
       Args:
           startupInfo: Dictionary containing basic startup information
          
       Returns:
           str: Markdown formatted report
       """
       timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      
       # Format markdown report
       md = f"""# Market Analysis Report: {startupInfo.get('name', 'Startup')}


*Generated on: {timestamp}*


## Executive Summary


**Sector:** {startupInfo.get('sector', 'N/A')}
**Product Type:** {startupInfo.get('productType', 'N/A')}
**Target Market:** {startupInfo.get('targetMarket', 'N/A')}
**Business Model:** {startupInfo.get('businessModel', 'N/A')}
**Geographic Focus:** {', '.join(startupInfo.get('geographicFocus', ['Global']))}


### Key Metrics
- **Market Attractiveness Score:** {self.marketAttractivenessScore:.2f}/1.00
- **Investment Timing Score:** {self.investmentTimingScore:.2f}/1.00
- **Overall Recommendation:** {self.recommendations[0] if self.recommendations else 'No recommendation available'}


## Market Size & Opportunity


| Metric | Value |
|--------|-------|
| **Total Addressable Market (TAM)** | ${self.marketMetrics.tam:.2f}B |
| **Serviceable Addressable Market (SAM)** | ${self.marketMetrics.sam:.2f}B |
| **Serviceable Obtainable Market (SOM)** | ${self.marketMetrics.som:.2f}B |
| **Market CAGR** | {self.marketMetrics.growthRate:.1f}% |
| **Market Maturity** | {self.marketMetrics.marketMaturity.value} |


### Target Market Segments
{self._formatListAsMd([seg.value for seg in self.marketMetrics.marketSegments])}


### Market Drivers
{self._formatListAsMd(self.marketMetrics.marketDrivers)}


### Market Challenges
{self._formatListAsMd(self.marketMetrics.marketChallenges)}


## Competitive Landscape Analysis


{self._formatCompetitorsTable()}


### Market Entry Barriers
{self._formatListAsMd(self.marketMetrics.entryBarriers)}


### Market Exit Barriers
{self._formatListAsMd(self.marketMetrics.exitBarriers)}


### Regulatory Environment
{self.marketMetrics.regulatoryEnvironment}


## Market Trends & Future Outlook


### Current Trends
{self._formatListAsMd(self.trends.currentTrends)}


### Future Predictions
{self._formatListAsMd(self.trends.futurePredictions)}


### Technology Advancements
{self._formatListAsMd(self.trends.technologyAdvancements)}


### Consumer Behavior Shifts
{self._formatListAsMd(self.trends.consumerBehaviorChanges)}


### Investment Climate
{self._formatListAsMd(self.trends.investmentTrends)}


### Industry Consolidation Trends
{self._formatListAsMd(self.trends.industryConsolidation)}


### Emerging Opportunities
{self._formatListAsMd(self.trends.emergingOpportunities)}


## Risk Assessment


{self._formatRiskTable()}


## Investment Recommendations


{self._formatListAsMd(self.recommendations)}


## References


{self._formatReferences()}


---


*This report was generated by an AI market analysis tool. Data should be verified with primary sources.*
"""
       return md
  
   def _formatListAsMd(self, items: List[str]) -> str:
       """Format a list as markdown bullet points."""
       if not items:
           return "No data available."
       result = ""
       for item in items:
           result += f"- {item}\n"
       return result
  
   def _formatCompetitorsTable(self) -> str:
       """Format competitors as a markdown table."""
       if not self.competitors:
           return "No competitor data available."
      
       table = "| Competitor | Funding Stage | Total Funding | Market Share | Key Differentiators |\n"
       table += "|------------|--------------|--------------|--------------|---------------------|\n"
      
       for comp in self.competitors:
           differentiators = ""
           if comp.keyDifferentiators:
               if len(comp.keyDifferentiators) >= 1:
                   differentiators = comp.keyDifferentiators[0]
               if len(comp.keyDifferentiators) >= 2:
                   differentiators += ", " + comp.keyDifferentiators[1]
           else:
               differentiators = "N/A"
              
           table += f"| {comp.name} | {comp.fundingStage} | ${comp.totalFunding:.1f}M | {comp.marketShare:.1f}% | {differentiators} |\n"
      
       return table
  
   def _formatRiskTable(self) -> str:
       """Format risk assessment as a markdown table."""
       if not self.riskAssessment:
           return "No risk assessment data available."
      
       table = "| Risk Category | Risk Score (0-1) | Severity |\n"
       table += "|--------------|-----------------|----------|\n"
      
       for risk, score in self.riskAssessment.items():
           severity = "High" if score > 0.7 else "Medium" if score > 0.4 else "Low"
           riskFormatted = risk.replace('_', ' ').title()
           table += f"| {riskFormatted} | {score:.2f} | {severity} |\n"
      
       return table
  
   def _formatReferences(self) -> str:
       """Format references as markdown list."""
       if not self.references:
           return "No external references used."
      
       result = ""
       for i, ref in enumerate(self.references, 1):
           result += f"{i}. **{ref.get('section', 'General')}**: {ref.get('source', 'Unknown')}"
           if 'url' in ref:
               result += f" - [{ref.get('url', '#')}]({ref.get('url', '#')})"
           result += "\n"
      
       return result
  
   def saveMarkdownReport(self, startupInfo: Dict[str, Any], outputPath: str = None) -> str:
       """
       Generate and save a markdown report to a file.
      
       Args:
           startupInfo: Dictionary containing basic startup information
           outputPath: Path to save the report (default: current directory)
          
       Returns:
           str: Path to the saved report
       """
       mdContent = self.generateMarkdown(startupInfo)
      
       if outputPath is None:
           companyName = startupInfo.get('name', 'startup').lower().replace(' ', '_')
           timestamp = datetime.now().strftime("%Y%m%d")
           outputPath = f"market_analysis_{companyName}_{timestamp}.md"
      
       with open(outputPath, "w") as f:
           f.write(mdContent)
      
       return outputPath


class MarketAnalysisNode(BaseAgent):
   """Node for analyzing market data for a startup."""
  
   def __init__(self, max_retries=3, wait=0):
       super().__init__(name="MarketAnalysisNode", max_retries=max_retries, wait=wait)
       self.references = []
      
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
  
   def prep(self, shared):
       """Prepare data for market analysis."""
       # Extract data from screening agent JSON
       screeningData = shared.get("screening_data", {})
       startupInfo = {
           "name": screeningData.get("name", "Unknown Startup"),
           "sector": screeningData.get("sector", "Technology"),
           "productType": screeningData.get("productType", "Software"),
           "targetMarket": screeningData.get("targetMarket", "Enterprise"),
           "businessModel": screeningData.get("businessModel", "SaaS"),
           "geographicFocus": screeningData.get("geographicFocus", ["Global"]),
           "foundedYear": screeningData.get("foundedYear", 0),
           "founderBackgrounds": screeningData.get("founderBackgrounds", []),
           "competitorNames": screeningData.get("competitorNames", [])
       }
      
       return startupInfo
  
   def exec(self, startupInfo):
       """Execute market analysis logic."""
       # Create initial market report with available data
       marketReport = self.createInitialMarketReport(startupInfo)
      
       # Fill in missing information using OpenAI
       self.fillMissingInformation(marketReport, startupInfo)
      
       # Calculate scores and final metrics
       self.calculateScores(marketReport, startupInfo)
      
       return marketReport
  
   def post(self, shared, prepRes, execRes):
       """Process results and store in shared data."""
       # Add market analysis report to shared storage
       shared["market_analysis"] = execRes
      
       # Add references if any
       if self.references:
           shared["market_analysis"]["references"] = self.references
      
       return "default"
  
   def createInitialMarketReport(self, startupInfo: Dict[str, Any]) -> Dict[str, Any]:
       """
       Create initial market report structure with available data.
      
       Args:
           startupInfo: Dictionary with startup information
          
       Returns:
           Dict containing initial market report
       """
       marketMetrics = {
           "marketSize": {
               "tam": 0.0,
               "tamGrowthRate": 0.0,
               "tamForecast5Year": 0.0,
               "sam": 0.0,
               "samGrowthRate": 0.0,
               "som": 0.0,
               "somGrowthRate": 0.0,
               "marketPenetrationRate": 0.0,
               "growthCeiling": 0.0,
               "regionalBreakdown": {}
           },
           "marketDynamics": {
               "maturityStage": "EMERGING",
               "marketSegments": [],
               "volatility": 0.0,
               "cyclicality": "None",
               "seasonality": "None",
               "marketConcentration": 0.0,
               "priceElasticity": 0.0,
               "switchingCosts": "Low",
               "networkEffects": "None"
           },
           "marketForces": {
               "drivers": [],
               "challenges": [],
               "enablers": [],
               "disruptors": [],
               "catalysts": []
           },
           "marketAccess": {
               "entryBarriers": [],
               "exitBarriers": [],
               "regulatoryEnvironment": "Unknown",
               "regulatoryTrends": [],
               "complianceRequirements": [],
               "certificationNeeds": [],
               "geographicRestrictions": []
           },
           "customerInsights": {
               "buyerTypes": [],
               "buyerPersonas": [],
               "decisionMakers": [],
               "buyingCriteria": [],
               "customerAcquisitionCost": 0.0,
               "customerLifetimeValue": 0.0,
               "salesCycleDuration": 0.0,
               "netPromoterScore": 0.0,
               "churnRate": 0.0,
               "retentionStrategies": []
           }
       }
      
       # Extract competitor information if available
       competitors = []
       for compName in startupInfo.get("competitorNames", []):
           competitors.append({
               "name": compName,
               "overview": {
                   "description": "",
                   "founded": 0,
                   "headquarters": "",
                   "privatePubic": "Private",
                   "employeeCount": 0
               },
               "financials": {
                   "fundingStage": "",
                   "totalFunding": 0.0,
                   "lastRoundDate": "",
                   "lastRoundAmount": 0.0,
                   "keyInvestors": [],
                   "revenue": 0.0,
                   "revenueGrowth": 0.0,
                   "valuation": 0.0,
                   "profitability": False
               },
               "market": {
                   "marketShare": 0.0,
                   "marketShareTrend": "Stable",
                   "targetSegments": [],
                   "geographicPresence": []
               },
               "product": {
                   "offerings": [],
                   "keyFeatures": [],
                   "pricingStrategy": "",
                   "pricingTiers": [],
                   "productMaturity": ""
               },
               "strategy": {
                   "strengths": [],
                   "weaknesses": [],
                   "keyDifferentiators": [],
                   "goToMarket": "",
                   "partnerStrategy": "",
                   "acquisitionTargets": [],
                   "exitStrategy": ""
               },
               "recentDevelopments": [],
               "customers": {
                   "keyCustomers": [],
                   "customerSegmentation": {},
                   "customerSatisfaction": 0.0
               }
           })
      
       trends = {
           "currentTrends": [],
           "futurePredictions": [],
           "technologyAdvancements": [],
           "consumerBehaviorChanges": [],
           "regulatoryChanges": [],
           "investmentTrends": [],
           "industryConsolidation": [],
           "emergingOpportunities": [],
           "emergingThreats": [],
           "timelines": {
               "shortTerm": [],
               "mediumTerm": [],
               "longTerm": []
           },
           "technologyAdoption": {
               "adoptionCurve": "",
               "earlyAdopters": [],
               "massDiffusionRate": 0.0,
               "technologicalReadiness": 0
           }
       }
      
       investmentMetrics = {
           "marketAttractivenessScore": 0.0,
           "investmentTimingScore": 0.0,
           "marketOpportunityScore": 0.0,
           "competitivePositioningScore": 0.0,
           "growthPotentialScore": 0.0,
           "scalabilityScore": 0.0,
           "expectedROI": {
               "bestCase": 0.0,
               "expectedCase": 0.0,
               "worstCase": 0.0
           },
           "investmentTimeframe": {
               "expectedTimeToExit": 0,
               "expectedExitMultiple": 0.0,
               "potentialExitPaths": []
           },
           "fundingRequirements": {
               "currentRound": 0.0,
               "nextRound": 0.0,
               "pathToProfitability": ""
           },
           "keyMetricsToTrack": []
       }
      
       riskAssessment = {
           "marketRisks": {},
           "competitiveRisks": {},
           "executionRisks": {},
           "financialRisks": {},
           "regulatoryRisks": {},
           "technologyRisks": {},
           "teamRisks": {},
           "overallRiskProfile": 0.0,
           "riskMitigationStrategies": []
       }
      
       strategicImplications = {
           "competitiveStrategy": {
               "recommendations": [],
               "differentiationOpportunities": [],
               "potentialAlliances": []
           },
           "goToMarketStrategy": {
               "recommendations": [],
               "channelStrategy": [],
               "pricingStrategy": []
           },
           "productStrategy": {
               "recommendations": [],
               "featureRoadmap": [],
               "innovationOpportunities": []
           },
           "geographicExpansion": {
               "recommendations": [],
               "prioritizedMarkets": [],
               "entryStrategies": []
           }
       }
      
       recommendations = {
           "investmentDecision": "",
           "valuationGuidance": "",
           "termSheetNotes": [],
           "nextStepsForDueDiligence": [],
           "shortTermRecommendations": [],
           "mediumTermRecommendations": [],
           "longTermRecommendations": [],
           "keySuccessFactors": [],
           "valueCreationOpportunities": []
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
               "confidenceScore": 0.0,
               "dataSources": [],
               "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               "dataGaps": []
           }
       }
      
       return marketReport
  
   def fillMissingInformation(self, marketReport: Dict[str, Any], startupInfo: Dict[str, Any]) -> None:
       """
       Fill missing information in the market report using OpenAI.
      
       Args:
           marketReport: Market report dictionary to update
           startupInfo: Startup information
       """
       sector = startupInfo.get("sector", "")
       companyName = startupInfo.get("name", "")
       productType = startupInfo.get("productType", "")
      
       # Fill market size information if missing
       if marketReport["marketMetrics"]["marketSize"]["tam"] == 0.0:
           marketSizeInfo = self.getMarketSizeFromOpenAI(sector, companyName, productType)
          
           marketReport["marketMetrics"]["marketSize"]["tam"] = marketSizeInfo.get("tam", 0.0)
           marketReport["marketMetrics"]["marketSize"]["tamGrowthRate"] = marketSizeInfo.get("growthRate", 0.0)
           marketReport["marketMetrics"]["marketSize"]["sam"] = marketSizeInfo.get("sam", 0.0)
           marketReport["marketMetrics"]["marketSize"]["som"] = marketSizeInfo.get("som", 0.0)
          
           self.references.append({
               "section": "Market Size",
               "source": "OpenAI o3mini",
               "query": f"Market size for {sector} sector: {companyName}",
               "urls": marketSizeInfo.get("sources", [])
           })
      
       # Fill market forces if missing
       if not marketReport["marketMetrics"]["marketForces"]["drivers"]:
           forcesInfo = self.getMarketForcesFromOpenAI(sector, companyName, productType)
          
           marketReport["marketMetrics"]["marketForces"]["drivers"] = forcesInfo.get("drivers", [])
           marketReport["marketMetrics"]["marketForces"]["challenges"] = forcesInfo.get("challenges", [])
           marketReport["marketMetrics"]["marketForces"]["enablers"] = forcesInfo.get("enablers", [])
           marketReport["marketMetrics"]["marketForces"]["disruptors"] = forcesInfo.get("disruptors", [])
          
           self.references.append({
               "section": "Market Forces",
               "source": "OpenAI o3mini",
               "query": f"Market forces for {sector} sector: {companyName}",
               "urls": forcesInfo.get("sources", [])
           })
      
       # Fill market trends if missing
       if not marketReport["trends"]["currentTrends"]:
           trendsInfo = self.getMarketTrendsFromOpenAI(sector, companyName, productType)
          
           marketReport["trends"]["currentTrends"] = trendsInfo.get("currentTrends", [])
           marketReport["trends"]["futurePredictions"] = trendsInfo.get("futurePredictions", [])
           marketReport["trends"]["technologyAdvancements"] = trendsInfo.get("technologyAdvancements", [])
           marketReport["trends"]["consumerBehaviorChanges"] = trendsInfo.get("consumerBehaviorChanges", [])
          
           self.references.append({
               "section": "Market Trends",
               "source": "OpenAI o3mini",
               "query": f"Market trends for {sector} sector: {companyName}",
               "urls": trendsInfo.get("sources", [])
           })
      
       # Fill competitors information if missing details
       for competitor in marketReport["competitors"]:
           if not competitor["strategy"]["strengths"]:
               compInfo = self.getCompetitorInfoFromOpenAI(competitor["name"], sector)
              
               competitor["overview"]["description"] = compInfo.get("description", "")
               competitor["overview"]["founded"] = compInfo.get("foundedYear", 0)
               competitor["financials"]["fundingStage"] = compInfo.get("fundingStage", "")
               competitor["financials"]["totalFunding"] = compInfo.get("totalFunding", 0.0)
               competitor["market"]["marketShare"] = compInfo.get("marketShare", 0.0)
               competitor["strategy"]["strengths"] = compInfo.get("strengths", [])
               competitor["strategy"]["weaknesses"] = compInfo.get("weaknesses", [])
               competitor["strategy"]["keyDifferentiators"] = compInfo.get("keyDifferentiators", [])
               competitor["product"]["pricingStrategy"] = compInfo.get("pricingStrategy", "")
              
               self.references.append({
                   "section": f"Competitor: {competitor['name']}",
                   "source": "OpenAI o3mini",
                   "query": f"Information about {competitor['name']} in {sector} sector",
                   "urls": compInfo.get("sources", [])
               })
  
   def calculateScores(self, marketReport: Dict[str, Any], startupInfo: Dict[str, Any]) -> None:
       """
       Calculate scores and metrics based on the available information.
      
       Args:
           marketReport: Market report to update
           startupInfo: Startup information
       """
       # Market attractiveness score based on market size, growth rate, and maturity
       tamScore = min(1.0, marketReport["marketMetrics"]["marketSize"]["tam"] / 100.0)
       growthScore = min(1.0, marketReport["marketMetrics"]["marketSize"]["tamGrowthRate"] / 30.0)
      
       # Maturity score - emerging and growing markets are more attractive
       maturityStage = marketReport["marketMetrics"]["marketDynamics"]["maturityStage"]
       maturityScore = 0.9 if maturityStage == "EMERGING" else 0.8 if maturityStage == "GROWING" else 0.5 if maturityStage == "MATURE" else 0.3
      
       # Competition score - lower concentration is better
       concentrationScore = 1.0 - min(1.0, marketReport["marketMetrics"]["marketDynamics"].get("marketConcentration", 0.5) / 100.0)
      
       # Calculate market attractiveness (weighted average)
       marketAttractivenessScore = (tamScore * 0.3) + (growthScore * 0.3) + (maturityScore * 0.2) + (concentrationScore * 0.2)
       marketReport["investmentMetrics"]["marketAttractivenessScore"] = marketAttractivenessScore
      
       # Investment timing score based on market trends and adoption curve
       adoptionCurve = marketReport["trends"]["technologyAdoption"].get("adoptionCurve", "")
       adoptionScore = 0.9 if adoptionCurve == "Early Adoption" else 0.7 if adoptionCurve == "Early Majority" else 0.5 if adoptionCurve == "Late Majority" else 0.3
      
       # Calculate investment timing score
       investmentTimingScore = adoptionScore
       marketReport["investmentMetrics"]["investmentTimingScore"] = investmentTimingScore
      
       # Overall market opportunity score
       marketOpportunityScore = (marketAttractivenessScore * 0.6) + (investmentTimingScore * 0.4)
       marketReport["investmentMetrics"]["marketOpportunityScore"] = marketOpportunityScore
      
       # Generate recommendations based on scores
       recommendations = []
      
       if marketAttractivenessScore > 0.7:
           recommendations.append("The market is highly attractive with significant growth potential")
       elif marketAttractivenessScore > 0.5:
           recommendations.append("The market shows moderate attractiveness with reasonable growth potential")
       else:
           recommendations.append("The market has limited attractiveness, requiring careful investment consideration")
          
       if investmentTimingScore > 0.7:
           recommendations.append("Current timing is optimal for market entry or expansion")
       elif investmentTimingScore > 0.5:
           recommendations.append("Market timing is adequate, but not optimal")
       else:
           recommendations.append("Consider delaying investment until market conditions improve")
          
       if marketOpportunityScore > 0.7:
           recommendations.append("Strong overall market opportunity suggests aggressive investment strategy")
           marketReport["recommendations"]["investmentDecision"] = "Pursue aggressively"
       elif marketOpportunityScore > 0.5:
           recommendations.append("Moderate market opportunity suggests measured investment approach")
           marketReport["recommendations"]["investmentDecision"] = "Pursue with caution"
       else:
           recommendations.append("Limited market opportunity requires a highly selective approach")
           marketReport["recommendations"]["investmentDecision"] = "Further research needed"
          
       marketReport["recommendations"]["shortTermRecommendations"] = recommendations
  
   def getMarketSizeFromOpenAI(self, sector, company, productType):
       """
       Use OpenAI to get market size information.
      
       Args:
           sector: Company sector
           company: Company name
           productType: Type of product
          
       Returns:
           Dict with market size information
       """
       model = self.get_4o_mini_model(temperature=0.7)
      
       prompt = f"""
       I need market size information for a company called {company} in the {sector} sector offering {productType}.
      
       Please provide:
       1. Total Addressable Market (TAM) in billions USD
       2. Serviceable Addressable Market (SAM) in billions USD
       3. Serviceable Obtainable Market (SOM) in billions USD
       4. Market growth rate (CAGR %)
       5. Sources (URLs) for this information
      
       Format your answer as JSON only, like:
       {{
           "tam": 50.0,
           "sam": 15.0,
           "som": 2.5,
           "growthRate": 12.5,
           "sources": ["https://example.com/market-report", "https://example2.com/industry-analysis"]
       }}
       """
      
       result = model(prompt)
       try:
           return json.loads(result)
       except:
           # Fallback values if parsing fails
           return {"tam": 10.0, "sam": 3.0, "som": 0.5, "growthRate": 8.0, "sources": []}
  
   def getMarketForcesFromOpenAI(self, sector, company, productType):
       """
       Use OpenAI to get market forces information.
      
       Args:
           sector: Company sector
           company: Company name
           productType: Type of product
          
       Returns:
           Dict with market forces information
       """
       model = self.get_4o_mini_model(temperature=0.7)
      
       prompt = f"""
       Please analyze the market forces for a company called {company} in the {sector} sector offering {productType}.
      
       Provide the following:
       1. Top 5 market drivers (factors pushing growth)
       2. Top 5 market challenges (barriers to growth)
       3. Top 3 market enablers (factors facilitating adoption)
       4. Top 3 market disruptors (factors changing the industry)
       5. Sources (URLs) for this information
      
       Format your answer as JSON only, like:
       {{
           "drivers": ["Driver 1", "Driver 2", "Driver 3", "Driver 4", "Driver 5"],
           "challenges": ["Challenge 1", "Challenge 2", "Challenge 3", "Challenge 4", "Challenge 5"],
           "enablers": ["Enabler 1", "Enabler 2", "Enabler 3"],
           "disruptors": ["Disruptor 1", "Disruptor 2", "Disruptor 3"],
           "sources": ["https://example.com/market-report", "https://example2.com/industry-analysis"]
       }}
       """
      
       result = model(prompt)
       try:
           return json.loads(result)
       except:
           # Fallback values if parsing fails
           return {
               "drivers": ["Increasing demand", "Technology adoption"],
               "challenges": ["Market competition", "Regulatory hurdles"],
               "enablers": ["Technology advancements", "Investment in sector"],
               "disruptors": ["Emerging technologies", "Changing consumer preferences"],
               "sources": []
           }
  
   def getMarketTrendsFromOpenAI(self, sector, company, productType):
       """
       Use OpenAI to get market trends information.
      
       Args:
           sector: Company sector
           company: Company name
           productType: Type of product
          
       Returns:
           Dict with market trends information
       """
       model = self.get_4o_mini_model(temperature=0.7)
      
       prompt = f"""
       Please analyze the market trends for a company called {company} in the {sector} sector offering {productType}.
      
       Provide the following:
       1. Top 5 current trends in the market
       2. Top 5 future predictions for the next 3-5 years
       3. Top 3 technology advancements affecting the market
       4. Top 3 consumer behavior changes relevant to this market
       5. Sources (URLs) for this information
      
       Format your answer as JSON only, like:
       {{
           "currentTrends": ["Trend 1", "Trend 2", "Trend 3", "Trend 4", "Trend 5"],
           "futurePredictions": ["Prediction 1", "Prediction 2", "Prediction 3", "Prediction 4", "Prediction 5"],
           "technologyAdvancements": ["Tech 1", "Tech 2", "Tech 3"],
           "consumerBehaviorChanges": ["Change 1", "Change 2", "Change 3"],
           "sources": ["https://example.com/market-trends", "https://example2.com/industry-forecast"]
       }}
       """
      
       result = model(prompt)
       try:
           return json.loads(result)
       except:
           # Fallback values if parsing fails
           return {
               "currentTrends": ["Digital transformation", "Increasing demand"],
               "futurePredictions": ["Market consolidation", "Technology integration"],
               "technologyAdvancements": ["AI integration", "Cloud adoption"],
               "consumerBehaviorChanges": ["Preference for digital solutions", "Demand for personalization"],
               "sources": []
           }
  
   def getCompetitorInfoFromOpenAI(self, competitorName, sector):
       """
       Use OpenAI to get competitor information.
      
       Args:
           competitorName: Competitor name
           sector: Industry sector
          
       Returns:
           Dict with competitor information
       """
       model = self.get_4o_mini_model(temperature=0.7)
      
       prompt = f"""
       Please provide competitive analysis information for {competitorName} in the {sector} sector.
      
       Include:
       1. Brief company description (2 sentences)
       2. Year founded (just the year as an integer)
       3. Funding stage (e.g., "Seed", "Series A", "Public")
       4. Estimated total funding in millions USD (as a number)
       5. Estimated market share percentage (as a number between 0 and 100)
       6. Top 3 strengths
       7. Top 3 weaknesses
       8. Top 3 key differentiators
       9. Pricing strategy (brief description)
       10. Sources (URLs) for this information
      
       Format your answer as JSON only, like:
       {{
           "description": "Company description here",
           "foundedYear": 2015,
           "fundingStage": "Series B",
           "totalFunding": 25.5,
           "marketShare": 5.3,
           "strengths": ["Strength 1", "Strength 2", "Strength 3"],
           "weaknesses": ["Weakness 1", "Weakness 2", "Weakness 3"],
           "keyDifferentiators": ["Differentiator 1", "Differentiator 2", "Differentiator 3"],
           "pricingStrategy": "Freemium with enterprise tiers",
           "sources": ["https://example.com/competitor-profile", "https://example2.com/funding-data"]
       }}
       """
      
       result = model(prompt)
       try:
           return json.loads(result)
       except:
           # Fallback values if parsing fails
           return {
               "description": f"{competitorName} is a company in the {sector} sector.",
               "foundedYear": 2018,
               "fundingStage": "Series A",
               "totalFunding": 10.0,
               "marketShare": 2.0,
               "strengths": ["Market experience", "Product quality", "Strong team"],
               "weaknesses": ["Limited market reach", "Funding constraints", "Feature gaps"],
               "keyDifferentiators": ["Unique technology", "Customer service", "Integration capabilities"],
               "pricingStrategy": "Subscription-based",
               "sources": []
           }
  
   def createEmptyMarketReport(self) -> Dict[str, Any]:
       """Create an empty market report for error scenarios."""
       return {
           "marketMetrics": {
               "marketSize": {"tam": 0.0, "sam": 0.0, "som": 0.0},
               "marketDynamics": {"maturityStage": "EMERGING", "marketSegments": []},
               "marketForces": {"drivers": ["Error in market analysis"], "challenges": ["Data unavailable"]},
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
           "riskAssessment": {
               "marketRisks": {"data_unavailable": 1.0},
               "competitiveRisks": {},
               "executionRisks": {},
               "financialRisks": {},
               "regulatoryRisks": {},
               "technologyRisks": {},
               "teamRisks": {},
               "overallRiskProfile": 0.5
           },
           "strategicImplications": {
               "competitiveStrategy": {"recommendations": []},
               "goToMarketStrategy": {"recommendations": []},
               "productStrategy": {"recommendations": []},
               "geographicExpansion": {"recommendations": []}
           },
           "recommendations": {
               "investmentDecision": "Insufficient data for decision",
               "valuationGuidance": "",
               "termSheetNotes": [],
               "nextStepsForDueDiligence": ["Gather more market data"],
               "shortTermRecommendations": [],
               "mediumTermRecommendations": [],
               "longTermRecommendations": []
           },
           "dataQuality": {
               "confidenceScore": 0.0,
               "dataSources": [],
               "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               "dataGaps": ["Market data missing"]
           },
           "references": []
       }


def analyzeMarket(input_source: Any, input_type: str = "json_data") -> Dict[str, Any]:
   """
   Main entry point for market analysis.
  
   Args:
       input_source: Source data for analysis - can be JSON data, URL, or file path
       input_type: Type of input source - "json_data" (default), "url", "json_file", or "text_file"
      
   Returns:
       Dict containing the market analysis results
   """
   shared = {}
   screeningData = {}
  
   # Process different input types
   if input_type == "json_data":
       # Direct JSON data input (default)
       screeningData = input_source
   elif input_type == "url":
       # URL input - scrape and extract information
       try:
           print(f"Scraping URL: {input_source}...")
           marketAnalysisNode = MarketAnalysisNode()
           title, content = marketAnalysisNode.scrape(input_source)
          
           # Check if scraping failed
           if content == "" or title.startswith("Error scraping"):
               print(f"Warning: {title}")
               # Fallback to treating the URL as a company name
               company_name = input_source.split("/")[-1].replace("-", " ").title() or "Unknown"
               screeningData = {
                   "name": company_name,
                   "sector": "Technology",
                   "competitorNames": [],
                   "productType": "Software",
                   "dataSources": [{"type": "url", "source": input_source, "status": "failed"}]
               }
           else:
               # Extract basic information from content
               screeningData = extractDataFromText(content, title)
              
               # Add reference for the URL source
               screeningData["dataSources"] = [{"type": "url", "source": input_source, "status": "success"}]
       except Exception as e:
           print(f"Error processing URL: {e}")
           # Extract company name from URL as fallback
           company_name = input_source.split("/")[-1].replace("-", " ").title() or "Unknown"
           screeningData = {
               "name": company_name,
               "sector": "Technology",
               "competitorNames": [],
               "dataSources": [{"type": "url", "source": input_source, "status": "error"}]
           }
   elif input_type == "json_file":
       # JSON file input
       try:
           with open(input_source, 'r') as file:
               screeningData = json.load(file)
       except Exception as e:
           print(f"Error reading JSON file: {e}")
           screeningData = {"name": "Unknown", "sector": "Technology"}
   elif input_type == "text_file":
       # Text file input
       try:
           with open(input_source, 'r') as file:
               content = file.read()
              
           # Extract filename as potential company name
           filename = os.path.basename(input_source)
           company_name = os.path.splitext(filename)[0].replace("_", " ").title()
              
           # Extract basic information from text
           screeningData = extractDataFromText(content, company_name)
          
           # Add reference for the file source
           screeningData["dataSources"] = [{"type": "file", "source": input_source}]
       except Exception as e:
           print(f"Error reading text file: {e}")
           screeningData = {"name": "Unknown", "sector": "Technology"}
   else:
       raise ValueError(f"Unsupported input_type: {input_type}. Use 'json_data', 'url', 'json_file', or 'text_file'.")
  
   # Set up shared store with screening data
   shared["screening_data"] = screeningData
  
   # Create and run the analysis flow
   try:
       print("Starting market analysis...")
       marketAnalysisNode = MarketAnalysisNode()
       flow = Flow(start=marketAnalysisNode)
      
       flow.run(shared)
      
       market_analysis = shared.get("market_analysis", {})
       if not market_analysis:
           print("Warning: Market analysis returned empty results")
           # Create fallback empty report
           market_analysis = marketAnalysisNode.createEmptyMarketReport()
           market_analysis["dataQuality"]["dataGaps"].append("Market analysis failed to produce results")
          
       return market_analysis
   except Exception as e:
       print(f"Error during market analysis: {e}")
       # Create fallback empty report
       marketAnalysisNode = MarketAnalysisNode()
       empty_report = marketAnalysisNode.createEmptyMarketReport()
       empty_report["dataQuality"]["dataGaps"].append(f"Error during analysis: {str(e)}")
       return empty_report


def extractDataFromText(content: str, title: str = "Unknown") -> Dict[str, Any]:
   """
   Extract company information from text content.
  
   Args:
       content: Text content to analyze
       title: Title or company name
      
   Returns:
       Dict with extracted company information
   """
   # Basic extraction logic - this could be improved with LLM assistance
   screeningData = {
       "name": title,
       "sector": "Unknown",
       "productType": "Unknown",
       "targetMarket": "Unknown",
       "businessModel": "Unknown",
       "geographicFocus": ["Global"],
       "competitorNames": []
   }
  
   # Look for sector information
   sectors = [
       "AI", "SaaS", "Fintech", "Healthcare", "Biotech", "Edtech",
       "E-commerce", "Cybersecurity", "Clean Energy", "Robotics"
   ]
  
   for sector in sectors:
       if sector.lower() in content.lower():
           screeningData["sector"] = sector
           break
  
   # Try to extract competitor names (basic approach)
   competitor_indicators = [
       "competitor", "competitors", "competing with", "similar to",
       "alternative to", "rivals", "competition"
   ]
  
   for indicator in competitor_indicators:
       if indicator in content.lower():
           # Get the sentence containing the indicator
           sentences = content.split(".")
           for sentence in sentences:
               if indicator in sentence.lower():
                   # Extract potential company names (basic heuristic)
                   words = sentence.split()
                   for i, word in enumerate(words):
                       if word[0].isupper() and i > 0 and words[i-1].lower() != "the":
                           if len(word) > 2 and word not in screeningData["competitorNames"]:
                               screeningData["competitorNames"].append(word)
  
   # Limit to 5 competitors to avoid noise
   screeningData["competitorNames"] = screeningData["competitorNames"][:5]
  
   return screeningData


def generate_comprehensive_report(company_data):
   """Generate a comprehensive market analysis report"""
   now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  
   # Determine which data is from URL vs AI
   url_source_count = sum(1 for section in company_data if section != "ai_references" and company_data[section])
   ai_source_count = len(company_data.get("ai_references", []))
   total_data_points = url_source_count + ai_source_count
  
   url_percentage = int((url_source_count / total_data_points) * 100) if total_data_points > 0 else 0
   ai_percentage = 100 - url_percentage
  
   report = f"""# Comprehensive Market Analysis: {company_data.get('name', 'Unknown')}


*Generated on: {now}*


## Executive Summary


**Company:** {company_data.get('name', 'Unknown')}
**Founded:** {company_data.get('founded', 'Unknown')}
**Headquarters:** {company_data.get('location', 'Unknown')}
**Industry:** {company_data.get('industry', 'Unknown')}
**Product:** {company_data.get('product_info', {}).get('summary', 'Unknown')}


{company_data.get('description', 'No description available.')}


## Market Analysis


### Market Size & Growth
- **Total Addressable Market (TAM):** ${company_data.get('market', {}).get('tam', 'Unknown')}B
- **Serviceable Addressable Market (SAM):** ${company_data.get('market', {}).get('sam', 'Unknown')}B
- **Serviceable Obtainable Market (SOM):** ${company_data.get('market', {}).get('som', 'Unknown')}B
- **Market CAGR:** {company_data.get('market', {}).get('cagr', 'Unknown')}%
- **Market Maturity:** {company_data.get('market', {}).get('maturity_stage', 'Unknown')}


### Market Drivers
{format_list(company_data.get('market', {}).get('drivers', []))}


### Market Challenges
{format_list(company_data.get('market', {}).get('challenges', []))}


## Competitive Landscape


### Direct Competitors
{format_competitors(company_data.get('competition', {}).get('direct_competitors', []))}


### Indirect Competitors
{format_competitors(company_data.get('competition', {}).get('indirect_competitors', []))}


### Competitive Advantage
{company_data.get('competition', {}).get('competitive_advantage', 'No data available.')}


## Business Model


**Revenue Model:** {company_data.get('business_model', {}).get('revenue_model', 'Unknown')}
**Pricing Strategy:** {company_data.get('business_model', {}).get('pricing_strategy', 'Unknown')}
**Target Customers:** {company_data.get('business_model', {}).get('target_customers', 'Unknown')}
**CAC:** ${company_data.get('business_model', {}).get('cac', 'Unknown')}
**LTV:** ${company_data.get('business_model', {}).get('ltv', 'Unknown')}
**Sales Cycle:** {company_data.get('business_model', {}).get('sales_cycle', 'Unknown')}


## Market Trends


### Current Trends
{format_list(company_data.get('trends', {}).get('current_trends', []))}


### Future Predictions
{format_list(company_data.get('trends', {}).get('future_predictions', []))}


### Technology Impact
{format_list(company_data.get('trends', {}).get('technology_impact', []))}


## Risk Assessment


### Market Risks
{format_list(company_data.get('risks', {}).get('market_risks', []))}


### Competitive Risks
{format_list(company_data.get('risks', {}).get('competitive_risks', []))}


### Execution Risks
{format_list(company_data.get('risks', {}).get('execution_risks', []))}


## Investment Analysis


**Funding to Date:** ${company_data.get('investment', {}).get('funding_to_date', 'Unknown')}M
**Current Valuation:** ${company_data.get('investment', {}).get('valuation', 'Unknown')}M
**Key Investors:** {', '.join(company_data.get('investment', {}).get('investors', ['Unknown']))}
**Expected ROI:** {company_data.get('investment', {}).get('expected_roi', 'Unknown')}x


## Recommendations


{format_list(company_data.get('recommendations', []))}


## Data Sources


**URL Data:** Approximately {url_percentage}% of this report was extracted directly from {company_data.get('source_url', 'the provided URL')}.
**AI-Generated Data:** Approximately {ai_percentage}% of this report was generated using AI to fill gaps in available information.


### AI-Generated Sections
{format_ai_references(company_data.get('ai_references', []))}


---


*This report was generated using both website data extraction and AI-enhanced analysis. All AI-generated content is marked accordingly.*
"""
   return report


if __name__ == "__main__":
   import argparse
  
   parser = argparse.ArgumentParser(
       description="Market Analysis Agent - Analyze market data for startups",
       epilog="""Examples:
       # Analyze using JSON data
       python Market_analysis_agent.py --input '{"name":"AI Startup", "sector":"AI"}'
      
       # Analyze a website
       python Market_analysis_agent.py --input "https://example.com/company-page"
      
       # Analyze a JSON file
       python Market_analysis_agent.py --input data/company_info.json
      
       # Analyze a text description
       python Market_analysis_agent.py --input data/company_description.txt
      
       # Run in interactive mode (no arguments)
       python Market_analysis_agent.py
       """,
       formatter_class=argparse.RawDescriptionHelpFormatter
   )
   parser.add_argument("--input", help="Input source (JSON data, URL, or file path)")
   parser.add_argument("--output", help="Output file path for report")
  
   args = parser.parse_args()
  
   # Interactive mode if no input argument is provided
   if args.input is None:
       print("=== Market Analysis Agent ===")
       input_source = input("Enter a URL, file path, or JSON data: ")
       output_path = input("Output file path (leave empty for no file output): ")
      
       if output_path.strip():
           args.output = output_path
          
       # Use the input from the prompt
       args.input = input_source
  
   # Auto-detect input type
   input_type = "json_data"  # Default
   input_source = args.input
  
   # Check if input is a URL
   if input_source.startswith(('http://', 'https://')):
       input_type = "url"
   # Check if input is a file path
   elif os.path.exists(input_source):
       # Check if it's a JSON file
       if input_source.endswith('.json'):
           input_type = "json_file"
       else:
           input_type = "text_file"
   # Otherwise, assume it's JSON data
   else:
       try:
           # Try to parse as JSON
           json.loads(input_source)
           input_type = "json_data"
       except json.JSONDecodeError:
           # If not valid JSON, treat it as a company name for simple analysis
           input_source = {
               "name": input_source,
               "sector": "Technology",
               "competitorNames": []
           }
           input_type = "json_data"
  
   print(f"Processing input as {input_type}...")
  
   # Process different input types
   if input_type == "json_data" and not isinstance(input_source, dict):
       try:
           input_data = json.loads(input_source)
       except json.JSONDecodeError:
           # This should have been caught above, but just in case
           input_data = {
               "name": input_source,
               "sector": "Technology",
               "competitorNames": []
           }
   else:
       input_data = input_source
  
   # Run analysis with appropriate input type
   marketReport = analyzeMarket(input_data, input_type)
  
   # Print summary
   print("\nMarket Analysis Report Summary:")
   print(f"TAM: ${marketReport['marketMetrics']['marketSize']['tam']}B")
   print(f"Market Attractiveness Score: {marketReport['investmentMetrics']['marketAttractivenessScore']:.2f}")
   print(f"Investment Timing Score: {marketReport['investmentMetrics']['investmentTimingScore']:.2f}")
   print(f"Number of Competitors: {len(marketReport.get('competitors', []))}")
   print(f"Investment Decision: {marketReport['recommendations'].get('investmentDecision', 'N/A')}")
  
   # Save report if output path specified
   if args.output:
       startupInfo = {
           "name": marketReport.get("name", input_data.get("name", "Unknown") if isinstance(input_data, dict) else "Unknown"),
           "sector": marketReport.get("sector", input_data.get("sector", "Technology") if isinstance(input_data, dict) else "Technology"),
           "productType": marketReport.get("productType", input_data.get("productType", "Software") if isinstance(input_data, dict) else "Software"),
           "targetMarket": marketReport.get("targetMarket", input_data.get("targetMarket", "Enterprise") if isinstance(input_data, dict) else "Enterprise"),
           "businessModel": marketReport.get("businessModel", input_data.get("businessModel", "SaaS") if isinstance(input_data, dict) else "SaaS"),
           "geographicFocus": marketReport.get("geographicFocus", input_data.get("geographicFocus", ["Global"]) if isinstance(input_data, dict) else ["Global"])
       }
      
       # Create MarketReport object for report generation
       reportGenerator = MarketReport(
           marketMetrics=MarketMetrics(
               tam=marketReport["marketMetrics"]["marketSize"]["tam"],
               sam=marketReport["marketMetrics"]["marketSize"]["sam"],
               som=marketReport["marketMetrics"]["marketSize"]["som"],
               growthRate=marketReport["marketMetrics"]["marketSize"]["tamGrowthRate"],
               marketMaturity=MarketMaturity.EMERGING,  # Default value
               marketSegments=[],  # Simplified for this example
               marketDrivers=marketReport["marketMetrics"]["marketForces"]["drivers"],
               marketChallenges=marketReport["marketMetrics"]["marketForces"]["challenges"],
               regulatoryEnvironment=marketReport["marketMetrics"]["marketAccess"]["regulatoryEnvironment"],
               entryBarriers=marketReport["marketMetrics"]["marketAccess"]["entryBarriers"],
               exitBarriers=marketReport["marketMetrics"]["marketAccess"]["exitBarriers"]
           ),
           competitors=[],  # Simplified for this example
           trends=MarketTrends(
               currentTrends=marketReport["trends"]["currentTrends"],
               futurePredictions=marketReport["trends"]["futurePredictions"],
               technologyAdvancements=marketReport["trends"]["technologyAdvancements"],
               consumerBehaviorChanges=marketReport["trends"]["consumerBehaviorChanges"],
               regulatoryChanges=marketReport["trends"]["regulatoryChanges"],
               investmentTrends=marketReport["trends"]["investmentTrends"],
               industryConsolidation=marketReport["trends"]["industryConsolidation"],
               emergingOpportunities=marketReport["trends"]["emergingOpportunities"]
           ),
           marketAttractivenessScore=marketReport["investmentMetrics"]["marketAttractivenessScore"],
           investmentTimingScore=marketReport["investmentMetrics"]["investmentTimingScore"],
           riskAssessment=marketReport["riskAssessment"].get("marketRisks", {}),
           recommendations=marketReport["recommendations"]["shortTermRecommendations"],
           references=marketReport.get("references", [])
       )
      
       # Save report
       report_path = reportGenerator.saveMarkdownReport(startupInfo, args.output)
       print(f"Report saved to: {report_path}")