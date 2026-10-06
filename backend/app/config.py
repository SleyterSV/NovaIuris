"""
配置管理
统一从项目根目录的 .env 文件加载配置
"""

import os
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
# 路径: NovaIuris/.env (相对于 backend/app/config.py)
project_root_env = os.path.join(os.path.dirname(__file__), '../../.env')

if os.path.exists(project_root_env):
    load_dotenv(project_root_env, override=False)
else:
    # 如果根目录没有 .env，尝试加载环境变量（用于生产环境）
    load_dotenv(override=False)


class Config:
    """Flask配置类"""
    
    # Flask配置
    APP_ENV = os.environ.get('APP_ENV', 'development').lower()
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_PUBLISHABLE_KEY = os.environ.get('SUPABASE_PUBLISHABLE_KEY')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    EMBEDDING_API_KEY = os.environ.get('OPENAI_API_KEY')
    AUTH_TIMEOUT_SECONDS = int(os.environ.get('AUTH_TIMEOUT_SECONDS', '5'))
    PROVIDER_MAX_RETRIES = int(os.environ.get('PROVIDER_MAX_RETRIES', '2'))
    LLM_TIMEOUT_SECONDS = int(os.environ.get('LLM_TIMEOUT_SECONDS', '60'))
    ACTIVE_TASKS_PER_USER = int(os.environ.get('ACTIVE_TASKS_PER_USER', '3'))
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.environ.get(
        'CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',') if origin.strip()]
    NOVACOURT_GRAPH_ENABLED = os.getenv('NOVACOURT_GRAPH_ENABLED', 'true').lower() == 'true'
    NOVACOURT_TASK_TIMEOUT_SECONDS = int(os.getenv('NOVACOURT_TASK_TIMEOUT_SECONDS', '1800'))
    NOVACOURT_GRAPH_TIMEOUT_SECONDS = int(os.getenv('NOVACOURT_GRAPH_TIMEOUT_SECONDS', '600'))
    NOVACOURT_GRAPH_POLL_INTERVAL_SECONDS = int(os.getenv('NOVACOURT_GRAPH_POLL_INTERVAL_SECONDS', '3'))
    NOVACOURT_GRAPH_SETTLE_SECONDS = int(os.getenv('NOVACOURT_GRAPH_SETTLE_SECONDS', '30'))
    NOVACOURT_PROVIDER_TIMEOUT_SECONDS = int(os.getenv('NOVACOURT_PROVIDER_TIMEOUT_SECONDS', '60'))
    NOVACOURT_GRAPH_BATCH_SIZE = int(os.getenv('NOVACOURT_GRAPH_BATCH_SIZE', '3'))
    NOVACOURT_SIMULATION_ENABLED = os.getenv('NOVACOURT_SIMULATION_ENABLED', 'true').lower() == 'true'
    NOVACOURT_SIMULATION_TIMEOUT_SECONDS = int(os.getenv('NOVACOURT_SIMULATION_TIMEOUT_SECONDS', '600'))
    NOVACOURT_PROVIDER_MAX_RETRIES = int(os.getenv('NOVACOURT_PROVIDER_MAX_RETRIES', '2'))
    NOVACOURT_RETRY_MAX_DELAY_SECONDS = int(os.getenv('NOVACOURT_RETRY_MAX_DELAY_SECONDS', '30'))
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATE_LIMIT_WINDOW_SECONDS = 60
    RATE_LIMIT_SEARCH = 30
    RATE_LIMIT_CASE = 10
    RATE_LIMIT_SIMULATION = 10
    RATE_LIMIT_DOCUMENTS = int(os.getenv('RATE_LIMIT_DOCUMENTS', '20'))

    # JSON配置 - 禁用ASCII转义，让中文直接显示（而不是 \uXXXX 格式）
    JSON_AS_ASCII = False
    
    # LLM配置（统一使用OpenAI格式）
    LLM_API_KEY = os.environ.get('LLM_API_KEY')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'https://api.openai.com/v1')
    LLM_MODEL_NAME = os.environ.get('LLM_MODEL_NAME', 'gpt-4o-mini')
    
    # ==========================================================
    # Compatibilidad con servicios NovaSearch / NovaCase
    # ==========================================================

    OPENAI_API_KEY = LLM_API_KEY
    OPENAI_BASE_URL = LLM_BASE_URL
    OPENAI_MODEL = LLM_MODEL_NAME

    # Zep配置
    ZEP_API_KEY = os.environ.get('ZEP_API_KEY')
    
    # 文件上传配置
    CASE_DOCUMENT_MAX_FILE_BYTES = int(os.getenv('CASE_DOCUMENT_MAX_FILE_BYTES', str(45 * 1024 * 1024)))
    CASE_DOCUMENT_MAX_CASE_BYTES = int(os.getenv('CASE_DOCUMENT_MAX_CASE_BYTES', str(200 * 1024 * 1024)))
    CASE_DOCUMENT_MAX_REQUEST_BYTES = int(os.getenv('CASE_DOCUMENT_MAX_REQUEST_BYTES', str(201 * 1024 * 1024)))
    MAX_CONTENT_LENGTH = CASE_DOCUMENT_MAX_REQUEST_BYTES
    CASE_DOCUMENT_MAX_FILES = int(os.getenv('CASE_DOCUMENT_MAX_FILES', '20'))
    CASE_DOCUMENT_MAX_UNCOMPRESSED_BYTES = int(os.getenv('CASE_DOCUMENT_MAX_UNCOMPRESSED_BYTES', str(100 * 1024 * 1024)))
    CASE_DOCUMENT_MAX_PAGES = int(os.getenv('CASE_DOCUMENT_MAX_PAGES', '5000'))
    CASE_DOCUMENT_CHUNK_TOKENS = int(os.getenv('CASE_DOCUMENT_CHUNK_TOKENS', '600'))
    CASE_DOCUMENT_CHUNK_OVERLAP = int(os.getenv('CASE_DOCUMENT_CHUNK_OVERLAP', '60'))
    CASE_DOCUMENT_CHUNK_MAX_CHARS = int(os.getenv('CASE_DOCUMENT_CHUNK_MAX_CHARS', '12000'))
    CASE_DOCUMENT_EMBEDDING_BATCH_SIZE = int(os.getenv('CASE_DOCUMENT_EMBEDDING_BATCH_SIZE', '64'))
    CASE_DOCUMENT_OCR_MIN_PAGE_CHARACTERS = int(os.getenv('CASE_DOCUMENT_OCR_MIN_PAGE_CHARACTERS', '30'))
    CASE_DOCUMENT_CONTEXT_TOP_K = int(os.getenv('CASE_DOCUMENT_CONTEXT_TOP_K', '8'))
    CASE_RESEARCH_MAX_QUERIES = int(os.getenv('CASE_RESEARCH_MAX_QUERIES', '4'))
    CASE_REPORT_MAX_SOURCES = int(os.getenv('CASE_REPORT_MAX_SOURCES', '16'))
    DOCUMENT_STAGING_MAX_AGE_SECONDS = int(os.getenv('DOCUMENT_STAGING_MAX_AGE_SECONDS', str(24 * 60 * 60)))
    CASE_CORPUS_RETENTION_DAYS = int(os.getenv('CASE_CORPUS_RETENTION_DAYS', '30'))
    CASE_CORPUS_DB_PATH = os.getenv('CASE_CORPUS_DB_PATH', os.path.join(os.path.dirname(__file__), '../uploads/case_corpus.sqlite3'))
    TASK_DB_PATH = os.getenv('TASK_DB_PATH', os.path.join(os.path.dirname(__file__), '../uploads/runtime_tasks.sqlite3'))
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'markdown'}
    
    # 文本处理配置
    DEFAULT_CHUNK_SIZE = 500  # 默认切块大小
    DEFAULT_CHUNK_OVERLAP = 50  # 默认重叠大小
    
    # OASIS模拟配置
    OASIS_DEFAULT_MAX_ROUNDS = int(os.environ.get('OASIS_DEFAULT_MAX_ROUNDS', '10'))
    OASIS_SIMULATION_DATA_DIR = os.path.join(os.path.dirname(__file__), '../uploads/simulations')
    
    # OASIS平台可用动作配置
    OASIS_TWITTER_ACTIONS = [
        'CREATE_POST', 'LIKE_POST', 'REPOST', 'FOLLOW', 'DO_NOTHING', 'QUOTE_POST'
    ]
    OASIS_REDDIT_ACTIONS = [
        'LIKE_POST', 'DISLIKE_POST', 'CREATE_POST', 'CREATE_COMMENT',
        'LIKE_COMMENT', 'DISLIKE_COMMENT', 'SEARCH_POSTS', 'SEARCH_USER',
        'TREND', 'REFRESH', 'DO_NOTHING', 'FOLLOW', 'MUTE'
    ]
    
    # Report Agent配置
    REPORT_AGENT_MAX_TOOL_CALLS = int(os.environ.get('REPORT_AGENT_MAX_TOOL_CALLS', '5'))
    REPORT_AGENT_MAX_REFLECTION_ROUNDS = int(os.environ.get('REPORT_AGENT_MAX_REFLECTION_ROUNDS', '2'))
    REPORT_AGENT_TEMPERATURE = float(os.environ.get('REPORT_AGENT_TEMPERATURE', '0.5'))
    
    @classmethod
    def validate(cls):
        """验证必要配置"""
        errors = []
        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY 未配置")
        if not cls.ZEP_API_KEY:
            errors.append("ZEP_API_KEY 未配置")
        return errors

