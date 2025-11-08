from typing import Any, Dict, List
from .table import Table
from Common.base import entry

DEFAULT_TABLE = "main"

def get(key: str, table: str = DEFAULT_TABLE) -> Any:
    return Table.of(table).get(key, None)

def set(key: str, value: Any, table: str = DEFAULT_TABLE) -> bool:
    return Table.of(table).set(key, value)

def exists(key: str, table: str = DEFAULT_TABLE) -> bool:
    return Table.of(table).get(key, None) is not None

def delete(key: str, table: str = DEFAULT_TABLE) -> bool:
    t = Table.of(table)
    if hasattr(t, "inner") and key in t.inner:
        del t.inner[key]
        t.sync()
        return True
    return False

def list_keys(table: str = DEFAULT_TABLE) -> List[str]:
    t = Table.of(table)
    return list(t.inner.keys()) if hasattr(t, "inner") else []

def set_text(key: str, text: str, table: str = DEFAULT_TABLE) -> bool:
    from datetime import datetime
    return set(key, entry(viewtype="text", value={"text": str(text), "lastSavedTime": datetime.now()}), table)


