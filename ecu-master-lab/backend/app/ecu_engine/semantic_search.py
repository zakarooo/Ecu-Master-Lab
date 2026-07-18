"""
PHASE 5 — Semantic Search with pgvector (fallback to keyword search).

Provides vector embeddings for map names, descriptions, and categories.
If pgvector is not available on Neon, falls back to trigram keyword matching.
"""

from __future__ import annotations

import hashlib
import logging
import math
import re
from typing import Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger("ecu_engine.semantic")

# Try to import pgvector; fallback gracefully
try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False


def _text_to_embedding(text_str: str, dim: int = 128) -> List[float]:
    """
    Deterministic text→embedding using feature hashing (SimHash-like).
    No external model required. Produces stable 128-dim vectors.
    """
    tokens = re.findall(r'[a-z0-9]{2,}', text_str.lower())
    vec = [0.0] * dim
    for token in tokens:
        h = int(hashlib.md5(token.encode()).hexdigest(), 16)
        for i in range(dim):
            bit = (h >> i) & 1
            vec[i] += 1.0 if bit else -1.0
    # L2 normalize
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class SemanticSearchEngine:
    """Semantic search for maps with pgvector or keyword fallback."""

    def __init__(self, session: Session):
        self.session = session
        self._has_pgvector = False
        self._check_pgvector()

    def _check_pgvector(self):
        """Check if pgvector extension is available."""
        try:
            self.session.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'"))
            row = self.session.execute(text(
                "SELECT 1 FROM pg_extension WHERE extname = 'vector'"
            )).fetchone()
            self._has_pgvector = row is not None
            if self._has_pgvector:
                logger.info("pgvector extension detected")
        except Exception:
            self._has_pgvector = False
            logger.info("pgvector not available, using keyword fallback")

    def ensure_vector_column(self):
        """Add embedding column to known_maps if pgvector available."""
        if not self._has_pgvector:
            return
        try:
            self.session.execute(text("""
                ALTER TABLE known_maps
                ADD COLUMN IF NOT EXISTS embedding vector(128)
            """))
            self.session.commit()
        except Exception:
            self.session.rollback()

    def compute_embeddings(self, batch_size: int = 500):
        """Compute embeddings for all maps (pgvector mode)."""
        if not self._has_pgvector:
            logger.info("Skipping embeddings (no pgvector)")
            return

        rows = self.session.execute(text("""
            SELECT id, map_name, category, ecu_model_name
            FROM known_maps
            WHERE embedding IS NULL
            LIMIT :limit
        """), {"limit": batch_size}).fetchall()

        if not rows:
            return

        updated = 0
        for row in rows:
            map_id, name, category, ecu = row
            text_str = f"{name or ''} {category or ''} {ecu or ''}"
            embedding = _text_to_embedding(text_str)
            embedding_str = "[%s]" % ",".join(str(x) for x in embedding)
            try:
                self.session.execute(text("""
                    UPDATE known_maps SET embedding = :emb::vector WHERE id = :id
                """), {"emb": embedding_str, "id": map_id})
                updated += 1
            except Exception:
                self.session.rollback()
                continue

        self.session.commit()
        logger.info("Computed embeddings for %d maps", updated)

    def search(
        self,
        query: str,
        ecu_filter: str = None,
        category_filter: str = None,
        limit: int = 20,
    ) -> List[dict]:
        """Search for maps matching query."""
        if self._has_pgvector:
            return self._search_vector(query, ecu_filter, category_filter, limit)
        return self._search_keyword(query, ecu_filter, category_filter, limit)

    def _search_vector(
        self,
        query: str,
        ecu_filter: Optional[str],
        category_filter: Optional[str],
        limit: int,
    ) -> List[dict]:
        """Vector similarity search using pgvector."""
        embedding = _text_to_embedding(query)
        emb_str = "[%s]" % ",".join(str(x) for x in embedding)

        where_clauses = ["embedding IS NOT NULL"]
        params: dict = {"emb": emb_str, "limit": limit}

        if ecu_filter:
            where_clauses.append("ecu_model_name LIKE :ecu")
            params["ecu"] = "%" + ecu_filter + "%"
        if category_filter:
            where_clauses.append("category LIKE :cat")
            params["cat"] = "%" + category_filter + "%"

        where_sql = " AND ".join(where_clauses)

        rows = self.session.execute(text(f"""
            SELECT
                id, map_name, category, ecu_model_name, offset_hex,
                offset_dec, size_bytes,
                1 - (embedding <=> :emb::vector) as similarity
            FROM known_maps
            WHERE {where_sql}
            ORDER BY embedding <=> :emb::vector
            LIMIT :limit
        """), params).fetchall()

        return [
            {
                "id": r[0], "name": r[1], "category": r[2],
                "ecu_model": r[3], "offset_hex": r[4],
                "offset_dec": r[5], "size_bytes": r[6],
                "similarity": round(float(r[7]), 4),
            }
            for r in rows
        ]

    def _search_keyword(
        self,
        query: str,
        ecu_filter: Optional[str],
        category_filter: Optional[str],
        limit: int,
    ) -> List[dict]:
        """Keyword-based fallback search."""
        tokens = [t.lower() for t in re.findall(r'[a-z0-9]{2,}', query.lower())]
        if not tokens:
            return []

        # Build ILIKE conditions for each token
        token_conditions = []
        params: dict = {}
        for i, token in enumerate(tokens):
            key = "t%d" % i
            token_conditions.append(
                "(LOWER(map_name) LIKE :%s OR LOWER(category) LIKE :%s OR LOWER(ecu_model_name) LIKE :%s)" % (key, key, key)
            )
            params[key] = "%" + token + "%"

        where_parts = [" OR ".join(token_conditions)]

        if ecu_filter:
            where_parts.append("LOWER(ecu_model_name) LIKE :ecu")
            params["ecu"] = "%" + ecu_filter.lower() + "%"
        if category_filter:
            where_parts.append("LOWER(category) LIKE :cat")
            params["cat"] = "%" + category_filter.lower() + "%"

        where_sql = " AND ".join(where_parts)
        params["limit"] = limit

        rows = self.session.execute(text(f"""
            SELECT
                id, map_name, category, ecu_model_name, offset_hex,
                offset_dec, size_bytes
            FROM known_maps
            WHERE {where_sql}
            ORDER BY map_name
            LIMIT :limit
        """), params).fetchall()

        results = []
        for r in rows:
            # Simple relevance score based on token coverage
            name_lower = (r[1] or "").lower()
            cat_lower = (r[2] or "").lower()
            ecu_lower = (r[3] or "").lower()
            combined = name_lower + " " + cat_lower + " " + ecu_lower
            hits = sum(1 for t in tokens if t in combined)
            score = hits / max(1, len(tokens))

            results.append({
                "id": r[0], "name": r[1], "category": r[2],
                "ecu_model": r[3], "offset_hex": r[4],
                "offset_dec": r[5], "size_bytes": r[6],
                "similarity": round(score, 4),
            })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results

    def get_statistics(self) -> dict:
        """Get knowledge base statistics."""
        try:
            stats = {}
            stats["total_maps"] = self.session.execute(
                text("SELECT COUNT(*) FROM known_maps")).scalar() or 0
            stats["total_axes"] = self.session.execute(
                text("SELECT COUNT(*) FROM map_axes")).scalar() or 0
            stats["total_strings"] = self.session.execute(
                text("SELECT COUNT(*) FROM known_strings")).scalar() or 0
            stats["total_checksums"] = self.session.execute(
                text("SELECT COUNT(*) FROM known_checksums")).scalar() or 0
            stats["total_segments"] = self.session.execute(
                text("SELECT COUNT(*) FROM known_segments")).scalar() or 0
            stats["total_ecu_models"] = self.session.execute(
                text("SELECT COUNT(DISTINCT ecu_model_name) FROM known_maps")).scalar() or 0
            stats["total_categories"] = self.session.execute(
                text("SELECT COUNT(DISTINCT category) FROM known_maps")).scalar() or 0
            stats["pgvector_available"] = self._has_pgvector

            if self._has_pgvector:
                stats["maps_with_embeddings"] = self.session.execute(
                    text("SELECT COUNT(*) FROM known_maps WHERE embedding IS NOT NULL")).scalar() or 0

            # Top categories
            cats = self.session.execute(text("""
                SELECT category, COUNT(*) as cnt
                FROM known_maps
                GROUP BY category
                ORDER BY cnt DESC
                LIMIT 10
            """)).fetchall()
            stats["top_categories"] = [{"name": r[0], "count": r[1]} for r in cats]

            # Top ECUs
            ecus = self.session.execute(text("""
                SELECT ecu_model_name, COUNT(*) as cnt
                FROM known_maps
                GROUP BY ecu_model_name
                ORDER BY cnt DESC
                LIMIT 10
            """)).fetchall()
            stats["top_ecus"] = [{"name": r[0], "count": r[1]} for r in ecus]

            return stats
        except Exception as exc:
            logger.error("Failed to get statistics: %s", exc)
            return {"error": str(exc)}
