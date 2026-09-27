"""
NovaIuris Backend - Flask应用工厂
"""

import os
import warnings

# 抑制 multiprocessing resource_tracker 的警告（来自第三方库如 transformers）
# 需要在所有其他导入之前设置
warnings.filterwarnings("ignore", message=".*resource_tracker.*")

from flask import Flask, request, g
from uuid import uuid4
from werkzeug.exceptions import HTTPException
from .utils.api_response import api_error
from .utils.rate_limit import CostEndpointRateLimiter
from flask_cors import CORS

from .config import Config
from .utils.logger import setup_logger, get_logger


def create_app(config_class=Config):
    """Flask应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    if os.getenv('APP_ENV', '').lower() == 'production' and not app.config.get('SECRET_KEY'):
        raise RuntimeError('SECRET_KEY must be configured in production')
    limiter = CostEndpointRateLimiter(config_class)
    app.extensions['cost_limiter'] = limiter

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
        allowed, retry_after = limiter.check(request.remote_addr, request.path) if request.method == "POST" else (True, 0)
        if not allowed:
            response, status = api_error('RATE_LIMITED', 'Demasiadas solicitudes. Inténtalo más tarde.', g.request_id, 429)
            response.headers['Retry-After'] = str(retry_after)
            return response, status

    @app.after_request
    def protect_response(response):
        response.headers['X-Request-ID'] = g.request_id
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
        logger.info('request_id=%s method=%s status=%s', g.request_id, request.method, response.status_code)
        return response

    @app.errorhandler(Exception)
    def public_error(error):
        status = error.code if isinstance(error, HTTPException) else 500
        logger.error('request_id=%s error_type=%s', getattr(g, 'request_id', ''), type(error).__name__)
        return api_error('REQUEST_FAILED', 'No fue posible completar la solicitud.', getattr(g, 'request_id', ''), status)

    # 注册蓝图
    # 👇 1. SE AGREGÓ export_bp A LA IMPORTACIÓN
    from .api import (
        graph_bp,
        simulation_bp,
        report_bp,
        export_bp,
        search_bp,
        case_bp
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

    # 健康检查
    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'NovaIuris Backend'}
    
    if should_log_startup:
        logger.info("NovaIuris Backend 启动完成")
    
    return app