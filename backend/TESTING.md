# Testing Guide

This project includes two testing modes to balance between fast development iteration and comprehensive API testing.

## Quick Tests (Default) - With Mocking

Run fast tests that mock external API calls:

```bash
pytest test_api.py
```

This mode:
- ✅ Mocks all external API calls (OpenStreetMap Nominatim, Overpass, Ollama)
- ✅ Runs very quickly (~1 second per test)
- ✅ Perfect for development and CI/CD pipelines
- ✅ No external dependencies or rate limits
- ✅ Deterministic results

**Use this mode when:**
- Developing new features
- Doing refactoring
- Running tests in CI/CD
- You want fast feedback loops (~80 seconds for all tests)

## Expensive Tests - With Real API Calls

Run full tests using real external APIs:

```bash
pytest test_api.py --run-expensive
```

This mode:
- 🔗 Makes real calls to OpenStreetMap APIs (Nominatim, Overpass)
- 🤖 Makes real calls to local Ollama instance (requires Ollama running)
- ⏱️ Runs slower (~26 seconds per member generation test due to API latency)
- 🔄 Subject to rate limits
- 🌐 Requires internet connection
- ✅ Validates actual API integration

**Use this mode when:**
- Working directly on the `get_real_addresses()` function
- Debugging Ollama integration issues
- Validating API integration before a merge
- Preparing for production deployment
- Need to test with real address data and member generation

## Running Specific Tests

Run a single test with mocking:
```bash
pytest test_api.py::test_generate_members
```

Run a single test with real API:
```bash
pytest test_api.py::test_generate_members --run-expensive
```

## How It Works

### Pytest Configuration (`conftest.py`)
- Adds `--run-expensive` command-line option to pytest
- Registers custom markers for test categorization
- Provides `run_expensive` fixture for checking the flag

### Mocking Strategy

#### 1. Address Mocking (`mock_get_real_addresses`)
The `mock_addresses` fixture in `test_api.py`:
- Patches both `app.services.generator.get_real_addresses` and `test_api.get_real_addresses`
- Returns consistent, predictable addresses
- Format: `"Vej {i+1}, 1000 {city}, {country}"`
- Uses Copenhagen coordinates (55.6761, 12.5683) with slight variations

#### 2. Ollama Chat Mocking (`mock_ollama_chat`)
The `mock_chat` fixture in `test_api.py`:
- Patches `app.services.generator.chat`
- Generates realistic member data JSON with:
  - Random first names and surnames
  - Realistic dates (birth and join dates)
  - Proper phone numbers and email addresses
  - Valid UUIDs
- Returns data that passes Pydantic validation

### Conditional Patching
Both fixtures check the `--run-expensive` flag:
- Without `--run-expensive` (default): mocks are applied
- With `--run-expensive`: mocks are skipped, real APIs are called

## Performance Comparison

| Mode | Member Generation Test | All Tests |
|------|------------------------|-----------|
| **Mocked** | 0.69 seconds | ~1.3 seconds |
| **Expensive** | 26 seconds | (depends on API) |

The mocking provides a **37x speedup** for the member generation tests!

## Common Issues

### Tests fail with real API when using `--run-expensive`
- Make sure Ollama is running: `ollama serve`
- Check your internet connection for OpenStreetMap API calls
- OpenStreetMap APIs have rate limits; spread requests over time

### Mock data doesn't match real data format
- The mocks are intentionally simplified for testing
- If your code relies on specific address formatting, use `--run-expensive`
- Consider adjusting the mock to match your real API responses better

