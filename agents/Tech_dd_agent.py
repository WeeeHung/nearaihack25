import openai
import json
from .base_agent import BaseAgent
from nearai.agents.environment import Environment

class TechDdAgent(BaseAgent):
    def __init__(self, env:Environment, name="TechDdAgent", max_retries=2):
        """Initialize the tech DD agent."""
        super().__init__(env, name)
        self.client = openai.Client(api_key=self.api_keys.get("OPENAI_API_KEY"))
        self.env.add_system_log("TechDdAgent initialized")

    def prep(self, shared):
        """Extract relevant company data from shared store."""
        return {
            "company_info": shared.get("company_info", ""),
            "team_data": shared.get("team_profiles", {})
        }

    def run(self, data):
        """Perform technical due diligence analysis."""
        self.env.add_system_log("Running TechDdAgent")
        print("running tech dd agent")
        print(data)

        # check if company_info is a valid key in data:
        if "company_info" not in data:
            self.env.add_system_log("company_info is not a valid key in data")
            return {}
        
        company_name = self._extract_company_name(data["company_info"]) if data["company_info"] else ""
        
        # Create analysis structure
        tech_dd = {
            "architecture": self._analyze_architecture(data["company_info"]) if data["company_info"] else {},
            "technical_differentiation": self._analyze_differentiation(data["company_info"]) if data["company_info"] else {},
            "team_technical_assessment": self._analyze_team(data["team_data"], data["company_info"]) if data["company_info"] else {},
            "engineering_factors": self._analyze_engineering_factors(data) if data["company_info"] else {},
            "summary": {}
        }
        
        # Generate summary after all sections are complete
        tech_dd["summary"] = self._generate_summary(tech_dd, company_name)
        print("end of tech dd agent")
        return tech_dd

    def _extract_company_name(self, company_info):
        """Extract company name from information."""
        # Simple extraction or use default
        if not company_info:
            return "Unknown Company"
            
        return company_info["company_name"] if "company_name" in company_info else "Unknown Company"

    def _analyze_architecture(self, company_info):
        """Analyze technical architecture."""
        if not company_info:
            return self._empty_architecture()
            
        prompt = f"""
        Based on this company information, analyze their technical architecture.
        If details aren't specified, make educated inferences based on their industry and product:
        
        {company_info}
        
        Return a JSON object with these fields:
        - stack: array of technologies used
        - architecture_type: (monolithic/microservices/serverless/etc)
        - infrastructure: (cloud/on-premise/hybrid)
        - scalability_assessment: text analysis
        - security_assessment: text analysis
        - technical_debt: text analysis
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-search-preview",
                web_search_options={},
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except:
            return self._empty_architecture()

    def _empty_architecture(self):
        """Return empty architecture structure."""
        return {
            "stack": [],
            "architecture_type": "Unknown",
            "infrastructure": "Unknown",
            "scalability_assessment": "No data available",
            "security_assessment": "No data available",
            "technical_debt": "No data available"
        }

    def _analyze_differentiation(self, company_info):
        """Analyze technical differentiation."""
        if not company_info:
            return {"differentiators": []}
            
        prompt = f"""
        Identify technical differentiators for this company:
        {company_info}
        
        Return a JSON object with a single field "differentiators" containing an array of objects with:
        - name: brief name of the differentiator
        - description: explanation
        - advantage_level: (Low/Medium/High)
        - sustainability: assessment of how hard this would be to replicate
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-search-preview",
                web_search_options={},
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except:
            return {"differentiators": []}

    def _analyze_team(self, team_data, company_info):
        """Analyze technical capabilities of the team."""
        if not team_data:
            return self._empty_team_assessment()
            
        prompt = f"""
        Evaluate the technical capabilities of this team:
        {json.dumps(team_data)}
        
        For this company:
        {company_info}
        
        Return a JSON with:
        - technical_expertise_match: (Low/Medium/High)
        - technical_leadership: assessment text
        - key_strengths: array of technical strengths
        - gaps: array of missing technical expertise
        - risk_assessment: text evaluation of technical risk
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except:
            return self._empty_team_assessment()
            
    def _empty_team_assessment(self):
        """Return empty team assessment structure."""
        return {
            "technical_expertise_match": "Unknown",
            "technical_leadership": "No data available",
            "key_strengths": [],
            "gaps": [],
            "risk_assessment": "No data available"
        }

    def _analyze_engineering_factors(self, data):
        """Analyze engineering success factors."""
        company_info = data.get("company_info", "")
        if not company_info:
            return {"factors": []}
            
        prompt = f"""
        Identify key engineering success factors for this company:
        {company_info}
        
        Return a JSON object with a single field "factors" containing an array of objects with:
        - name: name of the factor (e.g., "Development Methodology")
        - assessment: text analysis
        - impact: (Low/Medium/High)
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except:
            return {"factors": []}

    def _generate_summary(self, tech_dd, company_name):
        """Generate summary of technical findings."""
        try:
            summary_prompt = f"""
            Create a concise technical due diligence summary for {company_name} based on:
            {json.dumps(tech_dd)}
            
            Return a JSON with:
            - executive_summary: brief overview text
            - strengths: array of key technical strengths
            - risks: array of key technical risks
            - viability_rating: (Low/Medium/High)
            - recommendations: array of technical improvement suggestions
            """
            
            model = self.get_4o_mini_model()
            response = model(summary_prompt)
            return response
        except:
            return {
                "executive_summary": "Insufficient data for complete analysis",
                "strengths": [],
                "risks": [],
                "viability_rating": "Unknown",
                "recommendations": []
            }

    def post(self, shared, prep_res, exec_res):
        """Save results to shared store."""
        shared["tech_dd_results"] = exec_res
        
        # Save to file
        with open("tech_dd_report.json", "w") as f:
            json.dump(exec_res, f, indent=2)
            
        print(f"Technical DD report saved to tech_dd_report.json")
        return "default"

# if __name__ == "__main__":
#     agent = TechDdAgent()
#     shared = {"data": """
# Company Name: QuantumVision AI

# Description: QuantumVision AI is a deep tech startup founded in 2020 that specializes in combining quantum computing algorithms with computer vision to achieve unprecedented accuracy in real-time image recognition and analysis. Their flagship product, QuantumSight, can process and analyze video feeds 100x faster than traditional solutions while using 80% less computational resources.

# Technology: The company has developed a proprietary method for encoding visual data in quantum-inspired tensors, allowing for efficient parallel processing on both classical and quantum-ready hardware. Their core algorithm incorporates elements of quantum annealing and tensor network theory to dramatically reduce the dimensionality of visual data while preserving critical information.

# Products:
# 1. QuantumSight Pro - Enterprise-grade computer vision system for manufacturing quality control
# 2. QuantumSight Edge - Lightweight implementation designed for IoT and edge devices
# 3. QuantumVision API - Cloud-based API service for developers to integrate vision capabilities

# Market: Initially focused on manufacturing quality control, QuantumVision's technology has applications in autonomous vehicles, medical imaging, retail analytics, and security systems. Their current client base includes 3 Fortune 500 manufacturing companies and several mid-sized industrial automation firms.

# Business Model: SaaS with tiered pricing based on processing volume, plus consulting services for custom implementations. Enterprise licenses start at $50,000/year.

# Funding: Seed round of $2M (2020), Series A of $8M (2022) led by TechVentures Capital. Currently preparing for Series B.

# Traction: ARR of $1.5M with 120% YoY growth. 18 enterprise customers with 92% retention rate.

# Competition: Competing against traditional computer vision companies like Cognex and newer AI-focused startups, though their quantum-inspired approach gives them a unique position in the market.

# Team Size: 24 employees (14 in engineering, 4 in sales/marketing, 3 in operations, 3 in leadership)
# """}
#     prep_data = agent.prep(shared)
#     exec_data = agent.exec(prep_data)
#     print(exec_data)

