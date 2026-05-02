"""核心数据模型：PropertyEntry 与 PropertiesFile."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Union

from .exceptions import FileError, KeyNotFoundError


@dataclass
class PropertyEntry:
    """单条属性条目."""

    key: str
    value: str
    raw_lines: list[str]
    line_no: int


@dataclass
class CommentItem:
    """注释项."""

    kind: str = "comment"
    text: str = ""


@dataclass
class BlankItem:
    """空行项."""

    kind: str = "blank"


@dataclass
class EntryItem:
    """属性条目项."""

    kind: str = "entry"
    entry: PropertyEntry = field(default_factory=lambda: PropertyEntry("", "", [], 0))


Item = Union[CommentItem, BlankItem, EntryItem]


class PropertiesFile:
    """.properties 文件解析器，保留原始结构与注释."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.items: list[Item] = []
        self.entries: dict[str, PropertyEntry] = {}
        self.modified = False
        if path.exists():
            self._load()

    def _load(self) -> None:
        from . import parser

        try:
            content = self.path.read_text(encoding="utf-8")
        except OSError as e:
            raise FileError(f"无法读取文件 {self.path}: {e}") from e
        self.items, self.entries = parser.parse_properties(content)
        self.modified = False

    def get(self, key: str) -> PropertyEntry | None:
        """获取指定 key 的条目."""
        return self.entries.get(key)

    def set(self, key: str, value: str) -> None:
        """添加或更新 key."""
        from . import parser

        if key in self.entries:
            entry = self.entries[key]
            entry.value = value
            entry.raw_lines = parser.build_entry_lines(key, value)
            for item in self.items:
                if isinstance(item, EntryItem) and item.entry.key == key:
                    item.entry = entry
                    break
        else:
            entry = PropertyEntry(
                key=key,
                value=value,
                raw_lines=parser.build_entry_lines(key, value),
                line_no=0,
            )
            self.entries[key] = entry
            self.items.append(EntryItem(entry=entry))
        self.modified = True

    def remove(self, key: str) -> None:
        """移除指定 key."""
        if key not in self.entries:
            raise KeyNotFoundError(f"key 不存在: {key}")
        del self.entries[key]
        self.items = [
            item
            for item in self.items
            if not (isinstance(item, EntryItem) and item.entry.key == key)
        ]
        self.modified = True

    def save(self) -> None:
        """写回文件，保留结构与注释."""
        from . import parser

        try:
            text = parser.serialize_items(self.items)
            self.path.write_text(text, encoding="utf-8")
        except OSError as e:
            raise FileError(f"无法写入文件 {self.path}: {e}") from e
        self.modified = False
