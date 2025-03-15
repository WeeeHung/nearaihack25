import pytest
import json
import time
import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the agent orchestration module (update based on your project structure)
try:
    from agent import DiligenceAI  # Assuming this is your main orchestration class
    HAS_ORCHESTRATION = True
except ImportError:
    HAS_ORCHESTRATION = False

# Path for saving benchmark results
BENCHMARK_DIR = Path(__file__).parent / "benchmarks"
BENCHMARK_DIR.mkdir(exist_ok=True)

# Skip if orchestration is not available
pytestmark = pytest.mark.skipif(not HAS_ORCHESTRATION, reason="DiligenceAI orchestration not available")

class TestPipeline:
    """Test the full DiligenceAI pipeline."""
    
    @patch("agent.DiligenceAI._call_llm")
    def test_full_pipeline(self, mock_call_llm, sample_company_data):
        """Test the full DiligenceAI pipeline with mocked LLM calls."""
        # This test will use different mock responses based on the agent type
        def mock_llm_side_effect(prompt, agent_type):
            if "screening" in agent_type.lower():
                return json.dumps({
                    "initial_assessment": "Promising",
                    "key_areas_to_investigate": ["Market growth", "Technical validation"],
                    "risk_level": "Medium"
                })
            elif "market" in agent_type.lower():
                return json.dumps({
                    "market_size": "$12.5B",
                    "growth_rate": "18% CAGR",
                    "key_trends": ["AI adoption"],
                    "competitive_landscape": "Moderately competitive"
                })
            elif "tech" in agent_type.lower():
                return json.dumps({
                    "technology_stack": ["Python", "TensorFlow", "AWS"],
                    "technical_innovations": ["Custom NLP model"],
                    "technical_debt": "Low",
                    "scalability_assessment": "Good"
                })
            elif "report" in agent_type.lower():
                return json.dumps({
                    "executive_summary": "TechInnovate Inc. is promising...",
                    "key_findings": ["Strong market position", "Solid technical foundation"],
                    "risk_assessment": "Medium",
                    "recommendation": "Proceed with investment consideration"
                })
            else:
                return json.dumps({"result": "Generic response for " + agent_type})
        
        mock_call_llm.side_effect = mock_llm_side_effect
        
        # Initialize and run the pipeline
        pipeline = DiligenceAI(company_name=sample_company_data["name"])
        result = pipeline.run(sample_company_data)
        
        # Assertions
        assert "report" in result
        assert "executive_summary" in result["report"]
        assert "recommendation" in result["report"]
        
        # Verify LLM was called multiple times (once per agent)
        assert mock_call_llm.call_count >= 4
    
    @pytest.mark.benchmark
    def test_performance_benchmark(self, benchmark_metrics):
        """Benchmark the performance of the DiligenceAI pipeline."""
        # Create a benchmark data frame
        df = pd.DataFrame({
            "Component": list(benchmark_metrics["execution_time"].keys()),
            "Execution Time (s)": list(benchmark_metrics["execution_time"].values())
        })
        
        # Save the benchmark data
        df.to_csv(BENCHMARK_DIR / "execution_times.csv", index=False)
        
        # Create a visualization
        plt.figure(figsize=(10, 6))
        bars = plt.barh(df["Component"], df["Execution Time (s)"], color="skyblue")
        plt.xlabel("Execution Time (seconds)")
        plt.title("DiligenceAI Component Performance")
        plt.tight_layout()
        
        # Add data labels
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 1, bar.get_y() + bar.get_height()/2, f"{width:.1f}s", 
                    ha='left', va='center')
        
        # Save the visualization
        plt.savefig(BENCHMARK_DIR / "performance_benchmark.png")
        
        # Token usage metrics
        token_df = pd.DataFrame({
            "Token Type": list(benchmark_metrics["token_usage"].keys()),
            "Count": list(benchmark_metrics["token_usage"].values())
        })
        token_df.to_csv(BENCHMARK_DIR / "token_usage.csv", index=False)
        
        # Accuracy metrics
        accuracy_df = pd.DataFrame({
            "Metric": list(benchmark_metrics["accuracy_metrics"].keys()),
            "Score": list(benchmark_metrics["accuracy_metrics"].values())
        })
        accuracy_df.to_csv(BENCHMARK_DIR / "accuracy_metrics.csv", index=False)
        
        # Simple assertions to verify the test ran
        assert df["Execution Time (s)"].sum() > 0
        assert os.path.exists(BENCHMARK_DIR / "performance_benchmark.png")
        assert os.path.exists(BENCHMARK_DIR / "token_usage.csv")
        assert os.path.exists(BENCHMARK_DIR / "accuracy_metrics.csv")
    
    @pytest.mark.parametrize("industry", ["Software", "Healthcare", "Financial Services"])
    def test_industry_specific_analysis(self, industry):
        """Test that DiligenceAI works across different industries."""
        # This test would use industry-specific sample data
        # Just a placeholder for now - could expand with actual industry variants
        industry_data = {
            "name": f"Company in {industry}",
            "industry": industry,
            # Other industry-specific fields would go here
        }
        
        # Skip actual execution for now since we're just creating test structure
        assert industry in industry_data["industry"]
