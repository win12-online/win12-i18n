"""管理逻辑单元测试."""

from pathlib import Path

import pytest

from win12_i18n.exceptions import FileError
from win12_i18n.manager import I18NManager


class TestI18NManager:
    def test_load_files(self, tmp_path: Path) -> None:
        i18n = tmp_path / "i18n"
        i18n.mkdir()
        (i18n / "zh.properties").write_text("k=1\n", encoding="utf-8")
        (i18n / "en.properties").write_text("k=2\n", encoding="utf-8")
        mgr = I18NManager(tmp_path)
        assert sorted(mgr.languages()) == ["en", "zh"]

    def test_check_missing_and_extra(self, tmp_path: Path) -> None:
        i18n = tmp_path / "i18n"
        i18n.mkdir()
        (i18n / "zh.properties").write_text("a=1\nb=2\n", encoding="utf-8")
        (i18n / "en.properties").write_text("a=1\nc=3\n", encoding="utf-8")
        mgr = I18NManager(tmp_path)
        result = mgr.check("zh")
        assert result["en"]["missing"] == ["b"]
        assert result["en"]["extra"] == ["c"]

    def test_check_base_not_found(self, tmp_path: Path) -> None:
        i18n = tmp_path / "i18n"
        i18n.mkdir()
        mgr = I18NManager(tmp_path)
        with pytest.raises(FileError):
            mgr.check("zh")

    def test_sync_add_and_remove(self, tmp_path: Path) -> None:
        i18n = tmp_path / "i18n"
        i18n.mkdir()
        (i18n / "zh.properties").write_text("a=1\nb=2\n", encoding="utf-8")
        (i18n / "en.properties").write_text("a=1\nc=3\n", encoding="utf-8")
        mgr = I18NManager(tmp_path)
        actions = mgr.sync("zh")
        assert any("添加 [en] b" in a for a in actions)
        assert any("删除 [en] c" in a for a in actions)
        en_content = (i18n / "en.properties").read_text(encoding="utf-8")
        assert "b=" in en_content
        assert "c" not in en_content

    def test_show(self, tmp_path: Path) -> None:
        i18n = tmp_path / "i18n"
        i18n.mkdir()
        (i18n / "zh.properties").write_text("k=你好\n", encoding="utf-8")
        (i18n / "en.properties").write_text("k=hello\n", encoding="utf-8")
        mgr = I18NManager(tmp_path)
        result = mgr.show("k")
        assert result["zh"] == "你好"
        assert result["en"] == "hello"

    def test_show_not_found(self, tmp_path: Path) -> None:
        i18n = tmp_path / "i18n"
        i18n.mkdir()
        (i18n / "zh.properties").write_text("k=1\n", encoding="utf-8")
        mgr = I18NManager(tmp_path)
        result = mgr.show("missing")
        assert result["zh"] is None
