"""
认证相关 API
提供登录功能
"""
import httpx
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def login_to_qbittorrent(username: str, password: str, host: str) -> httpx.Cookies | None:
    """
    登录到 qBittorrent WebUI 并获取会话 cookie
    
    Args:
        username: 用户名
        password: 密码
        host: qBittorrent WebUI 地址
        
    Returns:
        成功返回包含会话 cookie 的对象，失败返回 None
    """
    logger.debug(f"尝试登录到 {host}，用户：{username}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/auth/login",
                data={"username": username, "password": password}
            )
        
            if response.status_code == 200:
                logger.info(f"登录成功：{host}")
                return response.cookies
            else:
                logger.error(f"登录失败：{host}, HTTP {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"登录异常：{str(e)}")
        return None
