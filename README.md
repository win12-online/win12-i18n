# win12-i18n
[![PyPI](https://img.shields.io/badge/PyPI-win12%20i18n-blue
)](https://pypi.org/project/win12-i18n/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/license/MIT)
<a href="https://github.com/win12-online/win12-i18n/actions/workflows/lint.yml">
    <img src="https://github.com/win12-online/win12-i18n/actions/workflows/lint.yml/badge.svg?branch=main&event=push" alt="pyright">
  </a>

Windows 12 网页版 i18n 管理 CLI 工具。

用于统一管理 `.properties` 格式的多语言资源文件，支持解析、校验、同步等操作。

## 安装

```bash
# 使用 uv（推荐）
uv pip install win12-i18n

# 或使用 pip
pip install win12-i18n
```

## 使用

```bash
# 查看帮助
win12-i18n --help

# 初始化 i18n 目录
win12-i18n init

# 添加翻译键值
win12-i18n add setting.psnl.color "深色模式" -l zh

# 检查各语言文件一致性
win12-i18n check

# 同步键值到所有语言文件
win12-i18n sync -b zh

# 查看某个键在各语言中的值
win12-i18n show setting.psnl.color
```

## 开发

```bash
# 克隆仓库
git clone https://github.com/win12-online/win12-i18n.git
cd win12-i18n

# 安装开发依赖
uv venv
uv pip install -e ".[dev]"

# 运行测试
uv run pytest
```

## 依赖

- Python >= 3.10
- Click >= 8.0

## 开源许可

本项目采用 [MIT](LICENSE) 开源许可证。

## 免责声明

* 本项目仅供学习交流使用，不得用于商业用途，如有侵权请联系删除
* 用户使用本项目所产生的任何后果，需自行承担风险
* 开发者不对使用本项目产生的任何直接或间接损失负责