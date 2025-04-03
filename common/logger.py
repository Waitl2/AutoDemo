import os
from loguru import logger
from common.read_config import get_config

def setup_logger():
    """
    配置loguru日志记录器
    """
    config = get_config()
    log_config = config.get('logging', {})
    log_level = log_config.get('level', 'INFO')
    log_rotation = log_config.get('rotation', '10 MB')
    log_retention = log_config.get('retention', '7 days')
    log_file_path = log_config.get('file_path', 'logs/runtime.log')

    log_directory = os.path.dirname(log_file_path)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    logger.remove()  # 移除默认的日志处理器

    # 添加控制台输出handler
    logger.add(
        sink=lambda msg: print(msg, end=''),  # 控制台输出
        level=log_level.upper(),  # 日志级别
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True # 在控制台启用颜色
    )

    # 添加文件输出handler
    logger.add(
        log_file_path,
        level=log_level.upper(),
        rotation=log_rotation,
        retention=log_retention,
        encoding='utf-8',
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        enqueue=True, # 异步写入，提高性能
        backtrace=True, # 记录异常堆栈信息
        diagnose=True  # 记录更详细的诊断信息
    )

    logger.info("Logger setup complete.")
    return logger

logger = setup_logger()