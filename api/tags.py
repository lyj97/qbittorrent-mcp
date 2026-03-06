"""
标签管理相关 API
提供添加种子标签功能
"""
import httpx
from utils.logger import setup_logger
from api.auth import login_to_qbittorrent
from utils.decorators import inject_config

logger = setup_logger(__name__)


@inject_config
async def add_torrent_tags_api(hash: str, tags: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    为种子添加标签
    
    Args:
        hash: 种子哈希值（或多个用 | 分隔）
        tags: 标签列表，逗号分隔
        host: qBittorrent WebUI 地址
        username: 用户名
        password: 密码
        
    Returns:
        添加标签的结果消息
    """
    logger.info(f"添加种子标签：hash={hash}, tags={tags}")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        logger.error("登录失败")
        return "登录失败，无法获取 SID"
    
    try:
        params = {"hashes": hash, "tags": tags}
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/addTags",
                data=params,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"成功添加标签：{hash}:{tags}")
                return f"成功添加标签：{hash}:{tags}"
            else:
                logger.error(f"添加标签失败：HTTP {response.status_code}")
                return f"添加标签失败：HTTP {response.status_code}"
                
    except Exception as e:
        logger.error(f"添加标签异常：{str(e)}")
        return f"错误：{str(e)}"
