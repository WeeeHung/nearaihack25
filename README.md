# Multi-Agent Due Diligence System

This directory contains the implementation of a multi-agent system for performing comprehensive due diligence on companies.

## Agents Overview

- **Market Analysis Agent**: Analyzes market trends, size, competitors, and growth potential
- **Financial Agent**: Evaluates financial health, metrics, projections, and risks
- **Legal Agent**: Identifies legal risks, regulatory issues, and compliance challenges
- **Competitors Agent**: Identifies competitors, market share, and growth potential
- **Due Diligence Report Agent**: Aggregates data from other agents and generates a comprehensive report

## Setup

### API Keys

The agents use external APIs that require authentication. Set up your API keys as environment variables:

```bash
# OpenAI API for LLM access
export OPENAI_API_KEY="your_openai_key_here"

# Alternative: temporarily set the API key for a single run
OPENAI_API_KEY="your_openai_key_here" python3 -m Agents.Legal_agent "CompanyName" "output.md"
```

## Using the Legal Agent

The Legal Agent can analyze legal risks for a company using market data from various sources:

### Interactive Mode

The easiest way to use the Legal Agent is to run it in interactive mode:

```bash
python3 -m Agents.Legal_agent
```

This will guide you through:

1. Entering the company name
2. Selecting a data source (URL, JSON file, text file, or no external data)
3. Providing the specific input source
4. Specifying an output file path

### Command-Line Usage

Alternatively, you can use the command-line version:

```bash
python3 -m Agents.Legal_agent "CompanyName" "output_report.md"
```

### Using External Data Sources

The Legal Agent can accept three types of input sources:

1. **JSON files** with structured market data:

```bash
python3 -m Agents.Legal_agent "CompanyName" "output_report.md" "path/to/market_data.json"
```

2. **Text files** containing market analysis:

```bash
python3 -m Agents.Legal_agent "CompanyName" "output_report.md" "path/to/market_report.txt"
```

3. **Website URLs** with market information:

```bash
python3 -m Agents.Legal_agent "CompanyName" "output_report.md" "https://example.com/market-report"
```

### JSON Format

When using JSON files, the data should follow this structure:

```json
{
    "market_size": "$345 billion",
    "competitors": [
        {
            "name": "Competitor1",
            "market_share": 35
        },
        ...
    ],
    "market_trends": [
        "Trend 1",
        "Trend 2",
        ...
    ],
    "market_challenges": [
        "Challenge 1",
        "Challenge 2",
        ...
    ]
}
```

## Integration with Flow

The agents are designed to be used as part of a PocketFlow workflow. Example usage:

```python
from pocketflow import Flow
from Agents.Legal_agent import LegalAnalysisNode, ReportGenerationNode

# Create nodes
legal_node = LegalAnalysisNode(input_source="path/to/data.json")
report_node = ReportGenerationNode(output_path="legal_report.md")

# Connect nodes
legal_node >> report_node

# Create and run flow
flow = Flow(start=legal_node)
flow.run({"company_name": "AIStartup"})
```
