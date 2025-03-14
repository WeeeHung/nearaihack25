"""
Screening Agent for Multi-Agent Due Diligence System

This script implements a screening agent that evaluates startups and private companies
based on predefined criteria. It analyzes company data, founders, tech stack, and investment history.
"""

import json
import random
from typing import Optional, Dict, Any, List
from enum import Enum
import typer
from pydantic import BaseModel, Field
import requests
from dotenv import load_dotenv
from ..base_agent import BaseAgent, AgentContext

# Initialize typer app
app = typer.Typer()

class Industry(str, Enum):
    """Supported industries for startup screening."""
    AI_ML = "AI/ML"
    SAAS = "SaaS"
    FINTECH = "FinTech"
    HEALTHTECH = "HealthTech"
    BIOTECH = "Biotech"
    CLEAN_ENERGY = "Clean Energy"
    BLOCKCHAIN = "Blockchain"
    EDTECH = "EdTech"
    E_COMMERCE = "E-Commerce"
    HARDWARE = "Hardware"
    CONSUMER_APPS = "Consumer Apps"
    ENTERPRISE = "Enterprise Software"
    LOGISTICS = "Logistics/Supply Chain"
    PROPTECH = "PropTech"
    GAMING = "Gaming"
    FOOD_AGRICULTURE = "Food/Agriculture"
    CYBERSECURITY = "Cybersecurity"
    AR_VR = "AR/VR"
    ROBOTICS = "Robotics"
    MARKETPLACE = "Marketplace"
    OTHER = "Other"

class ScreeningAgent(BaseAgent):
    """Agent responsible for initial startup screening and analysis."""
    
    def __init__(self, context: Optional[AgentContext] = None):
        super().__init__("screening", context)
        self.criteria = {
            "min_revenue": 0.0,  # Startups may have no revenue
            "min_growth_rate": 20.0,
            "min_team_size": 2,
            "target_industries": [
                "AI/ML", "SaaS", "FinTech", "HealthTech", "Biotech"
            ],
            "required_roles": ["CEO", "CTO"],
            "min_funding": 0.0,  # In millions USD
            "max_age": 10,  # Years since founding
            "tech_stack_focus": ["Cloud", "AI", "Blockchain", "Mobile"]
        }
    
    def execute(self, company_name: str) -> Dict[str, Any]:
        """
        Screen a startup or private company based on defined criteria.
        
        Args:
            company_name: Company name to analyze
            
        Returns:
            Complete analysis of the startup
        """
        try:
            # Update context with company name
            self.update_context(company_name=company_name)
            
            # Fetch company data from Crunchbase or similar source
            company_data = self._fetch_company_data(company_name)
            
            # Analyze the company against our criteria
            analysis_result = self._analyze_company(company_data)
            
            # Save the analysis result and confidence score
            self.save_analysis_result(
                analysis_result,
                analysis_result.get("confidence_score", 0.8)
            )
            
            # Save additional state
            self.save_state({
                "last_screened": company_name,
                "screening_criteria": self.criteria,
                "qualified": analysis_result.get("qualified", False)
            })
            
            return analysis_result
            
        except Exception as e:
            raise RuntimeError(f"Failed to screen company {company_name}: {str(e)}")
    
    def _fetch_company_data(self, company_name: str) -> Dict[str, Any]:
        """
        Fetch company data from Crunchbase or similar sources.
        
        In a production environment, this would use actual API calls.
        For development, it uses realistic mock data.
        
        Args:
            company_name: Name of the company to fetch data for
            
        Returns:
            Structured company data including financials, team, tech stack, etc.
        """
        try:
            # In production, uncomment and use actual API calls:
            # return self._call_crunchbase_api(company_name)
            
            # For development, generate realistic mock data
            return self._generate_mock_data(company_name)
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data for {company_name}: {str(e)}")
    
    def _call_crunchbase_api(self, company_name: str) -> Dict[str, Any]:
        """
        Make actual API calls to Crunchbase.
        
        Args:
            company_name: Company name to search for
            
        Returns:
            Company data from Crunchbase
        """
        # This would be implemented with actual API keys and endpoints
        api_key = os.getenv("CRUNCHBASE_API_KEY")
        if not api_key:
            raise ValueError("CRUNCHBASE_API_KEY not set in environment variables")
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Make the API request
        response = requests.get(
            f"https://api.crunchbase.com/api/v4/entities/organizations/{company_name}",
            headers=headers
        )
        response.raise_for_status()
        
        # Process and structure the response
        data = response.json()
        return self._structure_crunchbase_data(data)
    
    def _structure_crunchbase_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure and normalize raw Crunchbase data."""
        # This would extract and structure the relevant fields from the API response
        return {
            "name": raw_data.get("properties", {}).get("name", ""),
            "description": raw_data.get("properties", {}).get("short_description", ""),
            "founded_date": raw_data.get("properties", {}).get("founded_on", ""),
            # ... more fields would be extracted here
        }
    
    def _generate_mock_data(self, company_name: str) -> Dict[str, Any]:
        """Generate realistic mock data for development purposes."""
        # Set random seed based on company name for consistent results
        random.seed(hash(company_name) % 10000)
        
        # Generate founding date (1-10 years ago)
        founded_years_ago = random.randint(1, 10)
        founding_year = 2023 - founded_years_ago
        
        # Generate mock industry
        industry = random.choice([i.value for i in Industry])
        
        # Generate mock metrics
        revenue = random.uniform(0, 15.0) if random.random() > 0.3 else 0
        growth_rate = random.uniform(10.0, 200.0) if revenue > 0 else 0
        team_size = random.randint(2, 50)
        burn_rate = random.uniform(0.05, 1.0) * team_size  # Monthly burn rate in millions
        
        # Generate funding rounds
        num_rounds = random.randint(0, 4)
        funding_rounds = []
        total_funding = 0
        
        round_types = ["Pre-seed", "Seed", "Series A", "Series B", "Series C"]
        top_vcs = [
            "Sequoia Capital", "Andreessen Horowitz", "Y Combinator", 
            "Accel", "Benchmark", "First Round Capital", "Founders Fund",
            "GV", "Index Ventures", "Kleiner Perkins", "NEA", "Tiger Global"
        ]
        
        for i in range(num_rounds):
            if i < len(round_types):
                round_type = round_types[i]
                amount = random.uniform(0.2, 2.0) * (3 ** i)  # Increasing amounts for later rounds
                total_funding += amount
                
                # Select 1-3 investors for this round
                round_investors = random.sample(top_vcs, random.randint(1, min(3, len(top_vcs))))
                
                funding_rounds.append({
                    "round_type": round_type,
                    "amount": round(amount, 2),
                    "date": f"{2023 - founded_years_ago + i + 1}-{random.randint(1, 12)}-{random.randint(1, 28)}",
                    "investors": round_investors,
                    "lead_investor": round_investors[0] if round_investors else None
                })
        
        # Generate mock founders (1-4 founders)
        num_founders = random.randint(1, 4)
        founder_backgrounds = [
            "Previously founded successful startup",
            "Ex-Google engineer",
            "Former product manager at Facebook",
            "PhD in Computer Science",
            "Ex-McKinsey consultant",
            "Former VP at Amazon",
            "Serial entrepreneur",
            "Industry expert with 15+ years experience",
            "MIT/Stanford graduate",
            "Research scientist"
        ]
        
        founders = []
        for i in range(num_founders):
            role = "CEO" if i == 0 else ("CTO" if i == 1 else random.choice(["COO", "CPO", "CFO"]))
            founders.append({
                "name": f"Founder {i+1}",
                "role": role,
                "background": random.choice(founder_backgrounds),
                "experience_years": random.randint(5, 25),
                "education": random.choice(["Stanford", "MIT", "Harvard", "Berkeley", "Other"])
            })
        
        # Generate tech stack
        frameworks = ["React", "Angular", "Vue", "Django", "Flask", "Spring", "Express", "Rails"]
        languages = ["Python", "JavaScript", "TypeScript", "Go", "Rust", "Java", "Ruby", "C#"]
        databases = ["PostgreSQL", "MongoDB", "MySQL", "Redis", "DynamoDB", "Firestore", "Elasticsearch"]
        cloud_providers = ["AWS", "GCP", "Azure", "Digital Ocean", "Heroku"]
        
        tech_stack = {
            "frontend": random.sample(frameworks[:3], random.randint(1, 2)),
            "backend": random.sample(languages, random.randint(1, 3)),
            "database": random.sample(databases, random.randint(1, 2)),
            "infrastructure": random.sample(cloud_providers, random.randint(1, 2))
        }
        
        # Generate architectural patterns
        architectures = ["Microservices", "Monolith", "Serverless", "Event-driven"]
        architecture = random.choice(architectures)
        
        # Generate product stage
        product_stages = ["Concept", "MVP", "Private Beta", "Public Beta", "Growth", "Mature"]
        product_stage = product_stages[min(num_rounds + 1, len(product_stages) - 1)]
        
        # Compile the complete company data
        return {
            "name": company_name,
            "industry": industry,
            "founded_date": f"{founding_year}-{random.randint(1, 12)}-{random.randint(1, 28)}",
            "company_age_years": founded_years_ago,
            "headquarters": random.choice(["San Francisco", "New York", "Boston", "Austin", "Los Angeles"]),
            "description": f"A {industry} startup focused on innovation and growth.",
            "website": f"https://www.{company_name.lower().replace(' ', '')}.com",
            
            # Financial metrics
            "revenue": revenue,
            "growth_rate": growth_rate,
            "burn_rate": burn_rate,
            "runway_months": round(total_funding / burn_rate) if burn_rate > 0 else 0,
            
            # Team information
            "team_size": team_size,
            "founders": founders,
            "has_technical_cofounder": any(f["role"] == "CTO" for f in founders),
            
            # Funding information
            "total_funding": round(total_funding, 2),
            "funding_rounds": funding_rounds,
            "latest_round": funding_rounds[-1] if funding_rounds else None,
            "investors": list({investor for round in funding_rounds for investor in round["investors"]}),
            
            # Product and technology
            "product_stage": product_stage,
            "tech_stack": tech_stack,
            "architecture": architecture,
            "patents": random.randint(0, 5),
            
            # Market information
            "market_size": f"${random.randint(1, 500)}B",
            "target_customers": random.choice(["B2B", "B2C", "B2B2C", "Enterprise"]),
            "competitors": random.randint(2, 20),
            
            # Additional data
            "social_media": {
                "twitter_followers": random.randint(100, 100000),
                "linkedin_followers": random.randint(50, 5000)
            }
        }
    
    def _analyze_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze company data against screening criteria.
        
        Args:
            company_data: Structured company data
            
        Returns:
            Analysis results and recommendation
        """
        criteria_met = []
        criteria_missed = []
        
        # Check revenue criteria
        if company_data.get("revenue", 0) >= self.criteria["min_revenue"]:
            criteria_met.append("Revenue Threshold")
        else:
            criteria_missed.append("Revenue Threshold")
        
        # Check growth rate criteria
        if company_data.get("growth_rate", 0) >= self.criteria["min_growth_rate"]:
            criteria_met.append("Growth Rate")
        else:
            criteria_missed.append("Growth Rate")
        
        # Check team size criteria
        if company_data.get("team_size", 0) >= self.criteria["min_team_size"]:
            criteria_met.append("Team Size")
        else:
            criteria_missed.append("Team Size")
        
        # Check industry criteria
        if company_data.get("industry") in self.criteria["target_industries"]:
            criteria_met.append("Target Industry")
        else:
            criteria_missed.append("Target Industry")
        
        # Check company age criteria
        if company_data.get("company_age_years", 0) <= self.criteria["max_age"]:
            criteria_met.append("Company Age")
        else:
            criteria_missed.append("Company Age")
        
        # Check technical co-founder criteria
        if company_data.get("has_technical_cofounder", False):
            criteria_met.append("Technical Co-founder")
        else:
            criteria_missed.append("Technical Co-founder")
        
        # Check funding criteria
        if company_data.get("total_funding", 0) >= self.criteria["min_funding"]:
            criteria_met.append("Minimum Funding")
        else:
            criteria_missed.append("Minimum Funding")
        
        # Check for tech stack alignment
        tech_stack_match = False
        for tech in self.criteria["tech_stack_focus"]:
            tech_lower = tech.lower()
            if (
                tech_lower in str(company_data.get("tech_stack", {})).lower() or
                tech_lower in str(company_data.get("architecture", "")).lower()
            ):
                tech_stack_match = True
                break
        
        if tech_stack_match:
            criteria_met.append("Tech Stack Alignment")
        else:
            criteria_missed.append("Tech Stack Alignment")
        
        # Calculate score and qualification
        score = len(criteria_met) / (len(criteria_met) + len(criteria_missed))
        qualified = score >= 0.7  # 70% threshold for qualification
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            company_data,
            qualified,
            score
        )
        
        # Calculate confidence score
        # This would be based on data quality in a real system
        confidence_score = random.uniform(0.7, 0.95)
        
        # Compile the analysis result
        return {
            "company_name": company_data["name"],
            "industry": company_data["industry"],
            "qualified": qualified,
            "score": score,
            "criteria_met": criteria_met,
            "criteria_missed": criteria_missed,
            "recommendation": recommendation,
            "confidence_score": confidence_score,
            
            # Include key company data in the result
            "company_profile": {
                "founded_date": company_data.get("founded_date"),
                "team_size": company_data.get("team_size"),
                "total_funding": company_data.get("total_funding"),
                "latest_round": company_data.get("latest_round"),
                "revenue": company_data.get("revenue"),
                "growth_rate": company_data.get("growth_rate"),
                "burn_rate": company_data.get("burn_rate"),
                "runway_months": company_data.get("runway_months")
            },
            
            # Founder analysis
            "founder_analysis": {
                "num_founders": len(company_data.get("founders", [])),
                "has_technical_cofounder": company_data.get("has_technical_cofounder", False),
                "founder_backgrounds": [f["background"] for f in company_data.get("founders", [])],
                "founder_experience": sum(f.get("experience_years", 0) for f in company_data.get("founders", [])) / 
                                     max(len(company_data.get("founders", [])), 1)
            },
            
            # Tech analysis
            "tech_analysis": {
                "tech_stack": company_data.get("tech_stack"),
                "architecture": company_data.get("architecture"),
                "patents": company_data.get("patents"),
                "tech_score": 0.7 + (0.3 * random.random())  # Mock score
            },
            
            # Investor analysis
            "investor_analysis": {
                "total_funding": company_data.get("total_funding"),
                "num_rounds": len(company_data.get("funding_rounds", [])),
                "investors": company_data.get("investors", []),
                "has_tier_1_vc": any(vc in company_data.get("investors", []) for vc in 
                                   ["Sequoia Capital", "Andreessen Horowitz", "Y Combinator", "Accel"])
            }
        }
    
    def _generate_recommendation(
        self,
        company_data: Dict[str, Any],
        qualified: bool,
        score: float
    ) -> str:
        """Generate a detailed recommendation based on analysis results."""
        company_name = company_data["name"]
        
        if qualified and score >= 0.8:
            return f"Strongly recommend proceeding with due diligence for {company_name}. The startup shows excellent potential with strong founders, promising tech, and good market positioning."
        
        elif qualified and score >= 0.7:
            return f"Recommend proceeding with due diligence for {company_name}, but note some areas need deeper investigation. The company has potential but specific aspects require further validation."
        
        elif score >= 0.6:
            return f"Cautiously proceed with preliminary due diligence for {company_name}. Several areas require thorough investigation before committing significant resources."
        
        else:
            return f"Do not recommend proceeding with due diligence for {company_name} at this time. The startup does not meet key criteria for investment consideration."
    
    def update_criteria(self, new_criteria: Dict[str, Any]) -> None:
        """Update screening criteria."""
        # Update only the provided criteria, keep the rest unchanged
        for key, value in new_criteria.items():
            if key in self.criteria:
                self.criteria[key] = value
        
        # Save the updated criteria in the agent's state
        current_state = self.get_state() or {}
        current_state["screening_criteria"] = self.criteria
        self.save_state(current_state)
        
    def get_tech_analysis(self, company_name: str) -> Dict[str, Any]:
        """Get detailed technology stack analysis for a company."""
        company_data = self._fetch_company_data(company_name)
        return {
            "tech_stack": company_data.get("tech_stack", {}),
            "architecture": company_data.get("architecture", "Unknown"),
            "scalability_score": 0.6 + (0.4 * random.random()),
            "code_quality_estimate": 0.5 + (0.5 * random.random()),
            "technical_debt_estimate": 0.3 + (0.5 * random.random()),
            "patents": company_data.get("patents", 0),
            "tech_team_size": int(company_data.get("team_size", 10) * 0.6),  # Estimate tech team as 60% of total
            "tech_recommendations": [
                "Improve test coverage",
                "Consider microservices architecture",
                "Implement CI/CD pipeline"
            ]
        }
    
    def get_founder_analysis(self, company_name: str) -> Dict[str, Any]:
        """Get detailed founder analysis for a company."""
        company_data = self._fetch_company_data(company_name)
        founders = company_data.get("founders", [])
        
        return {
            "founders": founders,
            "num_founders": len(founders),
            "founder_experience_score": sum(f.get("experience_years", 0) for f in founders) / max(len(founders), 1) / 25,
            "founder_domain_expertise": 0.5 + (0.5 * random.random()),
            "founder_execution_score": 0.4 + (0.6 * random.random()),
            "founder_risk_factors": random.sample([
                "First-time founder",
                "Limited industry experience",
                "No prior exits",
                "Strong technical but weak business background"
            ], random.randint(0, 2)),
            "founder_strengths": random.sample([
                "Strong technical background",
                "Prior successful exit",
                "Domain expertise",
                "Strong network in the industry",
                "Complementary skill sets"
            ], random.randint(1, 3))
        }
    
    def get_investor_analysis(self, company_name: str) -> Dict[str, Any]:
        """Get detailed investor analysis for a company."""
        company_data = self._fetch_company_data(company_name)
        
        return {
            "funding_rounds": company_data.get("funding_rounds", []),
            "total_funding": company_data.get("total_funding", 0),
            "investors": company_data.get("investors", []),
            "lead_investors": [r.get("lead_investor") for r in company_data.get("funding_rounds", []) if r.get("lead_investor")],
            "investor_tier": "Tier 1" if any(vc in company_data.get("investors", []) for vc in 
                                          ["Sequoia Capital", "Andreessen Horowitz", "Y Combinator"]) else "Tier 2",
            "valuation_estimate": company_data.get("total_funding", 1) * random.uniform(3, 10),
            "fundraising_efficiency": 0.4 + (0.6 * random.random()),
            "next_round_estimate": {
                "timing": f"{random.randint(6, 24)} months",
                "amount": f"${round(company_data.get('total_funding', 1) * random.uniform(1.5, 3), 1)}M"
            }
        }

@app.command()
def main(
    company_name: str = typer.Argument(..., help="Startup or private company name"),
    min_revenue: float = typer.Option(0.0, help="Minimum revenue threshold in millions USD"),
    industry: Industry = typer.Option(Industry.AI_ML, help="Target industry for screening"),
    min_funding: float = typer.Option(0.0, help="Minimum funding raised in millions USD"),
    detailed: bool = typer.Option(False, help="Include detailed analysis in output")
):
    """Screen a startup or private company based on specified criteria."""
    try:
        # Initialize context and agent
        context = AgentContext(company_name=company_name)
        agent = ScreeningAgent(context=context)
        
        # Update criteria based on command line options
        agent.update_criteria({
            "min_revenue": min_revenue,
            "target_industries": [industry.value],
            "min_funding": min_funding
        })
        
        # Execute screening
        result = agent.execute(company_name)
        
        # Add detailed analysis if requested
        if detailed:
            result["detailed_tech_analysis"] = agent.get_tech_analysis(company_name)
            result["detailed_founder_analysis"] = agent.get_founder_analysis(company_name)
            result["detailed_investor_analysis"] = agent.get_investor_analysis(company_name)
        
        # Convert the result to a dictionary and print as JSON
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    # Load environment variables if any
    load_dotenv()
    
    # Run the CLI app
    app() 