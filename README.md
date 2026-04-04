# Comic Maker

Comic Maker 是一个把小说章节转成漫画生产中间产物的流水线工具。

当前流水线：

`章节输入 -> 自动切分 -> 镜头规划 -> 上下文补全 -> 出图 -> 人工审核/重试 -> 拼页 -> 导出`

## Features

- 章节切分：把输入文本拆成 `Beat` 列表
- 镜头规划：为每个 `Beat` 生成 `ShotPlan`
- Prompt 组装：基于角色/场景/动作信息生成分镜 prompt
- 出图 Provider：支持 `siliconflow`、`liblib`
- 审核与重试：支持失败后重试，并已修复“重试导致格数增加”问题
- 拼页与导出：生成 `page_manifest` 并导出章节包

## Project Status

项目已可跑通端到端流程，适合继续迭代。

当前已知限制：

- 跨 panel 人物一致性仍需增强（目前主要依赖 prompt）
- 多 provider 的参数还需要进一步调优（seed/参考图/一致性控制）

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

复制 `.env.example` 为 `.env`，填写你要使用的服务密钥。

最常用配置项：

- `LLM_BACKEND`: `anthropic` | `gemini` | `deepseek`
- `LLM_MODEL`
- `IMAGE_PROVIDER`: `mock` | `siliconflow` | `liblib`
- `IMAGE_MODEL`
- 对应的 `*_API_KEY`

### 3) Run Tests

烟雾测试：

```bash
python -m comic_maker.test_run
```

重试回归测试（锁死“重试不增格”）：

```bash
python -m unittest tests.test_retry_no_panel_growth -v
```

### 4) Run Pipeline

```bash
python -m comic_maker.main
```

安装后也可用命令：

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
│   └── test_retry_no_panel_growth.py
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
