"""
Tracker 管理相关 API
提供获取和添加 Tracker 功能
"""
import httpx
from utils.logger import setup_logger
from api.auth import login_to_qbittorrent
from utils.decorators import inject_config

logger = setup_logger(__name__)


@inject_config
async def get_torrent_trackers_urls(hash: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    获取种子的 Tracker 列表
    
    Args:
        hash: 种子哈希值
        host: qBittorrent WebUI 地址
        username: 用户名
        password: 密码
        
    Returns:
        包含 Tracker 信息的格式化字符串
    """
    logger.info(f"获取 Tracker 请求：hash={hash}")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        logger.error("登录失败")
        return "登录失败，无法获取 SID"
    
    try:
        params = {"hash": hash}
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{host}/api/v2/torrents/trackers",
                params=params,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                trackers = response.json()
                logger.debug(f"获取到 {len(trackers)} 个 Tracker")
                
                if not trackers:
                    logger.info("该种子没有 Tracker")
                    return "该种子没有 Tracker"
                
                # 提取所有实际 URL（排除 DHT、PeX、LSD 等特殊 Tracker）
                tracker_urls = []
                for tracker in trackers:
                    url = tracker.get('url')
                    if url and not url.startswith('** ['):
                        tracker_urls.append(url)
                
                if not tracker_urls:
                    logger.info("该种子没有有效的 Tracker URL")
                    return "该种子没有有效的 Tracker URL"
                
                result = ",".join(tracker_urls)
                logger.info(f"获取到 {len(tracker_urls)} 个 Tracker URL")
                return result
            else:
                logger.error(f"获取 Tracker 失败：HTTP {response.status_code}")
                return f"获取 Tracker 失败：HTTP {response.status_code}"
                
    except Exception as e:
        logger.error(f"获取 Tracker 异常：{str(e)}")
        return f"错误：{str(e)}"


@inject_config
async def add_trackers_to_torrent_api(hash: str, trackers: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    向种子添加 Tracker
    
    Args:
        hash: 种子哈希值
        trackers: Tracker URL，多个用 %0A 分隔
        host: qBittorrent WebUI 地址
        username: 用户名
        password: 密码
        
    Returns:
        添加 Tracker 的结果消息
    """
    logger.info(f"添加 Tracker 请求：hash={hash}, trackers={trackers[:50]}...")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        logger.error("登录失败")
        return "登录失败，无法获取 SID"
    
    try:
        params = {"hash": hash, "urls": trackers}
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/addTrackers",
                data=params,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"成功添加 Tracker：{hash}")
                return f"成功添加 Tracker: {hash}"
            else:
                logger.error(f"添加 Tracker 失败：HTTP {response.status_code}")
                return f"添加 Tracker 失败：HTTP {response.status_code}"
                
    except Exception as e:
        logger.error(f"添加 Tracker 异常：{str(e)}")
        return f"错误：{str(e)}"
