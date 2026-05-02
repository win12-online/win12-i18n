"""Click CLI 命令定义."""

from pathlib import Path

import click

from .exceptions import I18NError
from .manager import I18NManager
from .models import PropertiesFile


@click.group()
@click.option(
    "--project",
    "-p",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="项目根目录",
)
@click.option(
    "--dir",
    "-d",
    default="i18n",
    help="i18n 目录名（相对于项目根目录）",
)
@click.pass_context
def cli(ctx: click.Context, project: Path, dir: str) -> None:
    """Windows 12 i18n 管理工具."""
    ctx.ensure_object(dict)
    ctx.obj["project"] = project
    ctx.obj["i18n_dir"] = dir
    ctx.obj["manager"] = I18NManager(project, i18n_dir=dir)


@cli.command()
@click.pass_context
def init(ctx: click.Context) -> None:
    """初始化 i18n 目录."""
    project: Path = ctx.obj["project"]
    i18n_dir_name: str = ctx.obj["i18n_dir"]
    i18n_dir = project / i18n_dir_name
    i18n_dir.mkdir(exist_ok=True)
    sample = i18n_dir / "zh.properties"
    if not sample.exists():
        sample.write_text(
            "# Windows 12 中文翻译\n\n# 示例键\nexample.key=示例值\n",
            encoding="utf-8",
        )
    click.echo(f"已初始化 i18n 目录: {i18n_dir}")


@cli.command()
@click.argument("key")
@click.argument("value")
@click.option("--lang", "-l", required=True, help="语言代码")
@click.pass_context
def add(ctx: click.Context, key: str, value: str, lang: str) -> None:
    """添加或更新翻译键值."""
    manager: I18NManager = ctx.obj["manager"]
    if lang not in manager.files:
        manager.i18n_path.mkdir(parents=True, exist_ok=True)
        pf = PropertiesFile(manager.i18n_path / f"{lang}.properties")
        manager.files[lang] = pf
    pf = manager.files[lang]
    pf.set(key, value)
    pf.save()
    click.echo(f"已更新 [{lang}] {key} = {value}")


@cli.command()
@click.argument("key")
@click.pass_context
def remove(ctx: click.Context, key: str) -> None:
    """从所有语言文件移除 key."""
    manager: I18NManager = ctx.obj["manager"]
    found = False
    for lang, pf in manager.files.items():
        if key in pf.entries:
            pf.remove(key)
            pf.save()
            click.echo(f"已从 [{lang}] 移除 {key}")
            found = True
    if not found:
        click.secho("key 不存在于任何语言文件。", fg="red")


@cli.command()
@click.option("--base", "-b", default="zh", help="基准语言")
@click.pass_context
def check(ctx: click.Context, base: str) -> None:
    """检查各语言文件 key 一致性."""
    manager: I18NManager = ctx.obj["manager"]
    try:
        result = manager.check(base)
    except I18NError as e:
        click.secho(f"错误: {e}", fg="red")
        return
    has_issue = False
    for lang, issues in result.items():
        missing = issues["missing"]
        extra = issues["extra"]
        if missing or extra:
            has_issue = True
            click.secho(f"[{lang}]", fg="yellow")
            for k in missing:
                click.echo(f"  缺失: {k}")
            for k in extra:
                click.echo(f"  多余: {k}")
    if not has_issue:
        click.echo("所有语言文件 key 一致。")


@cli.command()
@click.option("--base", "-b", default="zh", help="基准语言")
@click.pass_context
def sync(ctx: click.Context, base: str) -> None:
    """同步 key 到所有语言文件."""
    manager: I18NManager = ctx.obj["manager"]
    try:
        actions = manager.sync(base)
    except I18NError as e:
        click.secho(f"错误: {e}", fg="red")
        return
    if not actions:
        click.echo("无需同步。")
        return
    for a in actions:
        click.echo(a)


@cli.command()
@click.argument("key")
@click.pass_context
def show(ctx: click.Context, key: str) -> None:
    """查看 key 在各语言中的值."""
    manager: I18NManager = ctx.obj["manager"]
    result = manager.show(key)
    found = False
    for lang, val in result.items():
        if val is not None:
            found = True
            click.echo(f"[{lang}] {val}")
    if not found:
        click.secho("key 不存在于任何语言文件。", fg="red")


def main() -> None:
    try:
        cli()
    except I18NError as e:
        click.secho(f"错误: {e}", fg="red")
        raise click.ClickException(str(e)) from e
