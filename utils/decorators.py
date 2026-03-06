"""
装饰器模块
提供统一的参数注入装饰器
"""
from functools import wraps
from config import settings


def inject_config(func):
    """
    装饰器：自动注入 qBittorrent 配置参数
    
    如果调用时未提供 host/username/password，则使用全局配置
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 如果是位置参数，需要转换为关键字参数
        import inspect
        sig = inspect.signature(func)
        bound = sig.bind_partial(*args, **kwargs)
        
        # 为缺失的参数填充默认值
        if 'host' not in bound.arguments:
            kwargs['host'] = settings.qb_host
        if 'username' not in bound.arguments:
            kwargs['username'] = settings.qb_username
        if 'password' not in bound.arguments:
            kwargs['password'] = settings.qb_password
        
        return await func(*args, **kwargs)
    
    return wrapper
