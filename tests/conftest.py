"""Pytest configuration and fixtures for MCP BigQuery Server tests."""

import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from unittest.mock import patch
    from pathlib import Path
    
    mock_settings = Mock()
    mock_settings.bearer_token = "test-bearer-token-with-at-least-32-characters"
    mock_settings.google_application_credentials = Path("/fake/path/credentials.json")
    mock_settings.gcp_project_id = "test-project-id"
    mock_settings.log_level = "INFO"
    mock_settings.host = "0.0.0.0"
    mock_settings.port = 8080
    
    with patch("mcp_bigquery.config.get_settings", return_value=mock_settings):
        yield mock_settings


@pytest.fixture
def mock_bigquery_client():
    """Mock BigQuery client for testing."""
    from unittest.mock import patch
    
    mock_client = MagicMock()
    
    with patch("mcp_bigquery.bigquery_client.bigquery.Client", return_value=mock_client):
        yield mock_client


@pytest.fixture
def sample_query_result():
    """Sample query result for testing."""
    return {
        "rows": [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
        ],
        "schema": [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED", "description": None},
            {"name": "name", "type": "STRING", "mode": "NULLABLE", "description": None},
            {"name": "age", "type": "INTEGER", "mode": "NULLABLE", "description": None},
        ],
        "statistics": {
            "total_rows": 2,
            "total_bytes_processed": 1024,
            "total_bytes_billed": 10240,
            "cache_hit": False,
            "num_dml_affected_rows": None,
        },
        "total_rows": 2,
    }


@pytest.fixture
def sample_datasets():
    """Sample datasets list for testing."""
    return {
        "datasets": [
            {
                "dataset_id": "dataset1",
                "full_dataset_id": "test-project.dataset1",
                "location": "US",
            },
            {
                "dataset_id": "dataset2",
                "full_dataset_id": "test-project.dataset2",
                "location": "EU",
            },
        ],
        "next_page_token": None,
    }


@pytest.fixture
def sample_tables():
    """Sample tables list for testing."""
    return {
        "tables": [
            {
                "table_id": "table1",
                "full_table_id": "test-project.dataset1.table1",
                "table_type": "TABLE",
                "created": "2023-01-01T00:00:00+00:00",
            },
            {
                "table_id": "table2",
                "full_table_id": "test-project.dataset1.table2",
                "table_type": "VIEW",
                "created": "2023-01-02T00:00:00+00:00",
            },
        ],
        "next_page_token": None,
    }
