"""
NovaIuris Backend - Flask应用工厂
"""

import os
import warnings
import hashlib
from time import perf_counter
from pathlib import Path

# 抑制 multiprocessing resource_tracker 的警告（来自第三方库如 transformers）
# 需要在所有其他导入之前设置
warnings.filterwarnings("ignore", message=".*resource_tracker.*")

from flask import Flask, request, g
from uuid import uuid4
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge
from .utils.api_response import api_error
from .utils.rate_limit import CostEndpointRateLimiter
from flask_cors import CORS

from .config import Config
from .utils.logger import setup_logger, get_logger
from .services.runtime_security import verify_supabase_user


def create_app(config_class=Config):
    """Flask应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    environment = app.config.get('APP_ENV', 'development')
    if environment not in {'development', 'test', 'production'}:
        raise RuntimeError('APP_ENV must be development, test or production')
    if environment == 'production':
        required = ('SECRET_KEY', 'SUPABASE_URL', 'SUPABASE_PUBLISHABLE_KEY',
                    'SUPABASE_KEY', 'EMBEDDING_API_KEY', 'LLM_API_KEY', 'ZEP_API_KEY',
                    'CASE_CORPUS_DB_PATH', 'TASK_DB_PATH')
        if any(not app.config.get(key) for key in required):
            raise RuntimeError('Production runtime configuration incomplete')
        if len(app.config['SECRET_KEY']) < 32:
            raise RuntimeError('Production SECRET_KEY is too short')
        if not app.config['SUPABASE_URL'].startswith('https://'):
            raise RuntimeError('Production Supabase URL must use HTTPS')
        if app.config.get('DEBUG') or not app.config.get('RATE_LIMIT_ENABLED'):
            raise RuntimeError('Production debug and rate limiting configuration unsafe')
        origins = app.config.get('CORS_ALLOWED_ORIGINS') or []
        if not origins or any(origin == '*' or not origin.startswith('https://') for origin in origins):
            raise RuntimeError('Production CORS origins must be explicit HTTPS origins')
        bounds = {'CASE_RESEARCH_MAX_QUERIES': (1, 12), 'CASE_REPORT_MAX_SOURCES': (1, 50),
                  'CASE_DOCUMENT_CONTEXT_TOP_K': (1, 30), 'CASE_DOCUMENT_MAX_FILES': (1, 30),
                  'CASE_DOCUMENT_MAX_FILE_BYTES': (1, 50 * 1024 * 1024),
                  'CASE_DOCUMENT_MAX_CASE_BYTES': (1, 300 * 1024 * 1024),
                  'CASE_DOCUMENT_MAX_REQUEST_BYTES': (1, 310 * 1024 * 1024),
                  'CASE_DOCUMENT_MAX_UNCOMPRESSED_BYTES': (1, 150 * 1024 * 1024),
                  'CASE_DOCUMENT_MAX_PAGES': (1, 10000),
                  'CASE_DOCUMENT_EMBEDDING_BATCH_SIZE': (1, 128),
                  'RATE_LIMIT_DOCUMENTS': (1, 100),
                  'ACTIVE_TASKS_PER_USER': (1, 10), 'AUTH_TIMEOUT_SECONDS': (1, 15),
                  'PROVIDER_MAX_RETRIES': (0, 2), 'LLM_TIMEOUT_SECONDS': (1, 180),
                  'NOVACOURT_GRAPH_TIMEOUT_SECONDS': (1, 1800),
                  'NOVACOURT_SIMULATION_TIMEOUT_SECONDS': (1, 1800)}
        if any(not lower <= app.config.get(key, -1) <= upper
               for key, (lower, upper) in bounds.items()):
            raise RuntimeError('Production runtime limit outside safe range')
        if app.config['CASE_DOCUMENT_MAX_FILE_BYTES'] > app.config['CASE_DOCUMENT_MAX_CASE_BYTES'] or app.config['CASE_DOCUMENT_MAX_CASE_BYTES'] >= app.config['CASE_DOCUMENT_MAX_REQUEST_BYTES']:
            raise RuntimeError('Production upload limits are inconsistent')
        project_root = Path(__file__).resolve().parents[2]
        for key in ('CASE_CORPUS_DB_PATH', 'TASK_DB_PATH'):
            configured = Path(app.config[key])
            target = configured.resolve()
            if not configured.is_absolute() or target.is_relative_to(project_root):
                raise RuntimeError('Production runtime database must use an external persistent volume')
    limiter = CostEndpointRateLimiter(config_class)
    app.extensions['cost_limiter'] = limiter
    if environment == 'production':
        from .models.task import TaskManager
        from .services.task_repository import TaskRepository, DocumentTaskRepository
        from .services.document_tasks import DocumentTaskManager
        app.extensions['task_manager'] = TaskManager(TaskRepository(app.config['TASK_DB_PATH']))
        app.extensions['document_task_repository'] = DocumentTaskRepository(app.config['TASK_DB_PATH'])
        app.extensions['document_task_manager'] = DocumentTaskManager(
            app.config['DOCUMENT_STAGING_MAX_AGE_SECONDS'],
            repository=app.extensions['document_task_repository'])

    # 设置JSON编码：确保中文直接显示（而不是 \uXXXX 格式）
    # Flask >= 2.3 使用 app.json.ensure_ascii，旧版本使用 JSON_AS_ASCII 配置
    if hasattr(app, 'json') and hasattr(app.json, 'ensure_ascii'):
        app.json.ensure_ascii = False
    
    # 设置日志
    logger = setup_logger('NovaIuris')
    
    # 只在 reloader 子进程中打印启动信息（避免 debug 模式下打印两次）
    is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    debug_mode = app.config.get('DEBUG', False)
    should_log_startup = not debug_mode or is_reloader_process
    
    if should_log_startup:
        logger.info("=" * 50)
        logger.info("NovaIuris Backend 启动中...")
        logger.info("=" * 50)
    
    # 启用CORS
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ALLOWED_ORIGINS"]}})
    
    # 注册模拟进程清理函数（确保服务器关闭时终止所有模拟进程）
    from .services.simulation_runner import SimulationRunner
    SimulationRunner.register_cleanup()
    if should_log_startup:
        logger.info("已注册模拟进程清理函数")
    
    # 请求日志中间件
    @app.before_request
    def identify_request():
        g.request_id = str(uuid4())
        g.request_started = perf_counter()
        if environment == 'production' and (request.path.startswith(('/api/graph/', '/api/simulation/', '/api/report/', '/api/export/')) or request.path == '/api/search'):
            return api_error('LEGACY_DISABLED', 'Esta ruta ya no está disponible.', g.request_id, 410)
        if environment == 'production' and request.method == 'OPTIONS':
            g.authenticated_user_id = None
            return None  # Browser preflight carries no bearer token.
        if environment == 'production' and request.path.startswith('/api/'):
            header = request.headers.get('Authorization', '')
            token = header[7:] if header.startswith('Bearer ') else ''
            verifier = app.config.get('AUTH_VERIFIER') or verify_supabase_user
            g.authenticated_user_id = verifier(token, app.config) if token else None
            if not g.authenticated_user_id:
                return api_error('AUTH_REQUIRED', 'Se requiere una sesión válida.', g.request_id, 401)
        else:
            # Explicit local/test identity; request JSON and headers cannot set it.
            g.authenticated_user_id = 'local-development-user'
        allowed, retry_after = limiter.check(g.authenticated_user_id or request.remote_addr, request.path) if request.method == "POST" else (True, 0)
        if not allowed:
            response, status = api_error('RATE_LIMITED', 'Demasiadas solicitudes. Inténtalo más tarde.', g.request_id, 429)
            response.headers['Retry-After'] = str(retry_after)
            return response, status

    @app.after_request
    def protect_response(response):
        response.headers['X-Request-ID'] = g.request_id
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['X-Frame-Options'] = 'DENY'
        if response.is_json and response.status_code >= 400:
            payload = response.get_json(silent=True) or {}
            error = payload.get('error')
            # Legacy errors are sanitized here; never pass exception text or traceback.
            if not isinstance(error, dict) or not {'code', 'message'} <= error.keys():
                message = 'Solicitud inválida.' if response.status_code < 500 else 'No fue posible completar la solicitud.'
                safe, _ = api_error('REQUEST_FAILED', message, g.request_id, response.status_code)
                response.set_data(safe.get_data())
            else:
                safe, _ = api_error(error['code'], error['message'], g.request_id, response.status_code)
                response.set_data(safe.get_data())
        identity = getattr(g, 'authenticated_user_id', None)
        safe_user = hashlib.sha256(identity.encode()).hexdigest()[:12] if identity else '-'
        logger.info('event=http_request request_id=%s user_hash=%s endpoint=%s method=%s status=%s duration_ms=%s',
                    g.request_id, safe_user, request.endpoint, request.method,
                    response.status_code, round((perf_counter() - g.request_started) * 1000))
        return response

    @app.errorhandler(Exception)
    def public_error(error):
        status = error.code if isinstance(error, HTTPException) else 500
        logger.error('request_id=%s error_type=%s', getattr(g, 'request_id', ''), type(error).__name__)
        return api_error('REQUEST_FAILED', 'No fue posible completar la solicitud.', getattr(g, 'request_id', ''), status)

    @app.errorhandler(RequestEntityTooLarge)
    def request_too_large(error):
        return api_error('FILE_TOO_LARGE', 'La solicitud supera el límite configurado de carga.',
                         getattr(g, 'request_id', ''), 413)

    # 注册蓝图
    # 👇 1. SE AGREGÓ export_bp A LA IMPORTACIÓN
    from .api import (
        graph_bp,
        simulation_bp,
        report_bp,
        export_bp,
        search_bp,
        case_bp,
        documents_bp
    )
    app.register_blueprint(graph_bp, url_prefix='/api/graph')
    app.register_blueprint(simulation_bp, url_prefix='/api/simulation')
    app.register_blueprint(report_bp, url_prefix='/api/report')
    # 👇 2. SE REGISTRÓ LA NUEVA RUTA DE EXPORTACIÓN
    app.register_blueprint(export_bp, url_prefix='/api/export')
    app.register_blueprint(search_bp, url_prefix='/api/search') # 👈 AGREGA ESTA LÍNEA 
    
    app.register_blueprint(
        case_bp,
        url_prefix='/api'
    )
    app.register_blueprint(documents_bp, url_prefix='/api')

    # 健康检查
    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'NovaIuris Backend'}

    @app.route('/ready')
    def ready():
        try:
            import sqlite3
            from .services.runtime_security import CaseOwnershipRepository
            CaseOwnershipRepository(app.config['CASE_CORPUS_DB_PATH'])
        except (OSError, ValueError, sqlite3.Error):
            return {'status': 'unavailable'}, 503
        return {'status': 'ready'}
    
    if should_log_startup:
        logger.info("NovaIuris Backend 启动完成")
    
    return app
