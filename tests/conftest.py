import os
import json
import pytest
from pathlib import Path

# Path to the test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"

@pytest.fixture(scope="session")
def test_api_key():
    """Get the API key for testing."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")
    return api_key

@pytest.fixture(scope="session")
def test_llm_model():
    """Get the LLM model to use for testing."""
    return os.environ.get("TEST_LLM_MODEL", "gpt-3.5-turbo")

@pytest.fixture(scope="session")
def sample_company_data():
    """Load sample company data for testing."""
    sample_data_path = TEST_DATA_DIR / "sample_company.json"
    
    # If the file doesn't exist yet, create it with sample data
    if not sample_data_path.exists():
        sample_data = {
            "name": "TechInnovate Inc.",
            "industry": "Software",
            "funding_stage": "Series B",
            "founding_year": 2018,
            "employees": 85,
            "founders": [
                {"name": "Jane Smith", "role": "CEO", "background": "Former Google PM"},
                {"name": "Michael Chen", "role": "CTO", "background": "MIT CS PhD"}
            ],
            "funding": {
                "total_raised": "$32M",
                "latest_round": {
                    "amount": "$20M",
                    "date": "2024-01-15",
                    "investors": ["Sequoia Capital", "Andreessen Horowitz"]
                },
                "previous_rounds": [
                    {
                        "type": "Seed",
                        "amount": "$2M",
                        "date": "2020-05-10"
                    },
                    {
                        "type": "Series A",
                        "amount": "$10M",
                        "date": "2022-08-22"
                    }
                ]
            },
            "product": {
                "description": "AI-powered enterprise workflow automation platform",
                "key_features": [
                    "Natural language processing for document understanding",
                    "Workflow automation with minimal coding",
                    "Integration with major enterprise systems"
                ],
                "target_market": "Mid to large enterprises in finance and healthcare"
            },
            "financials": {
                "annual_revenue": "$5.8M",
                "burn_rate": "$400K/month",
                "runway": "14 months"
            }
        }
        
        # Create the directory if it doesn't exist
        TEST_DATA_DIR.mkdir(exist_ok=True)
        
        # Save the sample data
        with open(sample_data_path, 'w') as f:
            json.dump(sample_data, f, indent=2)
    
    # Load and return the sample data
    with open(sample_data_path, 'r') as f:
        return json.load(f)

@pytest.fixture
def mock_agent_output():
    """Sample output from various agents for testing."""
    return {
        "market_analysis": {
            "market_size": "$12.5B",
            "growth_rate": "18% CAGR",
            "key_trends": [
                "Increasing adoption of AI in enterprise workflows",
                "Shift towards low-code/no-code solutions",
                "Growing demand for integration capabilities"
            ],
            "competitive_landscape": "Moderately competitive with 5-7 major players"
        },
        "financial_analysis": {
            "burn_rate_assessment": "Moderately high but sustainable given funding",
            "revenue_growth": "142% YoY",
            "unit_economics": "Improving with scale",
            "financial_risks": ["High customer acquisition cost", "Long sales cycles"]
        },
        "legal_analysis": {
            "ip_status": "5 pending patents, strong IP position",
            "regulatory_risks": "Low to moderate",
            "compliance_status": "No significant issues identified"
        }
    }

@pytest.fixture
def benchmark_metrics():
    """Standard benchmark metrics for performance testing."""
    return {
        "execution_time": {
            "screening": 12.5,  # seconds
            "market_analysis": 45.2,
            "financial_analysis": 38.7,
            "legal_analysis": 30.1,
            "team_evaluation": 22.8,
            "tech_due_diligence": 50.3,
            "report_generation": 28.6,
            "full_pipeline": 228.2
        },
        "token_usage": {
            "input_tokens": 15420,
            "output_tokens": 8750,
            "total_tokens": 24170
        },
        "accuracy_metrics": {
            "risk_identification": 0.92,  # 92% of risks correctly identified
            "opportunity_identification": 0.87,
            "overall_assessment": 0.90
        }
    }
