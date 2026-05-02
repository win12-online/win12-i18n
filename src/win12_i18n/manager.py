"""多语言文件管理逻辑."""

from pathlib import Path

from .exceptions import FileError
from .models import PropertiesFile


class I18NManager:
    """管理项目中的多语言 .properties 文件."""

    def __init__(self, project_path: Path, i18n_dir: str = "i18n") -> None:
        self.project_path = project_path
        self.i18n_path = project_path / i18n_dir
        self.files: dict[str, PropertiesFile] = {}
        self._load_files()

    def _load_files(self) -> None:
        if not self.i18n_path.exists():
            return
        for f in sorted(self.i18n_path.glob("*.properties")):
            lang = f.stem
            self.files[lang] = PropertiesFile(f)

    def languages(self) -> list[str]:
        return list(self.files.keys())

    def check(self, base: str) -> dict[str, dict[str, list[str]]]:
        """检查各语言文件与基准语言的差异.

        返回 {lang: {"missing": [...], "extra": [...]}}
        """
        if base not in self.files:
            raise FileError(f"基准语言文件不存在: {base}.properties")
        base_keys = set(self.files[base].entries.keys())
        result: dict[str, dict[str, list[str]]] = {}
        for lang, pf in self.files.items():
            if lang == base:
                continue
            keys = set(pf.entries.keys())
            result[lang] = {
                "missing": sorted(base_keys - keys),
                "extra": sorted(keys - base_keys),
            }
        return result

    def sync(self, base: str) -> list[str]:
        """以基准语言同步 key 到其他语言.

        缺失的 key 以空值添加，多余的 key 被删除.
        返回操作日志列表.
        """
        if base not in self.files:
            raise FileError(f"基准语言文件不存在: {base}.properties")
        base_keys = set(self.files[base].entries.keys())
        actions: list[str] = []
        for lang, pf in self.files.items():
            if lang == base:
                continue
            for key in sorted(base_keys - set(pf.entries.keys())):
                pf.set(key, "")
                actions.append(f"添加 [{lang}] {key}")
            for key in sorted(set(pf.entries.keys()) - base_keys):
                pf.remove(key)
                actions.append(f"删除 [{lang}] {key}")
            pf.save()
        return actions

    def show(self, key: str) -> dict[str, str | None]:
        """查看 key 在各语言中的值."""
        result: dict[str, str | None] = {}
        for lang, pf in self.files.items():
            entry = pf.get(key)
            result[lang] = entry.value if entry else None
        return result
