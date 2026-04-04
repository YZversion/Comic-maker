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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
LIBLIB_ACCESS_KEY = os.getenv("LIBLIB_ACCESS_KEY", "")
LIBLIB_SECRET_KEY = os.getenv("LIBLIB_SECRET_KEY", "")
LIBLIB_TEMPLATE_UUID = os.getenv("LIBLIB_TEMPLATE_UUID", "")

# LLM_BACKEND: "anthropic" | "gemini" | "deepseek"
LLM_BACKEND = os.getenv("LLM_BACKEND", "deepseek")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "siliconflow")  # mock | siliconflow | replicate | comfy
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

PANELS_PER_PAGE = 4
MAX_RETRY = 3

# Fixed style anchor injected into every panel prompt
STYLE_LOCK = "manga panel, black and white ink, clean lineart, screentone shading, highly detailed"

# Negative prompt passed to image providers that support it
NEGATIVE_PROMPT = "color, photograph, 3d render, blurry, text, watermark, extra limbs, deformed"
