"""
限速控制相关 API
提供全局和单种子的上传/下载限速功能
"""
import httpx
from utils.logger import setup_logger
from api.auth import login_to_qbittorrent
from utils.decorators import inject_config

logger = setup_logger(__name__)


@inject_config
async def set_global_download_limit_api(limit: int, host: str, username: str, password: str) -> str:
    """
    设置全局下载速度限制
    
    Args:
        limit: 速度限制值，字节/秒
        host: qBittorrent WebUI 地址
        username: 用户名
        password: 密码
        
    Returns:
        设置限速的结果消息
    """
    logger.info(f"设置全局下载限速：{limit} bytes/s")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        logger.error("登录失败")
        return "登录失败，无法获取 SID"
    
    try:
        params = {"limit": limit}
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/transfer/setDownloadLimit",
                data=params,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"成功设置全局下载限速：{limit}")
                return f"成功设置全局下载限速：{limit} bytes/s"
            else:
                logger.error(f"设置全局下载限速失败：HTTP {response.status_code}")
                return f"设置全局下载限速失败：HTTP {response.status_code}"
                
    except Exception as e:
        logger.error(f"设置全局下载限速异常：{str(e)}")
        return f"错误：{str(e)}"


@inject_config
async def set_global_upload_limit_api(limit: int, host: str, username: str, password: str) -> str:
    """
    设置全局上传速度限制
    
    Args:
        limit: 速度限制值，字节/秒
        host: qBittorrent WebUI 地址
        username: 用户名
        password: 密码
        
    Returns:
        设置限速的结果消息
    """
    logger.info(f"设置全局上传限速：{limit} bytes/s")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        logger.error("登录失败")
        return "登录失败，无法获取 SID"
    
    try:
        params = {"limit": limit}
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/transfer/setUploadLimit",
                data=params,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"成功设置全局上传限速：{limit}")
                return f"成功设置全局上传限速：{limit} bytes/s"
            else:
                logger.error(f"设置全局上传限速失败：HTTP {response.status_code}")
                return f"设置全局上传限速失败：HTTP {response.status_code}"
                
    except Exception as e:
        logger.error(f"设置全局上传限速异常：{str(e)}")
        return f"错误：{str(e)}"


@inject_config
async def set_torrent_download_limit_api(hash: str, limit: int, host: str, username: str, password: str) -> str:
    """
    设置单个种子的下载速度限制
    
    Args:
        hash: 种子哈希值
        limit: 速度限制值，字节/秒
        host: qBittorrent WebUI 地址
        username: 用户名
        password: 密码
        
    Returns:
        设置限速的结果消息
    """
    logger.info(f"设置种子下载限速：hash={hash}, limit={limit}")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        logger.error("登录失败")
        return "登录失败，无法获取 SID"
    
    try:
        params = {"hashes": hash, "limit": limit}
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/setDownloadLimit",
                data=params,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"成功设置种子下载限速：{hash}:{limit}")
                return f"成功设置种子下载限速：{hash}:{limit}"
            else:
                logger.error(f"设置种子下载限速失败：HTTP {response.status_code}")
                return f"设置种子下载限速失败：HTTP {response.status_code}"
                
    except Exception as e:
        logger.error(f"设置种子下载限速异常：{str(e)}")
        return f"错误：{str(e)}"


@inject_config
async def set_torrent_upload_limit_api(hash: str, limit: int, host: str, username: str, password: str) -> str:
    """
    设置单个种子的上传速度限制
    
    Args:
        hash: 种子哈希值
        limit: 速度限制值，字节/秒
        host: qBittorrent WebUI 地址
        username: 用户名
        password: 密码
        
    Returns:
        设置限速的结果消息
    """
    logger.info(f"设置种子上传限速：hash={hash}, limit={limit}")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        logger.error("登录失败")
        return "登录失败，无法获取 SID"
    
    try:
        params = {"hashes": hash, "limit": limit}
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/setUploadLimit",
                data=params,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"成功设置种子上传限速：{hash}:{limit}")
                return f"成功设置种子上传限速：{hash}:{limit}"
            else:
                logger.error(f"设置种子上传限速失败：HTTP {response.status_code}")
                return f"设置种子上传限速失败：HTTP {response.status_code}"
                
    except Exception as e:
        logger.error(f"设置种子上传限速异常：{str(e)}")
        return f"错误：{str(e)}"
