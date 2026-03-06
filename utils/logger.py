"""
统一日志配置模块
提供结构化的日志记录功能
"""
import logging
import os
from typing import Optional


def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    配置并返回 logger
    
    Args:
        name: logger 名称，通常使用 __name__
        log_file: 可选的日志文件路径，如果不提供则只输出到控制台
    
    Returns:
        配置好的 Logger 对象
    """
    logger = logging.getLogger(name)
    
    # 从环境变量读取日志级别
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logger.level)
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logger.level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# 创建默认 logger 实例
logger = setup_logger(__name__)
