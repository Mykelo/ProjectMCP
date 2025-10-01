"""BigQuery client wrapper for MCP BigQuery Server."""

import logging
from typing import Any, Optional, Iterator

from google.cloud import bigquery
from google.cloud.bigquery import Dataset, Table
from google.cloud.bigquery.dataset import DatasetListItem
from google.cloud.exceptions import GoogleCloudError

from mcp_bigquery.config import get_settings

logger = logging.getLogger(__name__)


class BigQueryClientError(Exception):
    """Raised when BigQuery operations fail."""

    pass


class BigQueryClient:
    """Wrapper for Google BigQuery client with simplified operations."""

    def __init__(self) -> None:
        """Initialize BigQuery client with credentials from settings."""
        settings = get_settings()
        try:
            self.client = bigquery.Client(
                project=settings.gcp_project_id,
                credentials=None,  # Uses GOOGLE_APPLICATION_CREDENTIALS env var
            )
            self.project_id = settings.gcp_project_id
            logger.info(f"BigQuery client initialized for project: {self.project_id}")
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {e}")
            raise BigQueryClientError(f"Failed to initialize BigQuery client: {e}")

    def execute_query(
        self,
        query: str,
        max_results: int | None = None,
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query to execute
            max_results: Maximum number of rows to return (default: 1000)
            timeout: Query timeout in seconds (default: 30.0)

        Returns:
            Dictionary containing query results, statistics, and metadata

        Raises:
            BigQueryClientError: If query execution fails
        """
        try:
            logger.info(f"Executing query: {query[:100]}...")

            job_config = bigquery.QueryJobConfig()
            query_job = self.client.query(query, job_config=job_config)

            # Wait for query to complete
            results = query_job.result(timeout=timeout, max_results=max_results)

            # Convert results to list of dictionaries
            rows = []
            for row in results:
                rows.append(dict(row.items()))

            # Get job statistics
            stats = {
                "total_rows": results.total_rows,
                "total_bytes_processed": query_job.total_bytes_processed,
                "total_bytes_billed": query_job.total_bytes_billed,
                "cache_hit": query_job.cache_hit,
                "num_dml_affected_rows": query_job.num_dml_affected_rows,
            }

            # Get schema information
            schema = []
            if results.schema:
                for field in results.schema:
                    schema.append(
                        {
                            "name": field.name,
                            "type": field.field_type,
                            "mode": field.mode,
                            "description": field.description,
                        }
                    )

            logger.info(
                f"Query executed successfully. "
                f"Rows: {len(rows)}, "
                f"Bytes processed: {stats['total_bytes_processed']}"
            )

            return {
                "rows": rows,
                "schema": schema,
                "statistics": stats,
                "total_rows": results.total_rows,
            }

        except GoogleCloudError as e:
            logger.error(f"BigQuery error executing query: {e}")
            raise BigQueryClientError(f"Failed to execute query: {e}")
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            raise BigQueryClientError(f"Unexpected error: {e}")

    def list_datasets(
        self,
        max_results: Optional[int] = None,
        page_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        List all datasets in the project.

        Args:
            max_results: Maximum number of datasets to return
            page_token: Token for pagination

        Returns:
            Dictionary containing datasets and pagination info

        Raises:
            BigQueryClientError: If listing fails
        """
        try:
            logger.info(f"Listing datasets for project: {self.project_id}")

            datasets = self.client.list_datasets(
                project=self.project_id,
                max_results=max_results,
                page_token=page_token,
            )

            dataset_list = []
            for dataset in datasets:
                dataset_list.append(
                    {
                        "dataset_id": dataset.dataset_id,
                        "full_dataset_id": f"{dataset.project}.{dataset.dataset_id}",
                    }
                )

            logger.info(f"Found {len(dataset_list)} datasets")

            return {
                "datasets": dataset_list,
                "next_page_token": datasets.next_page_token,
            }

        except GoogleCloudError as e:
            logger.error(f"BigQuery error listing datasets: {e}")
            raise BigQueryClientError(f"Failed to list datasets: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing datasets: {e}")
            raise BigQueryClientError(f"Unexpected error: {e}")

    def get_dataset_info(self, dataset_id: str) -> dict[str, Any]:
        """
        Get detailed information about a dataset.

        Args:
            dataset_id: The dataset ID

        Returns:
            Dictionary containing dataset metadata

        Raises:
            BigQueryClientError: If operation fails
        """
        try:
            logger.info(f"Getting info for dataset: {dataset_id}")

            dataset_ref = f"{self.project_id}.{dataset_id}"
            dataset: Dataset = self.client.get_dataset(dataset_ref)

            info = {
                "dataset_id": dataset.dataset_id,
                "project": dataset.project,
                "location": dataset.location,
                "description": dataset.description,
                "created": dataset.created.isoformat() if dataset.created else None,
                "modified": dataset.modified.isoformat() if dataset.modified else None,
                "default_table_expiration_ms": dataset.default_table_expiration_ms,
                "labels": dict(dataset.labels) if dataset.labels else {},
                "access_entries": len(dataset.access_entries) if dataset.access_entries else 0,
            }

            logger.info(f"Retrieved info for dataset: {dataset_id}")
            return info

        except GoogleCloudError as e:
            logger.error(f"BigQuery error getting dataset info: {e}")
            raise BigQueryClientError(f"Failed to get dataset info: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting dataset info: {e}")
            raise BigQueryClientError(f"Unexpected error: {e}")

    def list_tables(
        self,
        dataset_id: str,
        max_results: Optional[int] = None,
        page_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        List all tables in a dataset.

        Args:
            dataset_id: The dataset ID
            max_results: Maximum number of tables to return
            page_token: Token for pagination

        Returns:
            Dictionary containing tables and pagination info

        Raises:
            BigQueryClientError: If operation fails
        """
        try:
            logger.info(f"Listing tables in dataset: {dataset_id}")

            dataset_ref = f"{self.project_id}.{dataset_id}"
            tables = self.client.list_tables(
                dataset_ref,
                max_results=max_results,
                page_token=page_token,
            )

            table_list = []
            for table in tables:
                table_list.append(
                    {
                        "table_id": table.table_id,
                        "full_table_id": f"{table.project}.{table.dataset_id}.{table.table_id}",
                        "table_type": table.table_type,
                        "created": table.created.isoformat() if table.created else None,
                    }
                )

            logger.info(f"Found {len(table_list)} tables in dataset: {dataset_id}")

            return {
                "tables": table_list,
                "next_page_token": tables.next_page_token,
            }

        except GoogleCloudError as e:
            logger.error(f"BigQuery error listing tables: {e}")
            raise BigQueryClientError(f"Failed to list tables: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing tables: {e}")
            raise BigQueryClientError(f"Unexpected error: {e}")

    def get_table_info(self, dataset_id: str, table_id: str) -> dict[str, Any]:
        """
        Get detailed information about a table.

        Args:
            dataset_id: The dataset ID
            table_id: The table ID

        Returns:
            Dictionary containing table metadata and schema

        Raises:
            BigQueryClientError: If operation fails
        """
        try:
            logger.info(f"Getting info for table: {dataset_id}.{table_id}")

            table_ref = f"{self.project_id}.{dataset_id}.{table_id}"
            table: Table = self.client.get_table(table_ref)

            # Get schema information
            schema = []
            for field in table.schema:
                schema.append(
                    {
                        "name": field.name,
                        "type": field.field_type,
                        "mode": field.mode,
                        "description": field.description,
                    }
                )

            # Get partitioning info
            partitioning = None
            if table.time_partitioning:
                partitioning = {
                    "type": table.time_partitioning.type_,
                    "field": table.time_partitioning.field,
                    "expiration_ms": table.time_partitioning.expiration_ms,
                }

            # Get clustering info
            clustering = None
            if table.clustering_fields:
                clustering = {
                    "fields": table.clustering_fields,
                }

            info = {
                "table_id": table.table_id,
                "dataset_id": table.dataset_id,
                "project": table.project,
                "table_type": table.table_type,
                "created": table.created.isoformat() if table.created else None,
                "modified": table.modified.isoformat() if table.modified else None,
                "num_rows": table.num_rows,
                "num_bytes": table.num_bytes,
                "description": table.description,
                "schema": schema,
                "partitioning": partitioning,
                "clustering": clustering,
                "labels": dict(table.labels) if table.labels else {},
            }

            logger.info(f"Retrieved info for table: {dataset_id}.{table_id}")
            return info

        except GoogleCloudError as e:
            logger.error(f"BigQuery error getting table info: {e}")
            raise BigQueryClientError(f"Failed to get table info: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting table info: {e}")
            raise BigQueryClientError(f"Unexpected error: {e}")


# Global client instance
_client: Optional[BigQueryClient] = None


def get_bigquery_client() -> BigQueryClient:
    """Get or create the global BigQuery client instance."""
    global _client
    if _client is None:
        _client = BigQueryClient()
    return _client
