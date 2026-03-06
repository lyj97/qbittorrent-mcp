"""
其他杂项 API
提供版本查询、文件优先级设置、种子列表获取等功能
"""
import httpx
from utils.logger import setup_logger
from api.auth import login_to_qbittorrent
from utils.decorators import inject_config

logger = setup_logger(__name__)


@inject_config
async def get_application_version_api(host: str, username: str, password: str) -> str:
    """
    获取 qBittorrent 版本
    
    Returns:
        qBittorrent 版本号
    """
    logger.info("获取 qBittorrent 版本")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        logger.error("登录失败")
        return "登录失败，无法获取 SID"
    
    try:
        headers = {
            "Accept": "*/*",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{host}/api/v2/app/version",
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                version = response.text.strip()
                logger.info(f"qBittorrent 版本：{version}")
                return version
            else:
                logger.error(f"获取版本失败：HTTP {response.status_code}")
                return f"获取版本失败：HTTP {response.status_code}"
                
    except Exception as e:
        logger.error(f"获取版本异常：{str(e)}")
        return f"错误：{str(e)}"


@inject_config
async def set_file_priority_api(hash: str, id: str, priority: int, host: str, username: str, password: str) -> str:
    """
    设置文件优先级
    
    Args:
        hash: 种子哈希值
        id: 文件 ID（从 0 开始）
        priority: 优先级 (0=不下载，1=正常，6=高，7=最高)
        host: qBittorrent WebUI 地址
        username: 用户名
        password: 密码
        
    Returns:
        设置结果消息
    """
    logger.info(f"设置文件优先级：hash={hash}, id={id}, priority={priority}")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        logger.error("登录失败")
        return "登录失败，无法获取 SID"
    
    try:
        params = {"hash": hash, "id": id, "priority": priority}
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/filePrio",
                data=params,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"成功设置文件优先级：{hash}:{id}:{priority}")
                return f"成功设置文件优先级：{hash}:{id}:{priority}"
            else:
                logger.error(f"设置文件优先级失败：HTTP {response.status_code}")
                return f"设置文件优先级失败：HTTP {response.status_code}"
                
    except Exception as e:
        logger.error(f"设置文件优先级异常：{str(e)}")
        return f"错误：{str(e)}"


@inject_config
async def get_torrent_list_api(host: str, username: str, password: str) -> str:
    """
    获取种子列表
    
    Returns:
        种子列表的 JSON 数据
    """
    logger.info("获取种子列表")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        logger.error("登录失败")
        return "登录失败，无法获取 SID"
    
    try:
        headers = {
            "Accept": "*/*",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{host}/api/v2/torrents/info",
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                torrent_list = response.json()
                logger.info(f"获取到 {len(torrent_list)} 个种子")
                return torrent_list
            else:
                logger.error(f"获取种子列表失败：HTTP {response.status_code}")
                return f"获取种子列表失败：HTTP {response.status_code}"
                
    except Exception as e:
        logger.error(f"获取种子列表异常：{str(e)}")
        return f"错误：{str(e)}"
