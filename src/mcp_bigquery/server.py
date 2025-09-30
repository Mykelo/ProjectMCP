"""FastMCP server for BigQuery operations."""

import logging
from typing import Optional

from fastmcp import FastMCP
from pydantic import Field

from mcp_bigquery.bigquery_client import BigQueryClientError, get_bigquery_client
from mcp_bigquery.config import get_settings

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("BigQuery MCP Server")


@mcp.tool()
def execute_query(
    query: str = Field(
        ...,
        description="SQL query to execute on BigQuery",
        min_length=1,
    ),
    max_results: int = Field(
        default=1000,
        description="Maximum number of rows to return",
        ge=1,
        le=10000,
    ),
    timeout: float = Field(
        default=30.0,
        description="Query timeout in seconds",
        ge=1.0,
        le=300.0,
    ),
) -> dict:
    """
    Execute a SQL query on BigQuery and return the results.

    This tool allows you to run SELECT queries, as well as DDL and DML operations.
    Results are returned with schema information and query statistics.

    Args:
        query: The SQL query to execute
        max_results: Maximum number of rows to return (1-10000)
        timeout: Query timeout in seconds (1-300)

    Returns:
        Dictionary containing:
        - rows: List of result rows as dictionaries
        - schema: Schema information for the result columns
        - statistics: Query statistics (bytes processed, cache hit, etc.)
        - total_rows: Total number of rows in the result set

    Example:
        execute_query(
            query="SELECT * FROM `project.dataset.table` LIMIT 10",
            max_results=10,
            timeout=30.0
        )
    """
    try:
        logger.info(f"Executing query with max_results={max_results}, timeout={timeout}")
        client = get_bigquery_client()
        result = client.execute_query(
            query=query,
            max_results=max_results,
            timeout=timeout,
        )
        return result
    except BigQueryClientError as e:
        logger.error(f"Error executing query: {e}")
        return {
            "error": {
                "code": "QUERY_EXECUTION_ERROR",
                "message": str(e),
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error executing query: {e}")
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": f"Unexpected error: {str(e)}",
            }
        }


@mcp.tool()
def list_datasets(
    max_results: Optional[int] = Field(
        default=None,
        description="Maximum number of datasets to return (optional)",
        ge=1,
        le=1000,
    ),
    page_token: Optional[str] = Field(
        default=None,
        description="Token for pagination (optional)",
    ),
) -> dict:
    """
    List all BigQuery datasets in the configured project.

    Returns basic information about each dataset including ID, location,
    and full dataset identifier.

    Args:
        max_results: Maximum number of datasets to return per page
        page_token: Token for retrieving the next page of results

    Returns:
        Dictionary containing:
        - datasets: List of dataset information dictionaries
        - next_page_token: Token for the next page (if available)

    Example:
        list_datasets(max_results=100)
    """
    try:
        logger.info("Listing datasets")
        client = get_bigquery_client()
        result = client.list_datasets(
            max_results=max_results,
            page_token=page_token,
        )
        return result
    except BigQueryClientError as e:
        logger.error(f"Error listing datasets: {e}")
        return {
            "error": {
                "code": "LIST_DATASETS_ERROR",
                "message": str(e),
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error listing datasets: {e}")
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": f"Unexpected error: {str(e)}",
            }
        }


@mcp.tool()
def get_dataset_info(
    dataset_id: str = Field(
        ...,
        description="The dataset ID to get information about",
        min_length=1,
    ),
) -> dict:
    """
    Get detailed information about a specific BigQuery dataset.

    Returns comprehensive metadata including location, creation time,
    description, labels, and access control information.

    Args:
        dataset_id: The ID of the dataset

    Returns:
        Dictionary containing dataset metadata:
        - dataset_id: The dataset ID
        - project: The project ID
        - location: The dataset location (e.g., US, EU)
        - description: Dataset description
        - created: Creation timestamp
        - modified: Last modification timestamp
        - default_table_expiration_ms: Default table expiration
        - labels: Dataset labels
        - access_entries: Number of access control entries

    Example:
        get_dataset_info(dataset_id="my_dataset")
    """
    try:
        logger.info(f"Getting dataset info for: {dataset_id}")
        client = get_bigquery_client()
        result = client.get_dataset_info(dataset_id=dataset_id)
        return result
    except BigQueryClientError as e:
        logger.error(f"Error getting dataset info: {e}")
        return {
            "error": {
                "code": "GET_DATASET_INFO_ERROR",
                "message": str(e),
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error getting dataset info: {e}")
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": f"Unexpected error: {str(e)}",
            }
        }


@mcp.tool()
def list_tables(
    dataset_id: str = Field(
        ...,
        description="The dataset ID to list tables from",
        min_length=1,
    ),
    max_results: Optional[int] = Field(
        default=None,
        description="Maximum number of tables to return (optional)",
        ge=1,
        le=1000,
    ),
    page_token: Optional[str] = Field(
        default=None,
        description="Token for pagination (optional)",
    ),
) -> dict:
    """
    List all tables in a specific BigQuery dataset.

    Returns basic information about each table including ID, type,
    and creation time.

    Args:
        dataset_id: The ID of the dataset
        max_results: Maximum number of tables to return per page
        page_token: Token for retrieving the next page of results

    Returns:
        Dictionary containing:
        - tables: List of table information dictionaries
        - next_page_token: Token for the next page (if available)

    Example:
        list_tables(dataset_id="my_dataset", max_results=50)
    """
    try:
        logger.info(f"Listing tables in dataset: {dataset_id}")
        client = get_bigquery_client()
        result = client.list_tables(
            dataset_id=dataset_id,
            max_results=max_results,
            page_token=page_token,
        )
        return result
    except BigQueryClientError as e:
        logger.error(f"Error listing tables: {e}")
        return {
            "error": {
                "code": "LIST_TABLES_ERROR",
                "message": str(e),
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error listing tables: {e}")
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": f"Unexpected error: {str(e)}",
            }
        }


@mcp.tool()
def get_table_info(
    dataset_id: str = Field(
        ...,
        description="The dataset ID containing the table",
        min_length=1,
    ),
    table_id: str = Field(
        ...,
        description="The table ID to get information about",
        min_length=1,
    ),
) -> dict:
    """
    Get detailed information about a specific BigQuery table.

    Returns comprehensive metadata including schema, row/byte counts,
    partitioning, clustering, and table properties.

    Args:
        dataset_id: The ID of the dataset containing the table
        table_id: The ID of the table

    Returns:
        Dictionary containing table metadata:
        - table_id: The table ID
        - dataset_id: The dataset ID
        - project: The project ID
        - table_type: Type of table (TABLE, VIEW, etc.)
        - created: Creation timestamp
        - modified: Last modification timestamp
        - num_rows: Number of rows in the table
        - num_bytes: Size of the table in bytes
        - description: Table description
        - schema: Complete table schema
        - partitioning: Partitioning information (if applicable)
        - clustering: Clustering information (if applicable)
        - labels: Table labels

    Example:
        get_table_info(dataset_id="my_dataset", table_id="my_table")
    """
    try:
        logger.info(f"Getting table info for: {dataset_id}.{table_id}")
        client = get_bigquery_client()
        result = client.get_table_info(
            dataset_id=dataset_id,
            table_id=table_id,
        )
        return result
    except BigQueryClientError as e:
        logger.error(f"Error getting table info: {e}")
        return {
            "error": {
                "code": "GET_TABLE_INFO_ERROR",
                "message": str(e),
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error getting table info: {e}")
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": f"Unexpected error: {str(e)}",
            }
        }


# Initialize settings on module import
try:
    settings = get_settings()
    logger.info("MCP BigQuery Server initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MCP BigQuery Server: {e}")
    raise
