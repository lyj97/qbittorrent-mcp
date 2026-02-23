import httpx
import os
import json
import base64
import asyncio
from typing import Dict, List, Union, Optional

# 搜索相关常量
SEARCH_MAX_RETRIES = 10
SEARCH_RETRY_DELAY_SECONDS = 1.0

async def login_to_qbittorrent(username, password, host):
    """
    Login to qBittorrent WebUI and get session cookie
    
    Args:
        username: Username
        password: Password
        host: qBittorrent WebUI host address
        
    Returns:
        Returns object containing session cookie on success, None on failure
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{host}/api/v2/auth/login",
            data={"username": username, "password": password}
        )
    
        if response.status_code == 200:
            return response.cookies
        return None

async def add_torrent_api(query: str, host: str, username: str, password: str) -> str:
    """
    Add torrent files to qBittorrent
    
    Args:
        query: Query string containing torrent file path
        host: qBittorrent WebUI host address
        username: Username
        password: Password
        
    Returns:
        Status and message of the add operation
    """
    # Debug log, write to file
    with open("qbittorrent_debug.log", "a") as f:
        f.write(f"Received query: {query}\n")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    
    try:
        try:
            data = json.loads(query)
        except json.JSONDecodeError:
            # If not valid JSON, assume single file path
            file_paths = [query.strip()]
        else:
            # JSON parsing succeeded, determine result type
            if isinstance(data, list):
                file_paths = data
            elif isinstance(data, dict) and "file_paths" in data:
                file_paths = data["file_paths"]
            else:
                return "Error: JSON format not recognized, please provide required format"
            
        if not file_paths:
            return "Error: No torrent file path provided"
        
        results = []
        async with httpx.AsyncClient() as client:
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    results.append(f"File does not exist: {file_path}")
                    continue
                
                files = {}
                try:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                        file_name = os.path.basename(file_path)
                        files = {'torrents': (file_name, file_content, 'application/x-bittorrent')}
                except Exception as e:
                    results.append(f"Error reading file {file_path}: {str(e)}")
                    continue
                
                # Explicitly set HTTP request headers
                headers = {
                    "Accept": "*/*",
                    "Host": host.replace('http://', '').replace('https://', '')
                }
                
                response = await client.post(
                    f"{host}/api/v2/torrents/add",
                    files=files,
                    cookies=cookies,
                    headers=headers
                )
                
                if response.status_code == 200:
                    results.append(f"Successfully added torrent file: {file_name}")
                elif response.status_code == 415:
                    results.append(f"Invalid torrent file: {file_name}")
                else:
                    results.append(f"Failed to add torrent file {file_name}: status code {response.status_code}")
        
        return "\n".join(results)
    except json.JSONDecodeError:
        return "Error: Query string is not valid JSON format"
    except Exception as e:
        return f"Error: {str(e)}"

async def delete_torrent_api(hashes: str, delete_files: bool = False, host: str = '', username: str = '', password: str = '') -> str:
    """
    Delete torrents from qBittorrent
    
    Args:
        hashes: Torrent hash values to delete, multiple hashes separated by |, or use 'all' to delete all torrents
        delete_files: If True, also delete downloaded files
        host: qBittorrent WebUI host address
        username: Username
        password: Password
        
    Returns:
        Result message of delete operation
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    
    try:
        # Prepare form data
        data = {
            "hashes": hashes,
            "deleteFiles": str(delete_files).lower()
        }
        
        # Set correct Content-Type header
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        
        async with httpx.AsyncClient() as client:
            # Use data parameter instead of json parameter
            response = await client.post(
                f"{host}/api/v2/torrents/delete",
                data=data,  # Use data instead of json
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code == 200:
                if hashes == "all":
                    return "Successfully deleted all torrents"
                else:
                    return f"Successfully deleted specified torrent: {hashes}"
            else:
                # Error handling
                print(f"Failed to delete torrent, HTTP status code: {response.status_code}")
                print(f"Response body: {response.text}")
                try:
                    return f"Failed to delete torrent, HTTP status code: {response.status_code}, response body: {response.json()}"
                except:
                    return f"Failed to delete torrent, HTTP status code: {response.status_code}, response body: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

async def pause_torrent_api(hashes: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    Pause torrents
    
    Args:
        hashes: Torrent hash values to pause, multiple hashes separated by |, or use 'all' to pause all torrents
        host: qBittorrent WebUI host address
        username: Username
        password: Password
        
    Returns:
        Result message of pause operation
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    
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
                if hashes == "all":
                    return "Successfully paused all torrents"
                else:
                    return f"Successfully paused specified torrent: {hashes}"
            else:
                return f"Failed to pause torrent: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

async def resume_torrent_api(hashes: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    Resume torrents
    
    Args:
        hashes: Torrent hash values to resume, multiple hashes separated by |, or use 'all' to resume all torrents
        host: qBittorrent WebUI host address
        username: Username
        password: Password
        
    Returns:
        Result message of resume operation
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    
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
                if hashes == "all":
                    return "Successfully resumed all torrents"
                else:
                    return f"Successfully resumed specified torrent: {hashes}"
            else:
                return f"Failed to resume torrent: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}" 
    
async def get_torrent_trackers_urls(hash: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    Get torrent trackers
    
    Args:
        hash: Torrent hash value to get trackers for
        host: qBittorrent WebUI host address
        username: Username
        password: Password
    
    Returns:
        Formatted string containing torrent trackers
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    try:
        params = {"hash": hash}
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{host}/api/v2/torrents/trackers",
                    params=params,
                    cookies=cookies,
                    headers=headers
                )
            except Exception as e:
                return f"Error: {str(e)}"
            
            if response.status_code == 200:

                trackers = response.json()
                if not trackers:
                    return "This torrent has no trackers"
                
                # Extract all URLs
                tracker_urls = []
                for tracker in trackers:
                    url = tracker.get('url')
                    status = tracker.get('status')
                    msg = tracker.get('msg')
                    
                    # Exclude DHT, PeX, LSD and other special trackers, only get actual URLs
                    if not url.startswith('** ['):
                        tracker_urls.append(f"{url}")
                
                if not tracker_urls:
                    return "This torrent has no valid tracker URLs"
                
                return ",".join(tracker_urls)
            else:
                return f"Failed to get torrent trackers: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"
    
async def set_global_download_limit_api(limit: int, host: str = '', username: str = '', password: str = '') -> str:
    """
    Set global download speed limit
    
    Args:
        limit: Speed limit value, in bytes/second
        host: qBittorrent WebUI host address
        username: Username
        password: Password
    
    Returns:
        Result message of setting speed limit
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
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
                return f"Successfully set speed limit: {limit}"
            else:
                return f"Failed to set speed limit: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}" 
    
async def set_global_upload_limit_api(limit: int, host: str = '', username: str = '', password: str = '') -> str:
    """
    Set global upload speed limit
    
    Args:
        limit: Speed limit value, in bytes/second
        host: qBittorrent WebUI host address
        username: Username
        password: Password

    Returns:
        Result message of setting speed limit
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
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
                headers=headers)
            if response.status_code == 200:
                return f"Successfully set speed limit: {limit}"
            else:
                return f"Failed to set speed limit: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}" 
    
async def get_application_version_api(host: str = '', username: str = '', password: str = '') -> str:
    """
    Get qBittorrent version
    
    Returns:
        qBittorrent version
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
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
                return response.text.strip()
            else:
                return f"Failed to get qBittorrent version: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}" 
    
async def set_file_priority_api(hash: str, id: str, priority: int, host: str = '', username: str = '', password: str = '') -> str:
    """
    Set file priority
    
    Args:
        hash: Torrent hash value
        id: correspond to file position inside the array returned by torrent contents API, e.g. id=0 for first file, id=1 for second file, etc.
        priority: 
        Value	Description
        0	Do not download
        1	Normal priority
        6	High priority
        7	Maximal priority
        
    Returns:
        Result message of setting file priority
        HTTP Status Code	Scenario
        400	Priority is invalid
        400	At least one file id is not a valid integer
        404	Torrent hash was not found
        409	Torrent metadata hasn't downloaded yet
        409	At least one file id was not found
        200	All other scenarios
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    try:
        params = {"hash": hash, "id": id, "priority": priority}
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{host}/api/v2/torrents/filePrio",
                data=params,
                cookies=cookies,
                headers=headers)
            if response.status_code == 200:
                return f"Successfully set file priority: {hash}:{id}:{priority}"
            else:
                return f"Failed to set file priority: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

async def set_torrent_download_limit_api(hash: str, limit: int, host: str = '', username: str = '', password: str = '') -> str:
    """
    Set torrent download speed limit
    
    Args:
        hash: Torrent hash value
        limit: Speed limit value, in bytes/second
        host: qBittorrent WebUI host address
        username: Username
        password: Password
    
    Returns:
        Result message of setting torrent download speed limit
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
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
                headers=headers)
            if response.status_code == 200:
                return f"Successfully set torrent download speed limit: {hash}:{limit}"
            else:
                return f"Failed to set torrent download speed limit: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"
    

async def set_torrent_upload_limit_api(hash: str, limit: int, host: str = '', username: str = '', password: str = '') -> str:
    """
    Set torrent upload speed limit
    
    Args:
        hash: Torrent hash value
        limit: Speed limit value, in bytes/second
        host: qBittorrent WebUI host address
        username: Username
        password: Password
    
    Returns:
        Result message of setting torrent upload speed limit
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
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
                headers=headers)
            if response.status_code == 200:
                return f"Successfully set torrent upload speed limit: {hash}:{limit}"
            else:
                return f"Failed to set torrent upload speed limit: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}" 

async def add_trackers_to_torrent_api(hash: str, trackers: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    Add trackers to torrent
    
    Args:
        hash: Torrent hash value
        trackers: Tracker URLs as a string. Multiple URLs should be separated by the literal string "%0A" (URL-encoded newline)
        host: qBittorrent WebUI host address
        username: Username
        password: Password
        
    Example:
        hash=8c212779b4abde7c6bc608063a0d008b7e40ce32&urls=http://192.168.0.1/announce%0Audp://192.168.0.1:3333/dummyAnnounce
        
    Returns:
        Result message of adding trackers
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
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
                headers=headers)
            if response.status_code == 200:
                return f"Successfully added trackers: {hash}:{trackers}"
            else:
                return f"Failed to add trackers: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

async def add_torrent_tags_api(hash: str, tags: str, host: str = '', username: str = '', password: str = '') -> str:
    """
    Add torrent tags
    
    Args:
        hash: Torrent hash value (or multiple hashes separated by |)
        tags: Tags as a comma-separated string (e.g., "TagName1,TagName2")
        host: qBittorrent WebUI host address
        username: Username
        password: Password

    Example:
        hashes=8c212779b4abde7c6bc608063a0d008b7e40ce32|284b83c9c7935002391129fd97f43db5d7cc2ba0&tags=TagName1,TagName2
    
    Returns:
        Result message of adding torrent tags
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
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
                headers=headers)
            if response.status_code == 200:
                return f"Successfully added torrent tags: {hash}:{tags}"
            else:
                return f"Failed to add torrent tags: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

async def get_torrent_list_api(host: str = '', username: str = '', password: str = '') -> str:
    """
    Get torrent list
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return "Login failed, unable to get SID"
    try:
        headers = {
            "Accept": "*/*",
        }
        
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{host}/api/v2/torrents/info",
                cookies=cookies,
                headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return f"Failed to get torrent list: status code {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

async def search_torrents_api(
    pattern: str,
    category: str = 'all',
    plugins: str = 'all',
    max_size_gb: float = 5.0,
    limit: int = 100,
    offset: int = 0,
    host: str = '',
    username: str = '',
    password: str = ''
) -> str:
    """
    搜索种子
    
    Args:
        pattern: 搜索关键词
        category: 搜索类别 (all, movies, anime, books, tv, software等)，默认为all
        plugins: 搜索插件 (all或特定插件)，默认为all
        max_size_gb: 最大文件大小限制(GB)，默认为5GB
        limit: 内部参数，控制API返回的结果数量，默认为100
        offset: 内部参数，控制结果偏移量，默认为0
        host: qBittorrent WebUI主机地址
        username: 用户名
        password: 密码
    
    Returns:
        搜索结果的JSON字符串，包含过滤和排序后的top 10结果
    """
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        return json.dumps({"error": "登录失败，无法获取SID"})
    
    try:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        
        # Step 1: 启动搜索
        search_data = {
            "pattern": pattern,
            "category": category,
            "plugins": plugins
        }
        
        async with httpx.AsyncClient() as client:
            # 启动搜索
            response = await client.post(
                f"{host}/api/v2/search/start",
                data=search_data,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code != 200:
                return json.dumps({
                    "error": f"启动搜索失败: 状态码 {response.status_code}",
                    "response": response.text
                })
            
            # 获取搜索ID
            search_result = response.json()
            search_id = search_result.get('id')
            
            if not search_id:
                return json.dumps({
                    "error": "未能获取搜索ID",
                    "response": search_result
                })
            
            # Step 2: 轮询获取搜索结果，带超时机制
            torrents = []
            status = None
            
            for attempt in range(SEARCH_MAX_RETRIES):
                results_data = {
                    "id": search_id,
                    "limit": limit,
                    "offset": offset
                }
                
                response = await client.post(
                    f"{host}/api/v2/search/results",
                    data=results_data,
                    cookies=cookies,
                    headers=headers
                )
                
                if response.status_code != 200:
                    return json.dumps({
                        "error": f"获取搜索结果失败: 状态码 {response.status_code}",
                        "response": response.text
                    })
                
                results = response.json()
                status = results.get('status')
                torrents = results.get('results', [])
                
                # 如果搜索完成，跳出循环
                if status == 'Stopped':
                    break
                
                # 如果已有结果且已经尝试多次，返回现有结果
                if torrents and attempt >= 2:
                    break
                
                # 如果还在运行，等待后重试
                if attempt < SEARCH_MAX_RETRIES - 1:
                    await asyncio.sleep(SEARCH_RETRY_DELAY_SECONDS)
            
            # 检查是否获取到结果
            if not torrents and status != 'Stopped':
                return json.dumps({
                    "error": "搜索超时，未能获取到结果",
                    "search_id": search_id,
                    "status": status
                })
            
            # Step 3: 过滤大于max_size_gb的文件
            max_size_bytes = max_size_gb * 1024 * 1024 * 1024  # 转换为字节
            filtered_torrents = [
                torrent for torrent in torrents 
                if torrent.get('fileSize', 0) <= max_size_bytes
            ]
            
            # Step 4: 按nbSeeders降序排序
            sorted_torrents = sorted(
                filtered_torrents,
                key=lambda x: x.get('nbSeeders', 0),
                reverse=True
            )
            
            # Step 5: 返回top 10
            top_10 = sorted_torrents[:10]
            
            return json.dumps({
                "search_id": search_id,
                "pattern": pattern,
                "total_results": len(torrents),
                "filtered_results": len(filtered_torrents),
                "results": top_10
            }, ensure_ascii=False, indent=2)
            
    except Exception as e:
        return json.dumps({
            "error": f"错误: {str(e)}"
        })
    
    