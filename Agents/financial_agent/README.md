# Financial Agent

The Financial Agent is a component of the multi-agent due diligence system that performs in-depth financial analysis of startups and private companies.

## Features

- Analyzes startup financial health and viability
- Calculates key SaaS/tech company metrics
- Provides valuation estimates based on revenue multiples
- Generates recommendations for fundraising and financial strategy
- Seamlessly integrates with both Screening Agent and Market Analysis Agent

## Integration with Other Agents

The Financial Agent is designed to work with data from:

1. **Screening Agent**: Provides basic financial data
2. **Market Analysis Agent**: Provides market context to enrich financial analysis

### Data Flow

```
                    +-------------------+
                    |                   |
                    | Screening Agent   |
                    |                   |
                    +--------+----------+
                             |
                             | financial_data
                             v
          +----------------+ | +-------------------+
          |                | | |                   |
          | Market Analysis| | | Financial Agent   |
          | Agent          | | |                   |
          +-------+--------+ | +--------+----------+
                  |          |          |
                  |          |          |
                  +----------+----------+
                             |
                             | financial_report
                             v
                    +-------------------+
                    |                   |
                    |    Due Diligence  |
                    |    Report Agent   |
                    +-------------------+
```

## Key Metrics Analyzed

- Revenue & Growth Rate
- Unit Economics (LTV, CAC, LTV/CAC ratio)
- Burn Rate & Runway
- Gross Margins
- MRR & ARR
- Funding History
- Valuation Estimates
- Market Context (when market data is available)

## Usage

### Complete Integration (Recommended)

```python
from Agents.screening_agent.agent import ScreeningAgent
from Agents.financial_agent.agent import FinancialAgent
from Agents.Market_analysis_agent import analyze_market
from Agents.base_agent import AgentContext

# Set up screening agent
context = AgentContext(company_name="MyStartup")
screening_agent = ScreeningAgent(context=context)

# Run screening to get initial data
screening_agent.execute("MyStartup")

# Get market analysis data
market_data = analyze_market("MyStartup")

# Create financial agent with both data sources
financial_agent = FinancialAgent(
    screening_agent=screening_agent,
    market_data=market_data
)

# Run financial analysis
report = financial_agent.execute("MyStartup")

# Generate markdown report
report_path = financial_agent.save_markdown_report(report, "financial_analysis.md")
```

### With Screening Agent Only

```python
from Agents.screening_agent.agent import ScreeningAgent
from Agents.financial_agent.agent import FinancialAgent
from Agents.base_agent import AgentContext

# Set up screening agent
context = AgentContext(company_name="MyStartup")
screening_agent = ScreeningAgent(context=context)

# Run screening to get initial data
screening_agent.execute("MyStartup")

# Create financial agent with screening agent
financial_agent = FinancialAgent(screening_agent=screening_agent)

# Run financial analysis
report = financial_agent.execute("MyStartup")
```

### With Market Analysis Only

```python
from Agents.financial_agent.agent import FinancialAgent
from Agents.Market_analysis_agent import analyze_market

# Get market analysis data
market_data = analyze_market("MyStartup")

# Create financial agent with market data
financial_agent = FinancialAgent(market_data=market_data)

# Run financial analysis
report = financial_agent.execute("MyStartup")
```

### Standalone Mode

```python
from Agents.financial_agent.agent import FinancialAgent

# Create financial agent (will use mock data)
financial_agent = FinancialAgent()

# Run financial analysis
report = financial_agent.execute("MyStartup")

# Print summary
print(f"Financial Health Score: {report['financial_health_score']:.2f}")
print(f"Fundraising Readiness: {report['fundraising_readiness']:.2f}")
```

## Report Format

The financial agent generates a structured report with the following sections:

- Executive Summary
- Unit Economics
- Cash Flow Analysis
- Funding History
- Valuation Analysis
- Risk Assessment
- Growth Opportunities
- Recommendations

## Command Line Usage

You can also run the Financial Agent from the command line:

```bash
python Agents/Financials_agent.py "MyStartup" financial_report.md
``` 