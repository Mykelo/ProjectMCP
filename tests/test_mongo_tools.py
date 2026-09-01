"""Tool-layer tests for Mongo MCP tools (JWT verifier mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import mcp_bigquery.auth as auth_mod
from mcp_bigquery.mongo_client import MongoClientError

auth_mod.create_jwt_verifier = lambda public_key_path=None: MagicMock()  # type: ignore

from mcp_bigquery.server import (  # noqa: E402
    count_mongo_documents,
    find_mongo_documents,
    get_mongo_collection_info,
    list_mongo_collections,
)


def test_list_mongo_collections_tool_maps_not_configured() -> None:
    with patch(
        "mcp_bigquery.server.get_mongo_client",
        side_effect=MongoClientError(
            "Mongo is not configured: set MONGO_SSH_HOST",
            code="MONGO_NOT_CONFIGURED",
        ),
    ):
        result = list_mongo_collections.fn(database=None)
    assert result["error"]["code"] == "MONGO_NOT_CONFIGURED"
    assert "MONGO_SSH_HOST" in result["error"]["message"]


def test_find_mongo_documents_tool_returns_client_result() -> None:
    client = MagicMock()
    client.find_documents.return_value = {
        "database": "prelisting",
        "collection": "supplier_items",
        "documents": [{"asin": "B001"}],
        "returned": 1,
    }
    with patch("mcp_bigquery.server.get_mongo_client", return_value=client):
        result = find_mongo_documents.fn(
            collection="supplier_items",
            filter={"asin": "B001"},
            projection=None,
            sort=None,
            skip=0,
            limit=100,
            database=None,
        )
    assert result["returned"] == 1
    client.find_documents.assert_called_once()


def test_count_and_info_tools_delegate() -> None:
    client = MagicMock()
    client.count_documents.return_value = {
        "count": 3,
        "database": "prelisting",
        "collection": "suppliers",
    }
    client.get_collection_info.return_value = {
        "collection": "suppliers",
        "estimated_count": 3,
    }
    with patch("mcp_bigquery.server.get_mongo_client", return_value=client):
        assert count_mongo_documents.fn(
            collection="suppliers",
            filter=None,
            database=None,
        )["count"] == 3
        assert get_mongo_collection_info.fn(
            collection="suppliers",
            database=None,
            sample_size=20,
        )["estimated_count"] == 3
