"""Read-only MongoDB client wrapper for MCP tools."""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from bson import ObjectId
from bson.json_util import RELAXED_JSON_OPTIONS
from bson.json_util import dumps as bson_dumps
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from mcp_bigquery.config import get_settings

logger = logging.getLogger(__name__)

_OID_RE = re.compile(r"^[0-9a-fA-F]{24}$")
_FORBIDDEN_OPERATORS = frozenset({"$where", "$function", "$accumulator"})
_MAX_FIND_LIMIT = 1000
_DEFAULT_FIND_LIMIT = 100

KNOWN_COLLECTION_DESCRIPTIONS: dict[str, str] = {
    "supplier_items": "Supplier catalog items (ASINs, costs, tiers)",
    "suppliers": "Supplier/brand records (including keepaSync)",
    "master_nokeepa": "OMS master items",
    "purchasingLog": "Purchasing log entries",
    "purchasingLogGroups": "Purchasing log groups",
    "potracker": "Purchase order tracker",
    "potracker_archive": "Archived purchase order tracker rows",
    "aptracker": "Accounts payable tracker",
    "freight_log": "Freight log",
    "freight_log_itemized": "Itemized freight log",
    "current_shipment_log": "Current inbound shipment log",
    "invoices": "AP invoices",
    "ledger": "AP ledger",
    "asinmapping": "SKU/ASIN mapping",
    "asinmapping_external": "External SKU/ASIN mapping",
    "action_logs": "OMS action logs",
    "events": "Supplier/brand events",
    "mapped_tasks": "Mapped tasks",
}


class MongoClientError(Exception):
    """Raised when a Mongo tool operation fails."""

    def __init__(self, message: str, code: str = "MONGO_ERROR") -> None:
        super().__init__(message)
        self.code = code


class MongoQueryClient:
    """Read-only wrapper around a synchronous PyMongo client."""

    def __init__(self, pymongo_client: Any | None = None) -> None:
        settings = get_settings()
        self._settings = settings
        if pymongo_client is not None:
            self._client = pymongo_client
            return
        uri = (settings.mongo_uri or "").strip()
        if not uri:
            raise MongoClientError(
                "Mongo is not configured: set MONGO_URI",
                code="MONGO_NOT_CONFIGURED",
            )
        try:
            self._client = MongoClient(uri)
        except Exception as exc:
            logger.error("Failed to initialize Mongo client: %s", exc)
            raise MongoClientError(f"Failed to initialize Mongo client: {exc}") from exc

    def list_collections(self, database: str | None = None) -> dict[str, Any]:
        db_name = self._resolve_database(database)
        try:
            names = self._client[db_name].list_collection_names()
        except PyMongoError as exc:
            raise MongoClientError(f"Failed to list collections: {exc}") from exc
        collections = [
            {
                "name": name,
                "description": KNOWN_COLLECTION_DESCRIPTIONS.get(name),
            }
            for name in names
        ]
        return {"database": db_name, "collections": collections}

    def get_collection_info(
        self,
        collection: str,
        database: str | None = None,
        sample_size: int = 20,
    ) -> dict[str, Any]:
        db_name = self._resolve_database(database)
        coll_name = self._validate_collection(collection)
        sample_size = max(1, min(sample_size, 100))
        coll = self._client[db_name][coll_name]
        timeout = self._settings.mongo_query_timeout_ms
        try:
            estimated_count = coll.estimated_document_count()
            index_info = coll.index_information()
            sample = list(coll.find({}, limit=sample_size, max_time_ms=timeout))
        except PyMongoError as exc:
            raise MongoClientError(f"Failed to get collection info: {exc}") from exc
        return {
            "database": db_name,
            "collection": coll_name,
            "estimated_count": estimated_count,
            "indexes": _format_indexes(index_info),
            "inferred_fields": _infer_fields(sample),
        }

    def find_documents(
        self,
        collection: str,
        filter: Mapping[str, Any] | None = None,
        projection: Mapping[str, Any] | None = None,
        sort: Mapping[str, int] | list[Any] | None = None,
        skip: int = 0,
        limit: int = _DEFAULT_FIND_LIMIT,
        database: str | None = None,
    ) -> dict[str, Any]:
        db_name = self._resolve_database(database)
        coll_name = self._validate_collection(collection)
        query = coerce_filter(dict(filter or {}))
        limit = max(1, min(limit, _MAX_FIND_LIMIT))
        skip = max(0, skip)
        timeout = self._settings.mongo_query_timeout_ms
        find_kwargs: dict[str, Any] = {
            "filter": query,
            "skip": skip,
            "limit": limit,
            "max_time_ms": timeout,
        }
        if projection:
            find_kwargs["projection"] = dict(projection)
        sort_spec = _normalize_sort(sort)
        if sort_spec:
            find_kwargs["sort"] = sort_spec
        try:
            cursor = self._client[db_name][coll_name].find(**find_kwargs)
            documents = [document_to_jsonable(doc) for doc in cursor]
        except PyMongoError as exc:
            raise MongoClientError(f"Failed to find documents: {exc}") from exc
        return {
            "database": db_name,
            "collection": coll_name,
            "documents": documents,
            "returned": len(documents),
        }

    def count_documents(
        self,
        collection: str,
        filter: Mapping[str, Any] | None = None,
        database: str | None = None,
    ) -> dict[str, Any]:
        db_name = self._resolve_database(database)
        coll_name = self._validate_collection(collection)
        query = coerce_filter(dict(filter or {}))
        timeout = self._settings.mongo_query_timeout_ms
        try:
            count = self._client[db_name][coll_name].count_documents(
                query,
                maxTimeMS=timeout,
            )
        except PyMongoError as exc:
            raise MongoClientError(f"Failed to count documents: {exc}") from exc
        return {"database": db_name, "collection": coll_name, "count": count}

    def _resolve_database(self, database: str | None) -> str:
        name = (database or self._settings.mongo_default_database).strip()
        allowed = tuple(self._settings.allowed_mongo_databases)
        if name not in allowed:
            raise MongoClientError(
                f"Database '{name}' is not allowlisted. Allowed: {', '.join(allowed)}",
                code="DATABASE_NOT_ALLOWED",
            )
        return name

    def _validate_collection(self, collection: str) -> str:
        name = (collection or "").strip()
        if not name or name.startswith("system.") or "$" in name:
            raise MongoClientError(
                f"Invalid collection name: {collection!r}",
                code="INVALID_COLLECTION",
            )
        return name


def coerce_filter(value: Any, key: str | None = None) -> Any:
    """Reject unsafe operators and coerce hex / $oid values to ObjectId."""
    if isinstance(value, dict):
        for operator in value:
            if operator in _FORBIDDEN_OPERATORS:
                raise MongoClientError(
                    f"Filter operator {operator} is not allowed",
                    code="UNSAFE_FILTER",
                )
        if set(value.keys()) == {"$oid"} and isinstance(value.get("$oid"), str):
            return ObjectId(value["$oid"])
        return {k: coerce_filter(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [coerce_filter(item, key) for item in value]
    if key == "_id" and isinstance(value, str) and _OID_RE.fullmatch(value):
        return ObjectId(value)
    return value


def document_to_jsonable(value: Any) -> Any:
    """Convert BSON values to JSON-friendly Python types."""
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        iso = value.isoformat()
        if value.tzinfo is not None:
            return iso.replace("+00:00", "Z")
        return iso
    if isinstance(value, dict):
        return {str(k): document_to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [document_to_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return json.loads(bson_dumps(value, json_options=RELAXED_JSON_OPTIONS))


def _normalize_sort(
    sort: Mapping[str, int] | list[Any] | None,
) -> list[tuple[str, int]] | None:
    if not sort:
        return None
    if isinstance(sort, Mapping):
        return [(key, int(direction)) for key, direction in sort.items()]
    normalized: list[tuple[str, int]] = []
    for item in sort:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            normalized.append((str(item[0]), int(item[1])))
        else:
            raise MongoClientError(
                "sort must be an object of field:direction or a list of [field, direction]",
                code="INVALID_SORT",
            )
    return normalized


def _format_indexes(index_info: Mapping[str, Any]) -> list[dict[str, Any]]:
    indexes = []
    for name, spec in index_info.items():
        keys = spec.get("key", []) if isinstance(spec, Mapping) else []
        indexes.append({"name": name, "keys": list(keys)})
    return indexes


def _infer_fields(sample: list[Any]) -> list[dict[str, str]]:
    types_by_name: dict[str, str] = {}
    for doc in sample:
        if not isinstance(doc, dict):
            continue
        for name, value in doc.items():
            types_by_name.setdefault(name, _bson_type_name(value))
    return [{"name": name, "type": types_by_name[name]} for name in sorted(types_by_name)]


def _bson_type_name(value: Any) -> str:
    if isinstance(value, ObjectId):
        return "objectId"
    if isinstance(value, datetime):
        return "date"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "double"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if value is None:
        return "null"
    return type(value).__name__


_client: MongoQueryClient | None = None


def get_mongo_client() -> MongoQueryClient:
    """Get or create the global Mongo query client."""
    global _client
    if _client is None:
        _client = MongoQueryClient()
    return _client
