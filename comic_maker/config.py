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

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
LIBLIB_ACCESS_KEY = os.getenv("LIBLIB_ACCESS_KEY", "")
LIBLIB_SECRET_KEY = os.getenv("LIBLIB_SECRET_KEY", "")
LIBLIB_TEMPLATE_UUID = os.getenv("LIBLIB_TEMPLATE_UUID", "")
COMFYUI_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")
IPADAPTER_MODEL = os.getenv("IPADAPTER_MODEL", "ip-adapter-plus_sdxl_vit-h.bin")
IPADAPTER_CLIP_VISION = os.getenv("IPADAPTER_CLIP_VISION", "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors")
IPADAPTER_WEIGHT = float(os.getenv("IPADAPTER_WEIGHT", "0.6"))

# 当前版本仅支持 DeepSeek 作为 LLM 后端
LLM_BACKEND = "deepseek"
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

# 默认出图改为 LiblibAI
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "comfyui")  # mock | siliconflow | liblib | comfyui
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")

DEBUG = os.getenv("DEBUG", "true").lower() == "true"
LOG_FALLBACKS = os.getenv("LOG_FALLBACKS", "true").lower() == "true"

PANELS_PER_PAGE = 4
MAX_RETRY = 3
# Segments shorter than this many characters are merged with the previous segment
# to avoid trivially short beats (e.g. bare dialogue lines like "来了。")
MIN_BEAT_CHARS = 60

# Fixed style anchor injected into every panel prompt
STYLE_LOCK = (
    "masterpiece, best quality, full-color manga panel illustration, consistent art style across panels, "
    "consistent character design, clean lineart, cel shading, vibrant natural colors, cinematic lighting, "
    "detailed background, coherent costume and facial features, stable eye color and hairstyle"
)

# Negative prompt passed to image providers that support it
NEGATIVE_PROMPT = (
    "monochrome, grayscale, black and white, lowres, blurry, bad anatomy, deformed face, extra fingers, "
    "extra limbs, inconsistent character design, wrong hairstyle, wrong eye color, text, watermark, logo, "
    "jpeg artifacts, overexposed, oversaturated"
)

