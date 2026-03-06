"""
种子管理相关 API
提供添加、删除、暂停、恢复种子功能
"""
import os
import json
import httpx
from utils.logger import setup_logger
from api.auth import login_to_qbittorrent
from utils.decorators import inject_config

logger = setup_logger(__name__)


async def add_torrent_api(query: str, host: str, username: str, password: str) -> str:
    """
    添加种子到 qBittorrent
    
    Args:
        query: 查询字符串，包含种子文件路径
        host: qBittorrent WebUI 地址
        username: 用户名
        password: 密码
        
    Returns:
        添加操作的状态和消息
    """
    logger.info(f"收到添加种子请求：{query[:100]}...")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        logger.error("登录失败，无法获取会话")
        return "登录失败，无法获取 SID"
    
    try:
        # 解析查询字符串
        try:
            data = json.loads(query)
        except json.JSONDecodeError:
            file_paths = [query.strip()]
        else:
            if isinstance(data, list):
                file_paths = data
            elif isinstance(data, dict) and "file_paths" in data:
                file_paths = data["file_paths"]
            else:
                return "错误：JSON 格式不被支持"
            
        if not file_paths:
            return "错误：未提供种子文件路径"
        
        logger.debug(f"待处理的文件路径：{file_paths}")
        results = []
        
        async with httpx.AsyncClient() as client:
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    logger.warning(f"文件不存在：{file_path}")
                    results.append(f"文件不存在：{file_path}")
                    continue
                
                try:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                        file_name = os.path.basename(file_path)
                        files = {'torrents': (file_name, file_content, 'application/x-bittorrent')}
                except Exception as e:
                    logger.error(f"读取文件失败 {file_path}: {str(e)}")
                    results.append(f"读取文件失败 {file_path}: {str(e)}")
                    continue
                
                headers = {
                    "Accept": "*/*",
                    "Host": host.replace('http://', '').replace('https://', '')
                }
                
                logger.debug(f"上传种子文件：{file_name}")
                response = await client.post(
                    f"{host}/api/v2/torrents/add",
                    files=files,
                    cookies=cookies,
                    headers=headers
                )
                
                if response.status_code == 200:
                    logger.info(f"成功添加种子：{file_name}")
                    results.append(f"成功添加种子：{file_name}")
                elif response.status_code == 415:
                    logger.warning(f"无效的种子文件：{file_name}")
                    results.append(f"无效的种子文件：{file_name}")
                else:
                    logger.error(f"添加种子失败 {file_name}: HTTP {response.status_code}")
                    results.append(f"添加种子失败 {file_name}: HTTP {response.status_code}")
        
        result_text = "\n".join(results)
        logger.info(f"添加种子结果：{result_text}")
        return result_text
        
    except json.JSONDecodeError:
        logger.error("JSON 解析失败")
        return "错误：查询字符串不是有效的 JSON 格式"
    except Exception as e:
        logger.error(f"添加种子异常：{str(e)}")
        return f"错误：{str(e)}"


@inject_config
async def delete_torrent_api(hashes: str, delete_files: bool = False, host: str = '', username: str = '', password: str = '') -> str:
    """
    从 qBittorrent 删除种子
    
    Args:
        hashes: 要删除的种子哈希值，多个用 | 分隔，或使用'all'删除所有
        delete_files: 是否同时删除下载的文件
        host: qBittorrent WebUI 地址
        username: 用户名
        password: 密码
        
    Returns:
        删除操作的結果消息
    """
    logger.info(f"删除种子请求：hashes={hashes}, delete_files={delete_files}")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        logger.error("登录失败")
        return "登录失败，无法获取 SID"
    
    try:
        data = {
            "hashes": hashes,
            "deleteFiles": str(delete_files).lower()
        }
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/delete",
                data=data,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"成功删除种子：{hashes}")
                if hashes == "all":
                    return "成功删除所有种子"
                else:
                    return f"成功删除指定种子：{hashes}"
            else:
                logger.error(f"删除种子失败：HTTP {response.status_code}")
                try:
                    error_body = response.json()
                    logger.error(f"错误响应：{error_body}")
                    return f"删除种子失败：HTTP {response.status_code}, {error_body}"
                except:
                    error_body = response.text
                    logger.error(f"错误响应：{error_body}")
                    return f"删除种子失败：HTTP {response.status_code}, {error_body}"
                    
    except Exception as e:
        logger.error(f"删除种子异常：{str(e)}")
        return f"错误：{str(e)}"


@inject_config
async def pause_torrent_api(hashes: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    暂停种子
    
    Args:
        hashes: 要暂停的种子哈希值，多个用 | 分隔，或使用'all'暂停所有
        host: qBittorrent WebUI 地址
        username: 用户名
        password: 密码
        
    Returns:
        暂停操作的結果消息
    """
    logger.info(f"暂停种子请求：hashes={hashes}")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        logger.error("登录失败")
        return "登录失败，无法获取 SID"
    
    try:
        params = {"hashes": hashes}
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/stop",
                data=params,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"成功暂停种子：{hashes}")
                if hashes == "all":
                    return "成功暂停所有种子"
                else:
                    return f"成功暂停指定种子：{hashes}"
            else:
                logger.error(f"暂停种子失败：HTTP {response.status_code}")
                return f"暂停种子失败：HTTP {response.status_code}"
                
    except Exception as e:
        logger.error(f"暂停种子异常：{str(e)}")
        return f"错误：{str(e)}"


@inject_config
async def resume_torrent_api(hashes: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    恢复种子
    
    Args:
        hashes: 要恢复的种子哈希值，多个用 | 分隔，或使用'all'恢复所有
        host: qBittorrent WebUI 地址
        username: 用户名
        password: 密码
        
    Returns:
        恢复操作的結果消息
    """
    logger.info(f"恢复种子请求：hashes={hashes}")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        logger.error("登录失败")
        return "登录失败，无法获取 SID"
    
    try:
        params = {"hashes": hashes}
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/start",
                data=params,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"成功恢复种子：{hashes}")
                if hashes == "all":
                    return "成功恢复所有种子"
                else:
                    return f"成功恢复指定种子：{hashes}"
            else:
                logger.error(f"恢复种子失败：HTTP {response.status_code}")
                return f"恢复种子失败：HTTP {response.status_code}"
                
    except Exception as e:
        logger.error(f"恢复种子异常：{str(e)}")
        return f"错误：{str(e)}"
