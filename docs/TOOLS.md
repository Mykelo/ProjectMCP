## FastMCP Tools Spec (MCP-only)

This document defines the MCP tools (no HTTP endpoints) for the BigQuery server, implemented with FastMCP's `@mcp.tool` decorator. See FastMCP tools guide for behavior and schema generation based on function signatures and annotations.

Reference: `https://gofastmcp.com/servers/tools`

BigQuery client methods referenced: `https://cloud.google.com/python/docs/reference/bigquery/latest/summary_method`

---

### Conventions
- All tools require bearer token auth (validated by middleware before tool execution).
- FQIDs
  - `dataset_fqid`: `project.dataset`
  - `table_fqid`: `project.dataset.table`
- Pagination: tools that return lists accept `page_size` and `page_token` and return `next_page_token` when more results exist.
- Locations: optional `location` argument; default from server config if omitted.

---

### Tool: list_datasets

```python
from typing import Annotated, Optional
from pydantic import Field

@mcp.tool(
    description="List BigQuery datasets in a project",
    tags={"bigquery", "metadata", "list"},
)
def list_datasets(
    project_id: Optional[str] = None,
    page_size: Annotated[int, Field(gt=0, le=1000)] = 100,
    page_token: Optional[str] = None,
    location: Optional[str] = None,
) -> dict:
    """Returns a paginated list of datasets for the given project.
    If project_id is None, uses the server's default project.
    """
```

- Maps to: `Client.list_datasets(project=..., page_size=..., page_token=...)`
- Response shape:
```json
{
  "items": [
    {
      "dataset_fqid": "my-project.my_dataset",
      "project_id": "my-project",
      "dataset_id": "my_dataset",
      "location": "US",
      "labels": {"env": "dev"},
      "created": "2025-09-30T12:34:56Z",
      "modified": "2025-09-30T12:34:56Z"
    }
  ],
  "next_page_token": null
}
```

---

### Tool: get_dataset_info

```python
@mcp.tool(
    description="Get metadata for a BigQuery dataset",
    tags={"bigquery", "metadata"},
)
def get_dataset_info(
    dataset_fqid: Annotated[str, Field(pattern=r"^[\w-]+\.[\w$]+$")],
) -> dict:
    """Returns detailed metadata for a dataset (project.dataset)."""
```

- Maps to: `Client.get_dataset(bigquery.DatasetReference.from_string(dataset_fqid))`
- Response shape: metadata including location, description, labels, access, defaults, timestamps

---

### Tool: list_tables

```python
@mcp.tool(
    description="List tables within a dataset",
    tags={"bigquery", "metadata", "list"},
)
def list_tables(
    dataset_fqid: Annotated[str, Field(pattern=r"^[\w-]+\.[\w$]+$")],
    page_size: Annotated[int, Field(gt=0, le=1000)] = 100,
    page_token: Optional[str] = None,
) -> dict:
    """Returns tables and views in the dataset."""
```

- Maps to: `Client.list_tables(bigquery.DatasetReference.from_string(dataset_fqid), ...)`
- Response shape:
```json
{
  "items": [
    {
      "table_fqid": "my-project.my_dataset.my_table",
      "project_id": "my-project",
      "dataset_id": "my_dataset",
      "table_id": "my_table",
      "type": "TABLE",
      "partitioning": {"type": "DAY", "field": "event_date"},
      "clustering": ["user_id", "country"],
      "location": "US"
    }
  ],
  "next_page_token": null
}
```

---

### Tool: get_table_info

```python
@mcp.tool(
    description="Get metadata and schema for a table",
    tags={"bigquery", "metadata"},
)
def get_table_info(
    table_fqid: Annotated[str, Field(pattern=r"^[\w-]+\.[\w$]+\.[\w$]+$")],
) -> dict:
    """Returns table metadata including schema, partitioning, clustering, sizes."""
```

- Maps to: `Client.get_table(bigquery.TableReference.from_string(table_fqid))`
- Response shape includes: schema fields, num_rows, num_bytes, partitioning, clustering, labels, timestamps

---

### Tool: execute_query

```python
from typing import Mapping
from pydantic import BaseModel

class QueryParams(BaseModel):
    # Simple named parameters (positional and arrays can be added later)
    values: Mapping[str, object] = {}

@mcp.tool(
    description="Execute a SQL query in BigQuery and return rows (paginated)",
    tags={"bigquery", "query"},
)
def execute_query(
    sql: Annotated[str, Field(min_length=1)],
    parameters: Optional[QueryParams] = None,
    location: Optional[str] = None,
    use_legacy_sql: bool = False,
    dry_run: bool = False,
    maximum_bytes_billed: Optional[int] = None,
    timeout_ms: Annotated[int, Field(gt=0, le=10_0000_000)] = 60_000,
    page_size: Annotated[int, Field(gt=0, le=100_000)] = 1000,
    page_token: Optional[str] = None,
) -> dict:
    """Runs the query and returns: job_id, schema, total_rows, rows[], next_page_token, statistics."""
```

- Maps to: `Client.query(sql, job_config=QueryJobConfig(...), location=...)` then `QueryJob.result(page_size=..., timeout=timeout_ms/1000)`
- Row conversion: iterate `RowIterator` to JSON; advanced conversions available (`to_dataframe`, `to_arrow`) if needed later.
- Response example:
```json
{
  "job_id": "<job-id>",
  "location": "US",
  "schema": [{"name": "name", "type": "STRING", "mode": "NULLABLE"}],
  "total_rows": 10,
  "rows": [{"name": "Alice"}, {"name": "Bob"}],
  "next_page_token": null,
  "statistics": {"total_bytes_processed": 123456, "total_slot_ms": 789}
}
```

---

### Errors (MCP Tool Results)
- Validation errors are handled by FastMCP based on annotations (`Field`, types, Pydantic models).
- Translate BigQuery exceptions to MCP error results with meaningful messages and codes:
  - notFound → 404
  - accessDenied → 403
  - invalid → 400
  - backendError → 502
  - timeout → 408
- Include `reason`, `location`, and BigQuery `errors` array when available.

---

### Authentication
- A bearer token is required for all tool invocations. Implement using a FastMCP authentication hook or a decorator that checks the token before executing each tool.
- On failure, return a tool error with 401 and a short message.

---

### Notes and Future Enhancements
- Add parameterized queries with typed `ScalarQueryParameter` and arrays/structs.
- Optional BigQuery Storage API for faster reads (`to_arrow`/`bqstorage_client`).
- Streaming results via iterables (`to_arrow_iterable`, `to_dataframe_iterable`).
- Dataset/table allowlists, per-token access controls.
