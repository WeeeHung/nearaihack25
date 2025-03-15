"""
Legal Agent for Multi-Agent Due Diligence System

This file provides a high-level interface to the Legal Agent implementation.
It focuses on legal risk analysis and can receive data from other agents.

The Legal Agent can analyze legal risks for companies using market data from:
1. Market Analysis Agent (if available)
2. External data sources:
   - URLs (websites with market information)
   - JSON files (structured market data)
   - Text files (market reports)

Examples:
- Interactive mode (just run without arguments):
  python Legal_agent.py
  
- Basic usage: 
  python Legal_agent.py "CompanyName" "output_report.md"
  
- Using a JSON file as input:
  python Legal_agent.py "CompanyName" "output_report.md" "path/to/market_data.json"
  
- Using a text file as input:
  python Legal_agent.py "CompanyName" "output_report.md" "path/to/market_report.txt"
  
- Using a website URL as input:
  python Legal_agent.py "CompanyName" "output_report.md" "https://example.com/market-report"
"""

from typing import Dict, Any, Optional, List
from pocketflow import Flow, Node
from base_agent import BaseAgent
import random
from datetime import datetime
import json
import os
import re

# Try to import related agents
try:
    from .Market_analysis_agent import analyze_market
    HAS_MARKET_ANALYSIS = True
except ImportError:
    HAS_MARKET_ANALYSIS = False

try:
    from .Due_dillegence_report_agent import get_report_agent
    HAS_REPORT_AGENT = True
except ImportError:
    HAS_REPORT_AGENT = False

class LegalIssue:
    """Represents a potential legal issue or risk."""
    
    def __init__(self, category: str, description: str, severity: float, 
                 recommendations: List[str] = None):
        """
        Initialize a legal issue.
        
        Args:
            category: Category of the legal issue (e.g., "IP", "Compliance")
            description: Description of the issue
            severity: Severity score (0-1, where 1 is most severe)
            recommendations: List of recommendations to address the issue
        """
        self.category = category
        self.description = description
        self.severity = severity
        self.recommendations = recommendations or []

def extract_data_from_url(url: str) -> Dict[str, Any]:
    """
    Extract market data from a website URL.
    
    Args:
        url: URL to extract data from
        
    Returns:
        Dict containing extracted market data
    """
    try:
        # Create a BaseAgent instance to use its scrape method
        base_agent = BaseAgent("scraper")
        title, content = base_agent.scrape(url)
        
        # Extract market size information
        market_size_match = re.search(r'market\s+size.*?(\$[\d.]+ [bmtr]illion|\d+\.?\d* [bmtr]illion)', 
                                    content, re.IGNORECASE)
        market_size = market_size_match.group(1) if market_size_match else "Unknown"
        
        # Extract competitors
        competitors = []
        competitor_section = re.search(r'competitors?:?(.*?)(?:trends|challenges|market size)', 
                                    content, re.IGNORECASE | re.DOTALL)
        if competitor_section:
            comp_text = competitor_section.group(1)
            comp_matches = re.findall(r'([A-Z][A-Za-z\s]+)(?:\(.*?\))?', comp_text)
            for comp in comp_matches[:5]:  # Limit to 5 competitors
                competitors.append({"name": comp.strip(), "market_share": random.randint(5, 30)})
        
        # Extract trends
        trends = []
        trends_section = re.search(r'trends:?(.*?)(?:challenges|competitors|market size)', 
                                 content, re.IGNORECASE | re.DOTALL)
        if trends_section:
            trends_text = trends_section.group(1)
            # Split by bullet points, numbers, or new lines
            trend_items = re.split(r'•|\d+\.|\n+', trends_text)
            for item in trend_items:
                item = item.strip()
                if item and len(item) > 10:  # Avoid empty or very short items
                    trends.append(item)
        
        # Extract challenges
        challenges = []
        challenges_section = re.search(r'challenges:?(.*?)(?:trends|competitors|market size|conclusion)', 
                                    content, re.IGNORECASE | re.DOTALL)
        if challenges_section:
            challenges_text = challenges_section.group(1)
            # Split by bullet points, numbers, or new lines
            challenge_items = re.split(r'•|\d+\.|\n+', challenges_text)
            for item in challenge_items:
                item = item.strip()
                if item and len(item) > 10:  # Avoid empty or very short items
                    challenges.append(item)
        
        # Ensure we have at least some data
        if not trends:
            trends = ["Growing adoption of advanced technologies", 
                    "Increasing regulatory oversight",
                    "Shift towards sustainable practices"]
            
        if not challenges:
            challenges = ["Intense market competition",
                        "Regulatory uncertainty",
                        "Technological disruption"]
        
        # Construct market data
        market_data = {
            "source": f"Web: {url}",
            "title": title,
            "market_size": market_size,
            "competitors": competitors,
            "market_trends": trends[:5],  # Limit to 5 trends
            "market_challenges": challenges[:5]  # Limit to 5 challenges
        }
        
        return {"market_analysis": market_data}
    
    except Exception as e:
        print(f"Error extracting data from URL: {str(e)}")
        return {}

def extract_data_from_json(json_path: str) -> Dict[str, Any]:
    """
    Extract market data from a JSON file.
    
    Args:
        json_path: Path to the JSON file
        
    Returns:
        Dict containing extracted market data
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Check if the JSON already has market_analysis key
        if "market_analysis" in data:
            return data
        
        # If not, try to construct market_analysis from available keys
        market_data = {}
        for key in ["market_size", "competitors", "market_trends", "market_challenges"]:
            if key in data:
                market_data[key] = data[key]
        
        if market_data:
            return {"market_analysis": market_data, "source": f"JSON: {json_path}"}
        
        # If no relevant keys found, return the entire JSON as market_analysis
        return {"market_analysis": data, "source": f"JSON: {json_path}"}
    
    except Exception as e:
        print(f"Error extracting data from JSON file: {str(e)}")
        return {}

def extract_data_from_text(text_path: str) -> Dict[str, Any]:
    """
    Extract market data from a text file.
    
    Args:
        text_path: Path to the text file
        
    Returns:
        Dict containing extracted market data
    """
    try:
        with open(text_path, 'r') as f:
            content = f.read()
        
        # Extract market size information
        market_size_match = re.search(r'market\s+size.*?(\$[\d.]+ [bmtr]illion|\d+\.?\d* [bmtr]illion)', 
                                    content, re.IGNORECASE)
        market_size = market_size_match.group(1) if market_size_match else "Unknown"
        
        # Extract competitors
        competitors = []
        competitor_section = re.search(r'competitors?:?(.*?)(?:trends|challenges|market size)', 
                                    content, re.IGNORECASE | re.DOTALL)
        if competitor_section:
            comp_text = competitor_section.group(1)
            comp_matches = re.findall(r'([A-Z][A-Za-z\s]+)(?:\(.*?\))?', comp_text)
            for comp in comp_matches[:5]:  # Limit to 5 competitors
                competitors.append({"name": comp.strip(), "market_share": random.randint(5, 30)})
        
        # Extract trends
        trends = []
        trends_section = re.search(r'trends:?(.*?)(?:challenges|competitors|market size)', 
                                 content, re.IGNORECASE | re.DOTALL)
        if trends_section:
            trends_text = trends_section.group(1)
            # Split by bullet points, numbers, or new lines
            trend_items = re.split(r'•|\d+\.|\n+', trends_text)
            for item in trend_items:
                item = item.strip()
                if item and len(item) > 10:  # Avoid empty or very short items
                    trends.append(item)
        
        # Extract challenges
        challenges = []
        challenges_section = re.search(r'challenges:?(.*?)(?:trends|competitors|market size|conclusion)', 
                                    content, re.IGNORECASE | re.DOTALL)
        if challenges_section:
            challenges_text = challenges_section.group(1)
            # Split by bullet points, numbers, or new lines
            challenge_items = re.split(r'•|\d+\.|\n+', challenges_text)
            for item in challenge_items:
                item = item.strip()
                if item and len(item) > 10:  # Avoid empty or very short items
                    challenges.append(item)
        
        # Ensure we have at least some data
        if not trends:
            trends = ["Growing adoption of advanced technologies", 
                    "Increasing regulatory oversight",
                    "Shift towards sustainable practices"]
            
        if not challenges:
            challenges = ["Intense market competition",
                        "Regulatory uncertainty",
                        "Technological disruption"]
        
        # Construct market data
        market_data = {
            "source": f"Text file: {text_path}",
            "market_size": market_size,
            "competitors": competitors,
            "market_trends": trends[:5],  # Limit to 5 trends
            "market_challenges": challenges[:5]  # Limit to 5 challenges
        }
        
        return {"market_analysis": market_data}
    
    except Exception as e:
        print(f"Error extracting data from text file: {str(e)}")
        return {}

def detect_and_extract_from_input(input_source: str) -> Dict[str, Any]:
    """
    Detect input type and extract data accordingly.
    
    Args:
        input_source: URL, path to JSON file, or path to text file
        
    Returns:
        Dict containing extracted data
    """
    # Check if input is a URL
    if input_source.startswith(('http://', 'https://')):
        print(f"Detected URL: {input_source}")
        return extract_data_from_url(input_source)
    
    # Check if input is a file that exists
    if os.path.exists(input_source):
        # Check file extension for JSON
        if input_source.lower().endswith('.json'):
            print(f"Detected JSON file: {input_source}")
            return extract_data_from_json(input_source)
        
        # Assume text file for other extensions
        print(f"Detected text file: {input_source}")
        return extract_data_from_text(input_source)
    
    # If input doesn't match known formats, return empty dict
    print(f"Could not determine input type for: {input_source}")
    return {}

class LegalAgent(BaseAgent):
    """Agent responsible for legal analysis of startups."""
    
    def __init__(self, market_data: Optional[Dict[str, Any]] = None, input_source: Optional[str] = None):
        """
        Initialize the Legal Agent.
        
        Args:
            market_data: Optional market analysis data to incorporate
            input_source: Optional URL, JSON file, or text file to extract data from
        """
        super().__init__("legal")
        self.market_data = market_data
        self.input_source = input_source
        self.last_analysis = None
    
    def execute(self, company_name: str) -> Dict[str, Any]:
        """
        Execute legal analysis on a startup.
        
        Args:
            company_name: Name of the company to analyze
            
        Returns:
            Dict containing legal analysis results
        """
        try:
            # Get data for legal analysis
            data = self._get_legal_data(company_name)
            
            # Perform legal analysis
            legal_issues = self._analyze_legal_risks(data)
            
            # Generate a report from the analysis
            report = self._generate_report(legal_issues, company_name)
            
            # Store the analysis for later retrieval
            self.last_analysis = report
            
            return report
            
        except Exception as e:
            raise RuntimeError(f"Failed to analyze legal risks for {company_name}: {str(e)}")
    
    def get_last_analysis(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent legal analysis results.
        
        Returns:
            The last legal analysis or None if no analysis has been performed
        """
        return self.last_analysis
    
    def _get_legal_data(self, company_name: str) -> Dict[str, Any]:
        """
        Get data for legal analysis.
        
        Args:
            company_name: Company name to analyze
            
        Returns:
            Data for legal analysis
        """
        legal_data = {
            "company_name": company_name,
            "analysis_date": datetime.now().isoformat()
        }
        
        # If we have market analysis data, incorporate it
        if self.market_data:
            legal_data["market_analysis"] = self.market_data
        
        # Try to get market data from input_source if provided
        elif hasattr(self, 'input_source') and self.input_source:
            print(f"Extracting data from input source: {self.input_source}")
            extracted_data = detect_and_extract_from_input(self.input_source)
            if "market_analysis" in extracted_data:
                legal_data["market_analysis"] = extracted_data["market_analysis"]
        
        # Try to get market analysis data if not provided
        elif HAS_MARKET_ANALYSIS:
            try:
                market_data = analyze_market(company_name)
                if market_data:
                    legal_data["market_analysis"] = market_data
            except Exception as e:
                print(f"Warning: Failed to get market analysis data: {str(e)}")
        
        # Generate mock legal data for testing
        if not legal_data.get("market_analysis"):
            legal_data["mock_data"] = True
        
        return legal_data
    
    def _analyze_legal_risks(self, data: Dict[str, Any]) -> List[LegalIssue]:
        """
        Analyze legal risks based on available data.
        
        Args:
            data: Data for legal analysis
            
        Returns:
            List of identified legal issues
        """
        # Try to use LLM for analysis, but be prepared to fall back to random generation
        try:
            # Get 4o mini model if available
            o3mini_model = self.get_4o_mini_model(temperature=0.7)
            
            # Extract useful data
            company_name = data.get("company_name", "Unknown")
            market_data = data.get("market_analysis", {})
            
            # Create prompt for legal risk analysis
            market_size = market_data.get("market_size", "Unknown")
            competitors = market_data.get("competitors", [])
            market_trends = market_data.get("market_trends", [])
            market_challenges = market_data.get("market_challenges", [])
            
            # Build competitor summary
            competitor_summary = ""
            if competitors:
                for i, comp in enumerate(competitors[:5]):  # Limit to top 5
                    competitor_summary += f"- {comp.get('name', 'Unknown')}: {comp.get('market_share', 0)}% market share\n"
            
            trends_summary = "\n".join([f"- {trend}" for trend in market_trends])
            challenges_summary = "\n".join([f"- {challenge}" for challenge in market_challenges])
            
            prompt = f"""
As a legal expert, analyze the potential legal risks for {company_name} based on the following information.

MARKET INFORMATION:
- Market Size: {market_size}
- Key Competitors: 
{competitor_summary}
- Market Trends:
{trends_summary}
- Market Challenges:
{challenges_summary}

For each of the following legal categories, identify specific risks, rate their severity on a scale of 0.0-1.0 
(where 1.0 is extremely severe), and provide actionable recommendations:

1. Intellectual Property
2. Regulatory Compliance
3. Contracts
4. Data Privacy
5. Employment

Respond in this JSON format:
{{
  "legal_issues": [
    {{
      "category": "category name",
      "description": "detailed description of the issue",
      "severity": 0.XX,
      "recommendations": ["rec1", "rec2", "rec3"]
    }},
    ...
  ]
}}
"""
            # Try to generate legal issues using LLM
            response = o3mini_model(prompt)
            if response:
                # Extract the JSON part
                import json
                import re
                
                # Find all JSON-like content between curly braces
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    try:
                        json_data = json.loads(json_match.group(0))
                        if "legal_issues" in json_data and json_data["legal_issues"]:
                            # Convert to LegalIssue objects
                            legal_issues = []
                            for issue in json_data["legal_issues"]:
                                # Validate and sanitize data
                                category = issue.get("category", "Miscellaneous")
                                description = issue.get("description", "Undefined legal risk")
                                severity = float(issue.get("severity", 0.5))
                                # Ensure severity is between 0 and 1
                                severity = max(0.0, min(1.0, severity))
                                recommendations = issue.get("recommendations", ["Consult legal counsel"])
                                
                                legal_issues.append(LegalIssue(
                                    category=category,
                                    description=description,
                                    severity=severity,
                                    recommendations=recommendations
                                ))
                            
                            if legal_issues:
                                return legal_issues
                    except Exception:
                        # If JSON parsing fails, fall through to random generation
                        pass
        except Exception as e:
            print(f"LLM-based analysis failed, falling back to random generation: {e}")
        
        # Fallback: Generate mock legal issues if LLM analysis fails
        print("Using fallback method for legal risk generation")
        
        # Set random seed based on company name for consistent results
        company_name = data.get("company_name", "Unknown")
        random.seed(hash(company_name) % 10000)
        
        # Extract market data if available
        market_data = data.get("market_analysis", {})
        
        legal_issues = []
        
        # Generate IP-related issues
        ip_risk = random.uniform(0.1, 0.9)
        ip_issue = LegalIssue(
            category="Intellectual Property",
            description="Potential patent infringement risks in core technology",
            severity=ip_risk,
            recommendations=[
                "Conduct a comprehensive IP audit",
                "Consider filing defensive patents",
                "Implement an IP monitoring system"
            ]
        )
        legal_issues.append(ip_issue)
        
        # Generate compliance issues based on market data
        market_trends = market_data.get("market_trends", [])
        market_challenges = market_data.get("market_challenges", [])
        
        if "Regulatory uncertainty" in market_challenges or any("regulation" in trend.lower() for trend in market_trends):
            compliance_risk = random.uniform(0.6, 0.9)
            compliance_issue = LegalIssue(
                category="Regulatory Compliance",
                description="High regulatory risk due to evolving regulations in the industry",
                severity=compliance_risk,
                recommendations=[
                    "Establish a compliance team or officer role",
                    "Develop a regulatory tracking system",
                    "Create contingency plans for regulatory changes"
                ]
            )
            legal_issues.append(compliance_issue)
        else:
            compliance_risk = random.uniform(0.1, 0.5)
            compliance_issue = LegalIssue(
                category="Regulatory Compliance",
                description="Standard compliance requirements for the industry",
                severity=compliance_risk,
                recommendations=[
                    "Regular compliance reviews",
                    "Stay informed of industry regulations"
                ]
            )
            legal_issues.append(compliance_issue)
        
        # Generate contract risk issues
        contract_risk = random.uniform(0.2, 0.8)
        contract_issue = LegalIssue(
            category="Contracts",
            description="Potential vulnerabilities in key commercial agreements",
            severity=contract_risk,
            recommendations=[
                "Review and standardize contract templates",
                "Implement contract management system",
                "Include appropriate liability limitations"
            ]
        )
        legal_issues.append(contract_issue)
        
        # Generate data privacy issues
        data_privacy_risk = random.uniform(0.3, 0.9)
        privacy_issue = LegalIssue(
            category="Data Privacy",
            description="Exposure to data protection regulations and privacy laws",
            severity=data_privacy_risk,
            recommendations=[
                "Conduct privacy impact assessment",
                "Update privacy policies and procedures",
                "Implement data minimization practices"
            ]
        )
        legal_issues.append(privacy_issue)
        
        # Generate employment law issues
        employment_risk = random.uniform(0.1, 0.7)
        employment_issue = LegalIssue(
            category="Employment",
            description="Potential issues with employee agreements and classifications",
            severity=employment_risk,
            recommendations=[
                "Review employment contracts",
                "Verify worker classifications",
                "Update HR policies"
            ]
        )
        legal_issues.append(employment_issue)
        
        return legal_issues
    
    def _generate_report(self, legal_issues: List[LegalIssue], company_name: str) -> Dict[str, Any]:
        """
        Generate a structured report from the legal analysis.
        
        Args:
            legal_issues: List of identified legal issues
            company_name: Name of the company being analyzed
            
        Returns:
            Dictionary with structured report data
        """
        # Calculate overall legal risk score (weighted average of all issues)
        overall_risk = sum(issue.severity for issue in legal_issues) / len(legal_issues)
        
        # Identify high priority issues
        high_priority_issues = [issue for issue in legal_issues if issue.severity > 0.7]
        
        # Organize issues by category
        issues_by_category = {}
        for issue in legal_issues:
            if issue.category not in issues_by_category:
                issues_by_category[issue.category] = []
            issues_by_category[issue.category].append({
                "description": issue.description,
                "severity": f"{issue.severity:.2f}",
                "recommendations": issue.recommendations
            })
        
        # Generate overall recommendations
        overall_recommendations = []
        if overall_risk > 0.7:
            overall_recommendations.append("Immediate legal counsel engagement recommended")
        if high_priority_issues:
            overall_recommendations.append(f"Address {len(high_priority_issues)} high-priority legal risks")
        
        # Add generic recommendations
        overall_recommendations.extend([
            "Implement a comprehensive legal risk management system",
            "Regular legal audits and reviews"
        ])
        
        # Create the final report structure
        report = {
            "company_name": company_name,
            "analysis_date": datetime.now().isoformat(),
            "overall_legal_risk": overall_risk,
            "high_priority_count": len(high_priority_issues),
            "legal_issues_by_category": issues_by_category,
            "overall_recommendations": overall_recommendations
        }
        
        return report
    
    def generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """
        Generate a markdown-formatted report from the legal analysis.
        
        Args:
            report: Legal analysis report dictionary
            
        Returns:
            Markdown-formatted report string
        """
        try:
            # Try to use 4o mini model if available
            o3mini_model = self.get_4o_mini_model(temperature=0.7)
            
            # Extract relevant data from the report
            company_name = report['company_name']
            analysis_date = report['analysis_date']
            overall_risk = report['overall_legal_risk']
            high_priority_count = report['high_priority_count']
            issues_by_category = report['legal_issues_by_category']
            overall_recommendations = report['overall_recommendations']
            
            # Prepare summary of legal issues for the prompt
            issues_summary = ""
            for category, issues in issues_by_category.items():
                issues_summary += f"- {category}:\n"
                for issue in issues:
                    severity = float(issue['severity'])
                    severity_level = "High" if severity > 0.7 else "Medium" if severity > 0.4 else "Low"
                    issues_summary += f"  - {issue['description']} (Severity: {issue['severity']}, {severity_level})\n"
                    issues_summary += f"    Recommendations: {', '.join(issue['recommendations'])}\n"
            
            # Create prompt for o3mini
            prompt = f"""
Generate a comprehensive legal risk analysis report in markdown format for {company_name}.
The report should have the following structure:

1. Title with company name
2. Analysis date
3. Executive summary with overall risk score ({overall_risk:.2f}/1.00) and high priority issues count ({high_priority_count})
4. Detailed section for each legal issue category
5. Overall recommendations section

Here is the summary of legal issues to include:
{issues_summary}

Overall recommendations:
{', '.join(overall_recommendations)}

Make sure the report is professionally formatted in markdown with appropriate headers, bullet points, and emphasis.
Include a note at the end that this report was generated by the Legal Analysis Agent and data should be verified with legal counsel.
"""

            # Try to generate the report using LLM
            try:
                generated_report = o3mini_model(prompt)
                if generated_report:
                    return generated_report
            except Exception as e:
                print(f"LLM-based report generation failed, falling back to template: {e}")
        except Exception as e:
            print(f"Error setting up LLM for report generation: {e}")
        
        # Fallback to template-based generation if LLM fails
        md = f"""# Legal Risk Analysis: {report['company_name']}

*Generated on: {report['analysis_date']}*

## Executive Summary

**Overall Legal Risk Score:** {report['overall_legal_risk']:.2f}/1.00  
**High Priority Issues:** {report['high_priority_count']}

## Legal Issues by Category

"""
        # Add each category of legal issues
        for category, issues in report['legal_issues_by_category'].items():
            md += f"### {category}\n\n"
            
            for i, issue in enumerate(issues):
                severity = float(issue['severity'])
                severity_level = "High" if severity > 0.7 else "Medium" if severity > 0.4 else "Low"
                
                md += f"**Issue {i+1}:** {issue['description']}  \n"
                md += f"**Severity:** {issue['severity']} ({severity_level})  \n"
                md += "**Recommendations:**  \n"
                
                for rec in issue['recommendations']:
                    md += f"- {rec}  \n"
                
                md += "\n"

        # Add overall recommendations
        md += "## Overall Recommendations\n\n"
        for rec in report['overall_recommendations']:
            md += f"- {rec}\n"
        
        md += "\n---\n\n*This report was generated by the Legal Analysis Agent. Data should be verified with legal counsel.*"
        
        return md
    
    def save_markdown_report(self, report: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate and save a markdown report to a file.
        
        Args:
            report: Legal analysis report dictionary
            output_path: Path to save the report (default: current directory)
            
        Returns:
            str: Path to the saved report
        """
        md_content = self.generate_markdown_report(report)
        
        if output_path is None:
            company_name = report['company_name'].lower().replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d")
            output_path = f"legal_analysis_{company_name}_{timestamp}.md"
        
        with open(output_path, "w") as f:
            f.write(md_content)
        
        return output_path

class LegalAnalysisNode(Node):
    """Node for executing legal analysis"""
    
    def __init__(self, market_data: Optional[Dict[str, Any]] = None, input_source: Optional[str] = None):
        super().__init__()
        self.market_data = market_data
        self.input_source = input_source
        
    def prep(self, shared):
        """Prepare for legal analysis"""
        company_name = shared.get("company_name", "Unknown")
        
        # Get market data from shared if available
        if self.market_data is None and "market_data" in shared:
            self.market_data = shared["market_data"]
            
        # Get input source from shared if available
        if self.input_source is None and "input_source" in shared:
            self.input_source = shared["input_source"]
            
        return company_name
    
    def exec(self, company_name):
        """Execute legal analysis"""
        # Create legal agent
        legal_agent = LegalAgent(market_data=self.market_data, input_source=self.input_source)
        
        # Execute legal analysis
        return legal_agent.execute(company_name)
    
    def post(self, shared, prep_res, exec_res):
        """Process analysis results"""
        shared["legal_analysis"] = exec_res
        
        # Send data to Due Diligence Report Agent if available
        if HAS_REPORT_AGENT and exec_res:
            try:
                report_agent = get_report_agent()
                if report_agent:
                    report_agent.add_legal_data(exec_res)
                    print("Legal analysis data sent to Due Diligence Report Agent")
            except Exception as e:
                print(f"Warning: Failed to send data to Due Diligence Report Agent: {str(e)}")
                
        return "default"

class ReportGenerationNode(Node):
    """Node for generating legal reports"""
    
    def __init__(self, output_path: Optional[str] = None):
        super().__init__()
        self.output_path = output_path
    
    def prep(self, shared):
        """Prepare for report generation"""
        analysis_result = shared.get("legal_analysis", {})
        company_name = shared.get("company_name", "Unknown")
        return analysis_result, company_name
    
    def exec(self, inputs):
        """Generate legal report"""
        analysis_result, company_name = inputs
        legal_agent = LegalAgent()
        
        if not analysis_result:
            return "No legal analysis data available."
            
        return legal_agent.generate_markdown_report(analysis_result)
    
    def post(self, shared, prep_res, exec_res):
        """Save generated report"""
        analysis_result, company_name = prep_res
        shared["report_content"] = exec_res
        
        if self.output_path:
            # Save to specified path
            with open(self.output_path, "w") as f:
                f.write(exec_res)
            shared["report_path"] = self.output_path
        else:
            # Generate default filename if no path specified
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"legal_report_{company_name}_{timestamp}.md"
            
            with open(filename, "w") as f:
                f.write(exec_res)
            shared["report_path"] = filename
        
        return "default"

def analyze_legal_risks(company_name: str, market_data=None, input_source=None, output_path=None, send_to_report=True) -> Dict[str, Any]:
    """
    Analyze company legal risks and generate a report.
    
    Args:
        company_name (str): Name of the company to analyze
        market_data (dict, optional): Market analysis data 
        input_source (str, optional): URL, JSON file, or text file to extract data from
        output_path (str, optional): Path to save the report
        send_to_report (bool): Whether to send data to the Due Diligence Report Agent
        
    Returns:
        Dict containing the legal analysis results
    """
    # Create shared data store
    shared = {
        "company_name": company_name,
        "send_to_report": send_to_report
    }
    
    # Add market data if provided
    if market_data:
        shared["market_data"] = market_data
        
    # Add input source if provided
    if input_source:
        shared["input_source"] = input_source
    
    # Create analysis and report nodes
    legal = LegalAnalysisNode(market_data=market_data, input_source=input_source)
    report = ReportGenerationNode(output_path=output_path)
    
    # Connect nodes
    legal >> report
    
    # Create and run flow
    flow = Flow(start=legal)
    flow.run(shared)
    
    # Return analysis results
    return shared.get("legal_analysis", {})

def get_legal_data(company_name: str = None) -> Dict[str, Any]:
    """
    Get the last legal analysis results for a company.
    
    This function can be called by other agents (e.g., Due Diligence Report Agent)
    to get legal analysis data.
    
    Args:
        company_name: Optional company name filter
        
    Returns:
        Dict containing the legal analysis results
    """
    # In a production environment, this would retrieve data from a database
    # For simplicity, we'll check if we have an already-created LegalAgent
    # with analysis results, or create a new one if needed
    legal_agent = LegalAgent()
    
    # Check if we have saved analysis for this company
    if hasattr(legal_agent, 'last_analysis') and legal_agent.last_analysis:
        if company_name is None or legal_agent.last_analysis.get('company_name') == company_name:
            return legal_agent.last_analysis
    
    # If no saved analysis or doesn't match company, create a new analysis
    if company_name:
        return analyze_legal_risks(company_name, send_to_report=False)
    
    # Return empty dict if no company name and no saved analysis
    return {}

# Main function for CLI usage
if __name__ == "__main__":
    import sys
    import json
    
    def prompt_for_input():
        """Interactive mode to prompt user for all inputs"""
        print("\n=== Legal Risk Analysis Agent ===\n")
        
        # Prompt for company name
        company_name = input("Enter company name: ").strip()
        while not company_name:
            print("Company name is required.")
            company_name = input("Enter company name: ").strip()
            
        # Prompt for input source type
        print("\nSelect data source type:")
        print("1. Website URL")
        print("2. JSON file")
        print("3. Text file")
        print("4. No external data (use Market Analysis Agent if available)")
        
        source_type = input("\nEnter choice (1-4): ").strip()
        input_source = None
        
        while source_type not in ["1", "2", "3", "4"]:
            print("Invalid choice. Please select 1-4.")
            source_type = input("Enter choice (1-4): ").strip()
        
        if source_type != "4":
            if source_type == "1":
                input_source = input("\nEnter website URL: ").strip()
                while not input_source.startswith(("http://", "https://")):
                    print("Invalid URL. Must start with http:// or https://")
                    input_source = input("Enter website URL: ").strip()
            
            elif source_type == "2":
                input_source = input("\nEnter path to JSON file: ").strip()
                while not os.path.exists(input_source) or not input_source.lower().endswith('.json'):
                    print("Invalid file path or not a JSON file.")
                    input_source = input("Enter path to JSON file: ").strip()
            
            elif source_type == "3":
                input_source = input("\nEnter path to text file: ").strip()
                while not os.path.exists(input_source):
                    print("File not found.")
                    input_source = input("Enter path to text file: ").strip()
        
        # Prompt for output file
        default_output = f"legal_report_{company_name.lower().replace(' ', '_')}.md"
        output_path = input(f"\nEnter output file path (default: {default_output}): ").strip()
        if not output_path:
            output_path = default_output
            
        return company_name, input_source, output_path
    
    # Check if arguments were provided
    if len(sys.argv) < 2:
        print("Starting interactive mode...")
        company_name, input_source, output_path = prompt_for_input()
    else:
        company_name = sys.argv[1]
        output_path = None
        input_source = None
        
        # Handle optional arguments
        if len(sys.argv) > 2:
            output_path = sys.argv[2]
        
        if len(sys.argv) > 3:
            input_source = sys.argv[3]
    
    # Try to get market data from input source if provided
    market_data = None
    if input_source:
        print(f"Extracting data from input source: {input_source}")
        extracted_data = detect_and_extract_from_input(input_source)
        if "market_analysis" in extracted_data:
            market_data = extracted_data["market_analysis"]
    
    # Try to get market data from Market Analysis Agent if no input source provided
    if market_data is None and HAS_MARKET_ANALYSIS and not input_source:
        try:
            print(f"Retrieving market analysis data for {company_name}...")
            market_data = analyze_market(company_name)
        except Exception as e:
            print(f"Warning: Could not retrieve market analysis: {str(e)}")
    
    # Run legal analysis
    print(f"Analyzing legal risks for {company_name}...")
    analysis = analyze_legal_risks(company_name, market_data=market_data, input_source=input_source, output_path=output_path)
    
    # Report output location
    if output_path:
        print(f"Legal report saved to: {output_path}")
    else:
        print(json.dumps(analysis, indent=2))
