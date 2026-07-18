from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    items: List[Any]
    total: int
    skip: int
    limit: int


def _orm_to_dict(obj):
    if hasattr(obj, "__dict__"):
        d = {}
        for k, v in obj.__dict__.items():
            if k.startswith("_"):
                continue
            if hasattr(v, "__dict__") and not isinstance(v, (str, int, float, bool, type(None), list, dict)):
                continue
            d[k] = v
        return d
    return obj


def paginate_query(query, skip: int = 0, limit: int = 50):
    total = query.count()
    rows = query.offset(skip).limit(limit).all()
    items = [_orm_to_dict(r) for r in rows]
    return items, total
