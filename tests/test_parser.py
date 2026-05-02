"""解析器单元测试."""

from pathlib import Path

import pytest

from win12_i18n.exceptions import ParseError
from win12_i18n.models import BlankItem, CommentItem, EntryItem, PropertiesFile
from win12_i18n.parser import build_entry_lines, parse_properties, serialize_items


class TestParseProperties:
    def test_basic_key_value(self) -> None:
        content = "name= value"
        items, entries = parse_properties(content)
        assert len(items) == 1
        assert isinstance(items[0], EntryItem)
        assert entries["name"].value == " value"
        assert entries["name"].line_no == 1

    def test_multiline_value(self) -> None:
        content = "desc=\n第一行\n第二行\nother=ok"
        items, entries = parse_properties(content)
        assert len(items) == 2
        assert entries["desc"].value == "\n第一行\n第二行"
        assert entries["desc"].raw_lines == ["desc=", "第一行", "第二行"]
        assert entries["other"].value == "ok"

    def test_multiline_with_comment_and_blank(self) -> None:
        content = "desc=\n第一行\n# 注释\n\nother=ok"
        items, entries = parse_properties(content)
        assert entries["desc"].value == "\n第一行\n# 注释\n"
        assert entries["desc"].raw_lines == ["desc=", "第一行", "# 注释", ""]

    def test_comment_and_blank(self) -> None:
        content = "# header\n\nkey=val"
        items, entries = parse_properties(content)
        assert isinstance(items[0], CommentItem)
        assert items[0].text == "# header"
        assert isinstance(items[1], BlankItem)
        assert isinstance(items[2], EntryItem)

    def test_missing_equal_raises(self) -> None:
        with pytest.raises(ParseError):
            parse_properties("badline")

    def test_empty_value_not_multiline(self) -> None:
        content = "key=\nother=1"
        items, entries = parse_properties(content)
        # key= 后面紧跟 other=1，中间没有额外行
        # 但根据规则，key= 表示多行值开始，所以 "other=1" 不是 value 的一部分
        # 因为 "other=1" 包含 =，所以被识别为下一个 key
        assert entries["key"].value == ""
        assert entries["key"].raw_lines == ["key="]


class TestSerializeItems:
    def test_roundtrip(self, tmp_path: Path) -> None:
        original = "# h\n\nkey=val\n"
        items, entries = parse_properties(original)
        serialized = serialize_items(items)
        assert serialized == original

    def test_multiline_roundtrip(self) -> None:
        original = "key=\nline1\nline2\n"
        items, entries = parse_properties(original)
        serialized = serialize_items(items)
        assert serialized == original


class TestBuildEntryLines:
    def test_single_line(self) -> None:
        assert build_entry_lines("k", "v") == ["k=v"]

    def test_multi_line(self) -> None:
        assert build_entry_lines("k", "a\nb") == ["k=", "a", "b"]


class TestPropertiesFile:
    def test_load_and_save(self, tmp_path: Path) -> None:
        f = tmp_path / "test.properties"
        f.write_text("# c\n\nkey=val\n", encoding="utf-8")
        pf = PropertiesFile(f)
        assert pf.get("key").value == "val"
        pf.save()
        assert f.read_text(encoding="utf-8") == "# c\n\nkey=val\n"

    def test_set_new_key(self, tmp_path: Path) -> None:
        f = tmp_path / "test.properties"
        f.write_text("k1=v1\n", encoding="utf-8")
        pf = PropertiesFile(f)
        pf.set("k2", "v2")
        pf.save()
        assert "k2=v2" in f.read_text(encoding="utf-8")

    def test_set_existing_key(self, tmp_path: Path) -> None:
        f = tmp_path / "test.properties"
        f.write_text("k1=v1\n", encoding="utf-8")
        pf = PropertiesFile(f)
        pf.set("k1", "new")
        pf.save()
        content = f.read_text(encoding="utf-8")
        assert "k1=new" in content
        assert "k1=v1" not in content

    def test_remove_key(self, tmp_path: Path) -> None:
        f = tmp_path / "test.properties"
        f.write_text("k1=v1\nk2=v2\n", encoding="utf-8")
        pf = PropertiesFile(f)
        pf.remove("k1")
        pf.save()
        content = f.read_text(encoding="utf-8")
        assert "k1" not in content
        assert "k2=v2" in content

    def test_key_order_preserved(self, tmp_path: Path) -> None:
        f = tmp_path / "test.properties"
        f.write_text("a=1\nb=2\nc=3\n", encoding="utf-8")
        pf = PropertiesFile(f)
        pf.save()
        lines = f.read_text(encoding="utf-8").splitlines()
        assert lines[0] == "a=1"
        assert lines[1] == "b=2"
        assert lines[2] == "c=3"
