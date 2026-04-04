import os

from dotenv import load_dotenv

# 优先加载项目根目录的 .env 文件
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

PANELS_DIR = os.path.join(OUTPUT_DIR, "panels")
PAGES_DIR = os.path.join(OUTPUT_DIR, "pages")
EXPORTS_DIR = os.path.join(OUTPUT_DIR, "exports")
LOGS_DIR = os.path.join(OUTPUT_DIR, "logs")

CHARACTER_DB_PATH = os.path.join(DATA_DIR, "character_db.json")
SCENE_DB_PATH = os.path.join(DATA_DIR, "scene_db.json")
PROP_DB_PATH = os.path.join(DATA_DIR, "prop_db.json")
PANEL_MANIFEST_PATH = os.path.join(DATA_DIR, "panel_manifest.json")
PROJECT_STATE_PATH = os.path.join(DATA_DIR, "project_state.json")
PAGE_MANIFEST_PATH = os.path.join(PAGES_DIR, "page_manifest.json")
RUN_LOG_PATH = os.path.join(LOGS_DIR, "run.log")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

LLM_MODEL = os.getenv("LLM_MODEL", "claude-haiku-4-5-20251001")
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "mock")  # mock | replicate | comfy
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

PANELS_PER_PAGE = 4
MAX_RETRY = 3
