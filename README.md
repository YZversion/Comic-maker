# Comic Maker

一个用于把章节文本自动转换成漫画生产中间产物的流水线项目。

当前主流程：

`章节输入 -> 自动切分 -> 镜头规划 -> 上下文补全 -> 出图(mock) -> 审核 -> 拼页 -> 导出`

## Current Status

目前已具备可运行骨架（偏 Day1/Day2 能力）：

- 章节切分：按段落/基础规则生成 `Beat`
- 镜头规划：根据 `Beat` 生成基础 `ShotPlan`
- Prompt 组装：结合角色/场景上下文生成面板 prompt
- 出图：默认 `mock` provider（写入占位文件）
- 审核与重试：支持人工通过/重试
- 拼页与导出：生成 `page_manifest` 并导出章节包

## Project Layout

```text
Comic-maker/
├── comic_maker/
│   ├── main.py
│   ├── config.py
│   ├── test_run.py
│   ├── prompts/
│   ├── core/
│   │   ├── models.py
│   │   ├── storage.py
│   │   ├── segmenter.py
│   │   ├── planner.py
│   │   ├── prompt_builder.py
│   │   ├── context_manager.py
│   │   ├── panel_runner.py
│   │   ├── reviewer.py
│   │   ├── page_builder.py
│   │   └── exporter.py
│   ├── providers/
│   │   ├── llm_provider.py
│   │   └── image_provider.py
│   ├── data/
│   └── output/
├── pyproject.toml
├── .env.example
└── LICENSE
```

## Requirements

- Python `>=3.11`
- Windows / macOS / Linux 均可（已在 Windows PowerShell 下验证）

## Quick Start

### 1) 安装依赖

在仓库根目录执行：

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

pip install -e .
```

### 2) 运行烟雾测试（推荐先跑）

```bash
python -m comic_maker.test_run
```

如果输出包含 `-- 全部通过 --`，说明当前骨架正常。

### 3) 运行主流程

```bash
python -m comic_maker.main
```

或安装后直接用 CLI：

```bash
comic-maker
```

## Input / Output

### 输入

- 交互输入章节 ID（例如 `ch01`）
- 交互输入章节文本，单独输入 `END` 结束

### 运行中间数据

默认写入 `comic_maker/data/`：

- `character_db.json`
- `scene_db.json`
- `prop_db.json`
- `panel_manifest.json`
- `project_state.json`

### 输出产物

默认写入 `comic_maker/output/`：

- `panels/`：mock 出图占位文件（`*.png.txt`）
- `pages/page_manifest.json`
- `exports/<chapter_id>/`：章节导出包
- `logs/run.log`

## Config

核心配置在 `comic_maker/config.py`：

- 路径：`DATA_DIR`, `OUTPUT_DIR`, `..._PATH`
- 模型：`LLM_MODEL`（当前默认 `gpt-4o-mini`）
- 出图：`IMAGE_PROVIDER`（当前默认 `mock`）
- 其它：`PANELS_PER_PAGE`, `MAX_RETRY`, `DEBUG`

## Environment Variables

可参考 `.env.example`（后续接入真实服务时使用）：

- `ANTHROPIC_API_KEY`
- `IMAGE_PROVIDER`
- `REPLICATE_API_TOKEN`
- `DEBUG`

## Common Issues

### Windows 控制台乱码/编码问题

如果终端中文显示异常，可先执行：

```powershell
$env:PYTHONUTF8='1'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
```

## Next Steps

- 用真实 LLM 替换 `providers/llm_provider.py` stub
- 用真实图片服务替换 `providers/image_provider.py` mock
- 增加自动审核规则和更细粒度重试策略
- 补充单元测试（`segmenter/planner/storage`）
