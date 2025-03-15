# DiligenceAI Testing Framework

This directory contains tests for the DiligenceAI system to ensure reliability, reproducibility, and consistent performance.

## Testing Structure

- `test_agents.py`: Unit tests for individual agents (Screening, Market Analysis, Financial, etc.)
- `test_integration.py`: Tests interactions between multiple agents
- `test_pipeline.py`: End-to-end tests of the complete DiligenceAI pipeline
- `conftest.py`: Pytest fixtures and configuration
- `data/`: Sample test data for consistent, reproducible testing

## Setup

1. Install test dependencies:
   ```bash
   pip install -r tests/requirements.txt
   ```

2. Set up the test environment:
   ```bash
   # Set OpenAI API key for testing
   export OPENAI_API_KEY="your_openai_key_here"
   
   # Use a lower-cost model for testing
   export TEST_LLM_MODEL="gpt-3.5-turbo"
   ```

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run specific test categories
```bash
# Test individual agents
pytest tests/test_agents.py

# Test agent integration
pytest tests/test_integration.py

# Test full pipeline
pytest tests/test_pipeline.py
```

### Performance Testing
```bash
# Run performance benchmarks
pytest tests/test_pipeline.py::test_performance_benchmark
```

## Reproducibility

The tests are designed for reproducible results by:

1. Using fixed seed values for any randomization
2. Using consistent sample data in `tests/data/`
3. Employing deterministic LLM prompts
4. Mocking external API calls when appropriate
5. Recording benchmark metrics in standardized formats

## Sample Test Data

The `tests/data/` directory contains:

- Sample company information for analysis
- Standardized test cases representing different company types
- Mock financial statements, legal documents, and market data
- Benchmark reference outputs for validation

## Adding New Tests

When adding new agents or capabilities to DiligenceAI, please:

1. Add corresponding unit tests in `test_agents.py`
2. Update integration tests as needed
3. Ensure benchmark tests accurately reflect new capabilities
4. Add any required test data to the `data/` directory 