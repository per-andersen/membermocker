import pytest


def pytest_addoption(parser):
    """Add custom pytest options"""
    parser.addoption(
        "--run-expensive",
        action="store_true",
        default=False,
        help="Run tests that use external APIs (expensive tests)"
    )


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "expensive: mark test as expensive (uses external APIs)"
    )


@pytest.fixture
def run_expensive(request):
    """Fixture that indicates whether expensive tests should run"""
    return request.config.getoption("--run-expensive")
