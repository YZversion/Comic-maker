# Comic Maker

Comic Maker 是一个把小说章节转换成漫画生产中间产物的流水线工具。

当前流水线：

`章节输入 -> 自动切分 -> 镜头规划 -> 上下文补全 -> 出图 -> 人工审核/重试 -> 拼页 -> 导出`

## Features

- 章节切分：把输入文本拆成 `Beat` 列表
- 镜头规划：为每个 `Beat` 生成 `ShotPlan`
- Prompt 组装：基于角色/场景/动作生成分镜 prompt
- 出图 Provider：支持 `mock`、`siliconflow`、`liblib`（默认 `liblib`）
- 审核与重试：支持失败后重试，且已修复“重试导致格数增加”
- 拼页与导出：生成 `page_manifest` 并导出章节包

## LLM Backend

当前版本仅支持 **DeepSeek**。

- `DEEPSEEK_API_KEY` 必填
- `LLM_MODEL` 默认 `deepseek-chat`

## Requirements

- Python `>=3.11`
- 推荐使用虚拟环境

## Quick Start

### 1) Install

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

pip install -e .
```

### 2) Configure `.env`

复制 `.env.example` 为 `.env` 并填写密钥。

关键配置：

- `DEEPSEEK_API_KEY`
- `IMAGE_PROVIDER`（默认 `liblib`）
- `LIBLIB_ACCESS_KEY`
- `LIBLIB_SECRET_KEY`
- `LIBLIB_TEMPLATE_UUID`（可选）

### 3) Run Tests

单元/回归测试：

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

烟雾测试：

```bash
python -m comic_maker.test_run
```

说明：烟雾测试会强制使用 `mock` 出图，避免真实 API 成本与网络波动。

### 4) Run Pipeline

```bash
python -m comic_maker.main
```

安装后也可使用命令：

```bash
comic-maker
```

## Input / Output

输入：

- 章节 ID（如 `ch01`）
- 章节正文（输入完成后单独一行输入 `END`）

运行数据目录：

- `comic_maker/data/`
- `comic_maker/output/`

主要产物：

- `comic_maker/data/panel_manifest.json`
- `comic_maker/output/pages/page_manifest.json`
- `comic_maker/output/exports/<chapter_id>/`
- `comic_maker/output/logs/run.log`

## Project Layout

```text
Comic-maker/
├── comic_maker/
│   ├── main.py
│   ├── config.py
│   ├── test_run.py
│   ├── core/
│   ├── providers/
│   ├── prompts/
│   ├── data/
│   └── output/
├── tests/
├── pyproject.toml
├── .env.example
└── README.md
```

## Security Checklist (Before Git Push)

1. `.env` 不要提交（已在 `.gitignore`）
2. 提交前检查暂存区：

```powershell
git diff --cached | Select-String -Pattern 'sk-|AIza|API_KEY|SECRET|TOKEN|Bearer'
```

无输出再 push。

## Troubleshooting

### Windows 中文/编码显示异常

```powershell
$env:PYTHONUTF8='1'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
```

### `ModuleNotFoundError`

优先使用模块方式运行：

```bash
python -m comic_maker.main
```
