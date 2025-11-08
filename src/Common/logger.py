import logging
import os
from datetime import datetime
from pathlib import Path

# 日志目录
LOG_DIR = Path(__file__).parent.parent.parent / ".log"
LOG_DIR.mkdir(exist_ok=True)

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 创建日志文件名（按日期分割）
def get_log_filename(prefix="app"):
    """获取日志文件名"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    return LOG_DIR / f"{prefix}_{date_str}.log"

# 配置日志系统（集成到 uvicorn）
def setup_logging(level=logging.INFO):
    """配置应用日志系统
    
    Args:
        level: 日志级别
    """
    # 文件处理器
    file_handler = logging.FileHandler(
        get_log_filename("app"),
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    # 配置 uvicorn 的日志也输出到文件
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.addHandler(file_handler)
    
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.addHandler(file_handler)
    
    # 配置 FastAPI 日志
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.addHandler(file_handler)

# 获取模块日志器
def get_logger(module_name):
    """获取模块日志器
    
    Args:
        module_name: 模块名称
    
    Returns:
        logging.Logger: 日志器
    """
    return logging.getLogger(f"newtexus.{module_name}")

