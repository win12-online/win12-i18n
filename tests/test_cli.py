"""CLI 集成测试."""

from pathlib import Path

from click.testing import CliRunner

from win12_i18n.cli import cli


class TestCLI:
    def test_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Windows 12 i18n 管理工具" in result.output

    def test_init(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["-p", str(tmp_path), "init"])
        assert result.exit_code == 0
        assert (tmp_path / "i18n" / "zh.properties").exists()

    def test_add_and_show(self, tmp_path: Path) -> None:
        runner = CliRunner()
        # init
        runner.invoke(cli, ["-p", str(tmp_path), "init"])
        # add
        result = runner.invoke(
            cli, ["-p", str(tmp_path), "add", "test.key", "测试", "-l", "zh"]
        )
        assert result.exit_code == 0
        assert "已更新 [zh] test.key = 测试" in result.output
        # show
        result = runner.invoke(cli, ["-p", str(tmp_path), "show", "test.key"])
        assert result.exit_code == 0
        assert "[zh] 测试" in result.output

    def test_remove(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["-p", str(tmp_path), "init"])
        runner.invoke(cli, ["-p", str(tmp_path), "add", "k", "v", "-l", "zh"])
        result = runner.invoke(cli, ["-p", str(tmp_path), "remove", "k"])
        assert result.exit_code == 0
        assert "已从 [zh] 移除 k" in result.output

    def test_check_and_sync(self, tmp_path: Path) -> None:
        runner = CliRunner()
        i18n = tmp_path / "i18n"
        i18n.mkdir()
        (i18n / "zh.properties").write_text("a=1\n", encoding="utf-8")
        (i18n / "en.properties").write_text("b=2\n", encoding="utf-8")
        # check
        result = runner.invoke(cli, ["-p", str(tmp_path), "check", "-b", "zh"])
        assert result.exit_code == 0
        assert "缺失: a" in result.output or "缺失" in result.output
        # sync
        result = runner.invoke(cli, ["-p", str(tmp_path), "sync", "-b", "zh"])
        assert result.exit_code == 0
        assert "添加 [en] a" in result.output
        assert "删除 [en] b" in result.output

    def test_remove_not_found(self, tmp_path: Path) -> None:
        runner = CliRunner()
        runner.invoke(cli, ["-p", str(tmp_path), "init"])
        result = runner.invoke(cli, ["-p", str(tmp_path), "remove", "missing"])
        assert result.exit_code == 0
        assert "key 不存在于任何语言文件" in result.output
