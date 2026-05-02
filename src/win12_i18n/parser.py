""".properties 解析与序列化."""

from .exceptions import ParseError
from .models import BlankItem, CommentItem, EntryItem, Item, PropertyEntry


def parse_properties(content: str) -> tuple[list[Item], dict[str, PropertyEntry]]:
    """解析 .properties 内容.

    保留注释、空行、多行值与 key 顺序.
    """
    lines = content.splitlines()
    items: list[Item] = []
    entries: dict[str, PropertyEntry] = {}
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if stripped == "":
            items.append(BlankItem())
            i += 1
            continue

        if stripped.startswith("#"):
            items.append(CommentItem(text=line))
            i += 1
            continue

        if "=" not in line:
            raise ParseError(f"第 {i + 1} 行缺少 '=' 分隔符: {line!r}")

        key, sep, first_value = line.partition("=")
        key = key.strip()
        raw_lines = [line]
        value_parts = [first_value]
        i += 1

        # 多行值：key 行以 = 结尾（即 first_value 为空）
        if first_value == "":
            while i < n:
                next_line = lines[i]
                next_stripped = next_line.strip()

                if next_stripped == "":
                    raw_lines.append(next_line)
                    value_parts.append(next_line)
                    i += 1
                    continue

                if next_stripped.startswith("#"):
                    raw_lines.append(next_line)
                    value_parts.append(next_line)
                    i += 1
                    continue

                # 若下一行包含 = 且不是注释/空行，则视为下一个 key
                if "=" in next_line:
                    break

                raw_lines.append(next_line)
                value_parts.append(next_line)
                i += 1

        value = "\n".join(value_parts)
        line_no = i - len(raw_lines) + 1
        entry = PropertyEntry(
            key=key, value=value, raw_lines=raw_lines, line_no=line_no
        )
        items.append(EntryItem(entry=entry))
        entries[key] = entry

    return items, entries


def build_entry_lines(key: str, value: str) -> list[str]:
    """根据 key/value 构建 raw_lines."""
    if "\n" in value:
        return [f"{key}="] + value.split("\n")
    return [f"{key}={value}"]


def serialize_items(items: list[Item]) -> str:
    """将 items 序列化为文件内容."""
    lines: list[str] = []
    for item in items:
        match item:
            case CommentItem(text=t):
                lines.append(t)
            case BlankItem():
                lines.append("")
            case EntryItem(entry=e):
                lines.extend(e.raw_lines)
    return "\n".join(lines) + "\n"
