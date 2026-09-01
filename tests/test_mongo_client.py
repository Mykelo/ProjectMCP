"""Unit tests for the read-only Mongo wrapper (no live Mongo)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import Mock, patch

import pytest
from bson import ObjectId

from mcp_bigquery.mongo_client import MongoClientError, MongoQueryClient


class FakeCursor:
    def __init__(self, docs: list[dict[str, Any]]) -> None:
        self._docs = docs

    def __iter__(self):
        return iter(self._docs)


class FakeCollection:
    def __init__(self, docs: list[dict[str, Any]] | None = None) -> None:
        self._docs = list(docs or [])
        self.last_find: dict[str, Any] | None = None
        self.last_count: dict[str, Any] | None = None
        self.indexes: dict[str, Any] = {"_id_": {"v": 2, "key": [("_id", 1)]}}

    def find(
        self,
        filter: dict[str, Any] | None = None,
        projection: dict[str, Any] | None = None,
        sort: list[tuple[str, int]] | None = None,
        skip: int = 0,
        limit: int = 0,
        max_time_ms: int | None = None,
    ) -> FakeCursor:
        filt = filter or {}
        self.last_find = {
            "filter": filt,
            "projection": projection,
            "sort": sort,
            "skip": skip,
            "limit": limit,
            "max_time_ms": max_time_ms,
        }
        matched = [doc for doc in self._docs if _matches(doc, filt)]
        if skip:
            matched = matched[skip:]
        if limit:
            matched = matched[:limit]
        if projection:
            matched = [_project(doc, projection) for doc in matched]
        return FakeCursor(matched)

    def count_documents(
        self,
        filter: dict[str, Any] | None = None,
        maxTimeMS: int | None = None,
    ) -> int:
        filt = filter or {}
        self.last_count = {"filter": filt, "maxTimeMS": maxTimeMS}
        return sum(1 for doc in self._docs if _matches(doc, filt))

    def estimated_document_count(self) -> int:
        return len(self._docs)

    def index_information(self) -> dict[str, Any]:
        return self.indexes


class FakeDatabase:
    def __init__(self, collections: dict[str, FakeCollection]) -> None:
        self._collections = collections

    def list_collection_names(self) -> list[str]:
        return list(self._collections)

    def __getitem__(self, name: str) -> FakeCollection:
        if name not in self._collections:
            self._collections[name] = FakeCollection()
        return self._collections[name]


class FakePyMongoClient:
    def __init__(self, databases: dict[str, FakeDatabase]) -> None:
        self._databases = databases

    def __getitem__(self, name: str) -> FakeDatabase:
        if name not in self._databases:
            self._databases[name] = FakeDatabase({})
        return self._databases[name]


def _matches(doc: dict[str, Any], filt: dict[str, Any]) -> bool:
    if not filt:
        return True
    for key, value in filt.items():
        if key.startswith("$"):
            continue
        if doc.get(key) != value:
            return False
    return True


def _project(doc: dict[str, Any], projection: dict[str, Any]) -> dict[str, Any]:
    include = {k: v for k, v in projection.items() if k != "_id" and v}
    keep_id = projection.get("_id", 1)
    if include:
        out = {k: doc[k] for k in include if k in doc}
        if keep_id and "_id" in doc:
            out["_id"] = doc["_id"]
        return out
    out = dict(doc)
    if not keep_id:
        out.pop("_id", None)
    for key, value in projection.items():
        if key != "_id" and not value:
            out.pop(key, None)
    return out


def _settings(**overrides: Any) -> Mock:
    settings = Mock()
    settings.mongo_uri = "mongodb://localhost:27017"
    settings.mongo_default_database = "prelisting"
    settings.allowed_mongo_databases = ("prelisting",)
    settings.mongo_query_timeout_ms = 30_000
    for key, value in overrides.items():
        setattr(settings, key, value)
    return settings


def _client(
    collections: dict[str, FakeCollection] | None = None,
    settings: Mock | None = None,
    database: str = "prelisting",
) -> tuple[MongoQueryClient, FakeDatabase]:
    db = FakeDatabase(collections or {})
    pymongo_client = FakePyMongoClient({database: db})
    with patch("mcp_bigquery.mongo_client.get_settings", return_value=settings or _settings()):
        return MongoQueryClient(pymongo_client=pymongo_client), db


def test_missing_uri_raises_not_configured() -> None:
    settings = _settings(mongo_uri=None)
    with patch("mcp_bigquery.mongo_client.get_settings", return_value=settings):
        with pytest.raises(MongoClientError) as exc_info:
            MongoQueryClient()
    assert exc_info.value.code == "MONGO_NOT_CONFIGURED"
    assert "MONGO_URI" in str(exc_info.value)


def test_allowlist_rejects_other_database() -> None:
    client, _ = _client()
    with pytest.raises(MongoClientError) as exc_info:
        client.list_collections(database="warehouse")
    assert exc_info.value.code == "DATABASE_NOT_ALLOWED"


def test_rejects_system_and_dollar_collection_names() -> None:
    client, _ = _client()
    with pytest.raises(MongoClientError) as exc_info:
        client.find_documents(collection="system.users")
    assert exc_info.value.code == "INVALID_COLLECTION"
    with pytest.raises(MongoClientError) as exc_info:
        client.find_documents(collection="foo$bar")
    assert exc_info.value.code == "INVALID_COLLECTION"


def test_rejects_where_in_filter() -> None:
    client, _ = _client({"supplier_items": FakeCollection([{"asin": "B00"}])})
    with pytest.raises(MongoClientError) as exc_info:
        client.find_documents(
            collection="supplier_items",
            filter={"$where": "this.asin === 'B00'"},
        )
    assert exc_info.value.code == "UNSAFE_FILTER"


def test_find_applies_filter_projection_limit_and_serializes_objectid() -> None:
    oid = ObjectId()
    other = ObjectId()
    created = datetime(2024, 1, 15, 12, 0, tzinfo=UTC)
    collection = FakeCollection(
        [
            {"_id": oid, "asin": "B001", "brand": "Acme", "created": created},
            {"_id": other, "asin": "B002", "brand": "Other"},
        ]
    )
    client, _ = _client({"supplier_items": collection})

    result = client.find_documents(
        collection="supplier_items",
        filter={"asin": "B001"},
        projection={"asin": 1, "created": 1},
        limit=1,
    )

    assert collection.last_find is not None
    assert collection.last_find["limit"] == 1
    assert collection.last_find["filter"]["asin"] == "B001"
    assert len(result["documents"]) == 1
    doc = result["documents"][0]
    assert doc["_id"] == str(oid)
    assert doc["asin"] == "B001"
    assert isinstance(doc["created"], str)
    assert "brand" not in doc


def test_count_returns_integer_from_collection() -> None:
    collection = FakeCollection(
        [
            {"asin": "B001", "brand": "Acme"},
            {"asin": "B002", "brand": "Acme"},
            {"asin": "B003", "brand": "Other"},
        ]
    )
    client, _ = _client({"supplier_items": collection})
    result = client.count_documents(collection="supplier_items", filter={"brand": "Acme"})
    assert result["count"] == 2
    assert result["database"] == "prelisting"
    assert result["collection"] == "supplier_items"
    assert collection.last_count is not None
    assert collection.last_count["maxTimeMS"] == 30_000


def test_list_collections_attaches_known_descriptions() -> None:
    client, _ = _client(
        {
            "supplier_items": FakeCollection(),
            "mystery_col": FakeCollection(),
        }
    )
    result = client.list_collections()
    by_name = {item["name"]: item["description"] for item in result["collections"]}
    assert "supplier catalog" in (by_name["supplier_items"] or "").lower()
    assert by_name["mystery_col"] is None
    assert result["database"] == "prelisting"


def test_get_collection_info_includes_indexes_and_inferred_fields() -> None:
    oid = ObjectId()
    collection = FakeCollection([{"_id": oid, "asin": "B001", "cost": 12.5}])
    collection.indexes = {
        "_id_": {"v": 2, "key": [("_id", 1)]},
        "asin_1": {"v": 2, "key": [("asin", 1)]},
    }
    client, _ = _client({"supplier_items": collection})
    result = client.get_collection_info("supplier_items")
    assert result["collection"] == "supplier_items"
    assert result["estimated_count"] == 1
    index_names = {item["name"] for item in result["indexes"]}
    assert index_names == {"_id_", "asin_1"}
    field_names = {item["name"] for item in result["inferred_fields"]}
    assert {"_id", "asin", "cost"} <= field_names


def test_nested_function_operator_is_rejected() -> None:
    client, _ = _client({"supplier_items": FakeCollection()})
    with pytest.raises(MongoClientError) as exc_info:
        client.find_documents(
            collection="supplier_items",
            filter={"$or": [{"asin": "B001"}, {"$function": {"body": "1"}}]},
        )
    assert exc_info.value.code == "UNSAFE_FILTER"


def test_hex_string_id_is_coerced_to_objectid() -> None:
    oid = ObjectId()
    collection = FakeCollection([{"_id": oid, "asin": "B001"}])
    client, _ = _client({"supplier_items": collection})
    client.find_documents(collection="supplier_items", filter={"_id": str(oid)})
    assert collection.last_find is not None
    assert collection.last_find["filter"]["_id"] == oid
