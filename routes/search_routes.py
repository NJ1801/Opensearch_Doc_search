from fastapi import APIRouter, HTTPException
from datetime import datetime, date
from models.search_models import SearchInput
from opensearch_client.client import get_client
from config.settings import OPENSEARCH_INDEX
from utils.response import success_response

router = APIRouter()


# ---------------------------
# Helpers
# ---------------------------
def parse_date_safe(d: str | None):
    if not d:
        return None
    try:
        return datetime.fromisoformat(d)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format: {d}. Expected YYYY-MM-DD"
        )


def parse_keywords(raw: str) -> list[str]:
    """
    Split keywords by comma or whitespace.
    Remove empty tokens safely.
    """
    if not raw or not raw.strip():
        raise HTTPException(400, "keyword cannot be empty")

    parts = raw.replace(",", " ").split()
    keywords = [p.lower().strip() for p in parts if p.strip()]

    if not keywords:
        raise HTTPException(400, "No valid keywords provided")

    return keywords


# ---------------------------
# Search Endpoint
# ---------------------------
@router.post("/search")
def search(payload: SearchInput):
    client = get_client()

    # ---------------------------
    # Validate pagination
    # ---------------------------
    if payload.from_ < 0 or payload.size <= 0:
        raise HTTPException(400, "from_ must be >= 0 and size must be > 0")

    if payload.from_ + payload.size > 10000:
        raise HTTPException(
            400,
            "from_ + size must be <= 10000 (OpenSearch limit). Use pagination or scroll."
        )

    # ---------------------------
    # Validate dates
    # ---------------------------
    date_from = parse_date_safe(payload.date_from)
    date_to = parse_date_safe(payload.date_to)

    today = datetime.combine(date.today(), datetime.min.time())

    if date_from and date_to and date_from > date_to:
        raise HTTPException(400, "date_from cannot be after date_to")

    if date_to and date_to > today:
        raise HTTPException(400, "date_to cannot be in the future")

    # ---------------------------
    # Keyword parsing
    # ---------------------------
    keywords = parse_keywords(payload.keyword)

    # ---------------------------
    # Build keyword queries (SAFE)
    # ---------------------------
    should_queries = []

    if payload.search_mode == "filename":
        for kw in keywords:
            should_queries.append({
                "match_phrase_prefix": {
                    "filename": {
                        "query": kw
                    }
                }
            })

    else:
        for kw in keywords:
            should_queries.append({
                "match": {
                    "content": {
                        "query": kw
                    }
                }
            })

    if not should_queries:
        raise HTTPException(400, "No valid search terms generated")

    must = [{
        "bool": {
            "should": should_queries,
            "minimum_should_match": 1
        }
    }]

    # ---------------------------
    # Filters
    # ---------------------------
    filters = []

    # File type filter
    if payload.file_types and "all" not in payload.file_types:
        filters.append({
            "terms": {
                "filetype": [ft.lower() for ft in payload.file_types]
            }
        })

    # Date range filter
    if date_from or date_to:
        range_q = {}
        if date_from:
            range_q["gte"] = date_from.isoformat()
        if date_to:
            range_q["lte"] = date_to.isoformat()

        filters.append({
            "range": {
                "modified": range_q
            }
        })

    # Size filter (KB → bytes)
    if payload.size_from is not None or payload.size_to is not None:
        size_range = {}
        if payload.size_from is not None:
            size_range["gte"] = int(payload.size_from * 1024)
        if payload.size_to is not None:
            size_range["lte"] = int(payload.size_to * 1024)

        filters.append({"range": {"size_bytes": size_range}})

    # ---------------------------
    # Final OpenSearch query
    # ---------------------------
    query = {
        "_source": {
            "excludes": ["content"]   # hide full content
        },
        "query": {
            "bool": {
                "must": must,
                "filter": filters
            }
        },
        "highlight": {
            "fields": {
                "content": {
                    "fragment_size": 150,
                    "number_of_fragments": 1
                },
                "filename": {
                    "fragment_size": 150,
                    "number_of_fragments": 1
                }
            }
        },
        "from": payload.from_,
        "size": payload.size
    }

    # ---------------------------
    # Execute search
    # ---------------------------
    try:
        res = client.search(index=OPENSEARCH_INDEX, body=query)
    except Exception as e:
        raise HTTPException(500, f"Search execution failed: {str(e)}")

    # ---------------------------
    # Format response
    # ---------------------------
    results = []
    for hit in res["hits"]["hits"]:
        src = hit["_source"]

        snippet = (
            hit.get("highlight", {}).get("content")
            or hit.get("highlight", {}).get("filename")
            or []
        )

        results.append({
            "path": src.get("path"),
            "filename": src.get("filename"),
            "filetype": src.get("filetype"),
            "modified": src.get("modified"),
            "size_bytes": src.get("size_bytes"),
            "snippet": snippet
        })

    return success_response(
        "Search completed",
        {
            "count": len(results),
            "results": results
        }
    )
