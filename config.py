"""
配置管理模块
从环境变量读取配置
"""
import os


class Settings:
    """应用配置"""
    
    def __init__(self):
        # qBittorrent 配置
        self.qb_host = os.getenv("QB_HOST", "http://127.0.0.1:8580")
        self.qb_username = os.getenv("QB_USERNAME", "admin")
        self.qb_password = os.getenv("QB_PASSWORD", "adminadmin")
        
        # 日志配置
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # 搜索配置
        self.search_max_retries = int(os.getenv("SEARCH_MAX_RETRIES", "10"))
        self.search_retry_delay = float(os.getenv("SEARCH_RETRY_DELAY", "1.0"))


# 全局配置实例
settings = Settings()
