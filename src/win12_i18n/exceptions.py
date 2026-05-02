"""自定义异常类."""


class I18NError(Exception):
    """i18n 工具基类异常."""

    pass


class ParseError(I18NError):
    """.properties 文件解析失败."""

    pass


class KeyNotFoundError(I18NError):
    """指定的 key 不存在."""

    pass


class FileError(I18NError):
    """文件读写错误."""

    pass
