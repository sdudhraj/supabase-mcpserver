import pytest
from supabase import create_client, Client
from your_module import supabase_lifespan  # Adjust import based on actual module

# Mocking utilities (assuming you're using pytest-mock or similar)
@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv('SUPABASE_URL', 'test_url')
    monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY', 'test_key')

def test_supabase_lifespan_with_env_vars(mock_env):
    # Simulate the lifespan context
    context = supabase_lifespan()  # This might need adaptation if not directly callable
    assert context.client is not None  # Check if client is created successfully

def test_supabase_lifespan_without_env_vars():
    with pytest.raises(ValueError):
        # Trigger the error case
        supabase_lifespan()  # Ensure this raises ValueError as per the code

# Add more tests for database operations as needed
