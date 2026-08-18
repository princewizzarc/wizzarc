from __future__ import annotations
from core.app_paths import DATA_DIR

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import re
import uuid


# =========================================================
# CONSTANTS
# =========================================================

TEMP_HISTORY_TTL = timedelta(days=1)

DEFAULT_DATA_DIR = DATA_DIR

TEMP_HISTORY_FILE = (
    DEFAULT_DATA_DIR
    / "temporary_history.json"
)

PERMANENT_MEMORY_FILE = (
    DEFAULT_DATA_DIR
    / "permanent_memory.json"
)


# =========================================================
# MODELS
# =========================================================

@dataclass
class TemporaryHistoryItem:
    id: str
    role: str
    content: str
    created_at: str
    metadata: Dict[str, Any]


@dataclass
class PermanentMemoryItem:
    id: str
    key: str
    value: str
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]


# =========================================================
# HELPERS
# =========================================================

def utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


def iso_now() -> str:
    return utc_now().isoformat()


def parse_iso(value: str) -> Optional[datetime]:
    try:
        parsed = datetime.fromisoformat(
            str(value)
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed

    except Exception:
        return None


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


def load_json_list(path: Path) -> List[dict]:
    ensure_parent(path)

    if not path.exists():
        return []

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(
            data,
            list
        ):
            return data

    except Exception:
        pass

    return []


def save_json_list(
    path: Path,
    items: List[dict]
) -> None:

    ensure_parent(path)

    path.write_text(
        json.dumps(
            items,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


# =========================================================
# MEMORY MANAGER
# =========================================================

class MemoryManager:

    def __init__(
        self,
        temporary_path: Path = TEMP_HISTORY_FILE,
        permanent_path: Path = PERMANENT_MEMORY_FILE,
        temp_ttl: timedelta = TEMP_HISTORY_TTL,
    ):
        self.temporary_path = Path(
            temporary_path
        )

        self.permanent_path = Path(
            permanent_path
        )

        self.temp_ttl = temp_ttl

        self.cleanup_temporary_history()

    # =====================================================
    # TEMPORARY HISTORY
    # =====================================================

    def add_temporary(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TemporaryHistoryItem:

        role = str(role).strip().lower()
        content = str(content).strip()

        if not content:
            raise ValueError(
                "Temporary history content cannot be empty."
            )

        item = TemporaryHistoryItem(
            id=str(
                uuid.uuid4()
            ),
            role=role or "unknown",
            content=content,
            created_at=iso_now(),
            metadata=metadata or {},
        )

        items = load_json_list(
            self.temporary_path
        )

        items.append(
            asdict(item)
        )

        save_json_list(
            self.temporary_path,
            items
        )

        return item

    def get_temporary(
        self,
        limit: Optional[int] = None,
    ) -> List[TemporaryHistoryItem]:

        self.cleanup_temporary_history()

        items = [
            TemporaryHistoryItem(
                id=str(
                    item.get(
                        "id",
                        ""
                    )
                ),
                role=str(
                    item.get(
                        "role",
                        "unknown"
                    )
                ),
                content=str(
                    item.get(
                        "content",
                        ""
                    )
                ),
                created_at=str(
                    item.get(
                        "created_at",
                        ""
                    )
                ),
                metadata=(
                    item.get(
                        "metadata",
                        {}
                    )
                    if isinstance(
                        item.get(
                            "metadata",
                            {}
                        ),
                        dict
                    )
                    else {}
                ),
            )
            for item in load_json_list(
                self.temporary_path
            )
        ]

        if (
            limit is not None
            and
            limit >= 0
        ):
            return items[
                -limit:
            ]

        return items

    def cleanup_temporary_history(
        self
    ) -> int:

        items = load_json_list(
            self.temporary_path
        )

        now = utc_now()
        kept = []

        for item in items:

            created_at = parse_iso(
                item.get(
                    "created_at",
                    ""
                )
            )

            if created_at is None:
                continue

            if (
                now
                - created_at
                <= self.temp_ttl
            ):
                kept.append(
                    item
                )

        removed = (
            len(items)
            - len(kept)
        )

        if (
            removed
            or
            items != kept
        ):
            save_json_list(
                self.temporary_path,
                kept
            )

        return removed

    def clear_temporary(
        self
    ) -> int:

        items = load_json_list(
            self.temporary_path
        )

        count = len(
            items
        )

        save_json_list(
            self.temporary_path,
            []
        )

        return count

    # =====================================================
    # PERMANENT MEMORY
    # =====================================================

    def remember(
        self,
        key: str,
        value: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PermanentMemoryItem:

        key = str(key).strip()
        value = str(value).strip()

        if not key:
            raise ValueError(
                "Memory key cannot be empty."
            )

        if not value:
            raise ValueError(
                "Memory value cannot be empty."
            )

        items = load_json_list(
            self.permanent_path
        )

        normalized_key = (
            key.lower()
        )

        now = iso_now()

        for item in items:

            if (
                str(
                    item.get(
                        "key",
                        ""
                    )
                )
                .strip()
                .lower()
                == normalized_key
            ):
                item[
                    "value"
                ] = value

                item[
                    "updated_at"
                ] = now

                if metadata is not None:
                    item[
                        "metadata"
                    ] = metadata

                save_json_list(
                    self.permanent_path,
                    items
                )

                return PermanentMemoryItem(
                    id=str(
                        item.get(
                            "id",
                            ""
                        )
                    ),
                    key=str(
                        item.get(
                            "key",
                            key
                        )
                    ),
                    value=value,
                    created_at=str(
                        item.get(
                            "created_at",
                            now
                        )
                    ),
                    updated_at=now,
                    metadata=(
                        item.get(
                            "metadata",
                            {}
                        )
                        if isinstance(
                            item.get(
                                "metadata",
                                {}
                            ),
                            dict
                        )
                        else {}
                    ),
                )

        item = PermanentMemoryItem(
            id=str(
                uuid.uuid4()
            ),
            key=key,
            value=value,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )

        items.append(
            asdict(item)
        )

        save_json_list(
            self.permanent_path,
            items
        )

        return item

    def list_memories(
        self
    ) -> List[PermanentMemoryItem]:

        return [
            PermanentMemoryItem(
                id=str(
                    item.get(
                        "id",
                        ""
                    )
                ),
                key=str(
                    item.get(
                        "key",
                        ""
                    )
                ),
                value=str(
                    item.get(
                        "value",
                        ""
                    )
                ),
                created_at=str(
                    item.get(
                        "created_at",
                        ""
                    )
                ),
                updated_at=str(
                    item.get(
                        "updated_at",
                        ""
                    )
                ),
                metadata=(
                    item.get(
                        "metadata",
                        {}
                    )
                    if isinstance(
                        item.get(
                            "metadata",
                            {}
                        ),
                        dict
                    )
                    else {}
                ),
            )
            for item in load_json_list(
                self.permanent_path
            )
        ]

    def forget(
        self,
        key: str
    ) -> bool:

        key = str(key).strip().lower()

        if not key:
            return False

        items = load_json_list(
            self.permanent_path
        )

        kept = [
            item
            for item in items
            if (
                str(
                    item.get(
                        "key",
                        ""
                    )
                )
                .strip()
                .lower()
                != key
            )
        ]

        removed = (
            len(kept)
            != len(items)
        )

        if removed:
            save_json_list(
                self.permanent_path,
                kept
            )

        return removed

    def get_memory(
        self,
        key: str
    ) -> Optional[PermanentMemoryItem]:

        key = str(key).strip().lower()

        for item in self.list_memories():

            if (
                item.key
                .strip()
                .lower()
                == key
            ):
                return item

        return None


    # =====================================================
    # RELEVANT PERMANENT MEMORY
    # =====================================================

    def find_relevant_memories(
        self,
        query: str,
        limit: int = 5,
    ) -> List[PermanentMemoryItem]:

        query = str(
            query
        ).lower().strip()

        if not query:
            return []

        # Small stop-word list keeps matching lightweight
        # without requiring embeddings or another AI call.
        stop_words = {
            "a", "an", "the", "is", "are", "am",
            "i", "me", "my", "mine", "you", "your",
            "do", "does", "did", "what", "which",
            "who", "where", "when", "why", "how",
            "to", "of", "for", "in", "on", "at",
            "and", "or", "that", "this", "it",
            "prefer", "preferred",
        }

        query_words = {
            word
            for word in re.findall(
                r"[a-z0-9]+",
                query
            )
            if (
                len(word) > 1
                and
                word not in stop_words
            )
        }

        scored = []

        for memory in self.list_memories():

            key_text = (
                memory.key
                .lower()
                .strip()
            )

            value_text = (
                memory.value
                .lower()
                .strip()
            )

            key_words = set(
                re.findall(
                    r"[a-z0-9]+",
                    key_text
                )
            )

            value_words = set(
                re.findall(
                    r"[a-z0-9]+",
                    value_text
                )
            )

            score = 0

            # Full key phrase match is strongest.
            if (
                key_text
                and
                key_text in query
            ):
                score += 10

            # Key-word overlap matters more than value overlap.
            score += (
                len(
                    query_words
                    & key_words
                )
                * 4
            )

            score += (
                len(
                    query_words
                    & value_words
                )
                * 2
            )

            if score > 0:
                scored.append(
                    (
                        score,
                        memory.updated_at,
                        memory,
                    )
                )

        scored.sort(
            key=lambda item: (
                item[0],
                item[1],
            ),
            reverse=True,
        )

        return [
            item[2]
            for item in scored[
                :max(
                    0,
                    limit
                )
            ]
        ]

    def build_relevant_permanent_context(
        self,
        query: str,
        limit: int = 5,
    ) -> str:

        memories = (
            self.find_relevant_memories(
                query=query,
                limit=limit,
            )
        )

        if not memories:
            return ""

        lines = [
            "RELEVANT SAVED USER MEMORIES:"
        ]

        for item in memories:
            lines.append(
                f"- {item.key}: {item.value}"
            )

        return "\n".join(
            lines
        )

    # =====================================================
    # CONTEXT BUILDING
    # =====================================================

    def build_recent_context(
        self,
        limit: int = 8,
    ) -> str:

        items = self.get_temporary(
            limit=limit
        )

        if not items:
            return ""

        lines = [
            "RECENT CONVERSATION CONTEXT:"
        ]

        for item in items:

            role = (
                item.role
                .strip()
                .capitalize()
            )

            lines.append(
                f"{role}: {item.content}"
            )

        return "\n".join(
            lines
        )

    def build_permanent_context(
        self,
        limit: int = 20,
    ) -> str:

        memories = self.list_memories()

        if not memories:
            return ""

        lines = [
            "SAVED USER MEMORIES:"
        ]

        for item in memories[
            -limit:
        ]:
            lines.append(
                f"- {item.key}: {item.value}"
            )

        return "\n".join(
            lines
        )


MEMORY_MANAGER = MemoryManager()
