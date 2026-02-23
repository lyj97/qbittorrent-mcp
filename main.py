import httpx
from mcp.server import FastMCP
import base64
import os
import json
import uuid
from api import (
    login_to_qbittorrent,
    add_torrent_api,
    delete_torrent_api,
    pause_torrent_api,
    resume_torrent_api,
    get_torrent_trackers_urls,
    set_global_download_limit_api,
    set_global_upload_limit_api,
    get_application_version_api,
    set_file_priority_api,
    set_torrent_download_limit_api,
    set_torrent_upload_limit_api,
    add_trackers_to_torrent_api,
    add_torrent_tags_api,
    get_torrent_list_api,
    search_torrents_api
)

# Define key parameters
DEFAULT_HOST = 'http://127.0.0.1:8080'
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'adminadmin'

# Initialize FastMCP server
app = FastMCP('qbittorrent')

@app.tool()
async def add_torrent(query: str) -> str:
    """
    Add torrent files to qBittorrent
    
    Args:
        query: Query string containing torrent file path, supports the following formats:
               1. JSON string: "{\"file_paths\": [\"path/to/file1.torrent\", \"path/to/file2.torrent\"]}"
               2. JSON string: "[\"path/to/file1.torrent\", \"path/to/file2.torrent\"]"
               3. Single file path: "path/to/file.torrent"
        
    Returns:
        Status and message of the add operation
    """
    return await add_torrent_api(query, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def delete_torrent(hashes: str, delete_files: bool = False) -> str:
    """
    Delete torrents from qBittorrent
    
    Args:
        hashes: Torrent hash values to delete, multiple hashes separated by |, or use 'all' to delete all torrents
        delete_files: If True, also delete downloaded files
        
    Returns:
        Result message of delete operation
    """
    return await delete_torrent_api(hashes, delete_files, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def pause_torrent(hashes: str) -> str:
    """
    Pause torrents
    
    Args:
        hashes: Torrent hash values to pause, multiple hashes separated by |, or use 'all' to pause all torrents
        
    Returns:
        Result message of pause operation
    """
    return await pause_torrent_api(hashes, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def resume_torrent(hashes: str) -> str:
    """
    Resume torrents
    
    Args:
        hashes: Torrent hash values to resume, multiple hashes separated by |, or use 'all' to resume all torrents
        
    Returns:
        Result message of resume operation
    """
    return await resume_torrent_api(hashes, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def get_torrent_trackers(hash: str) -> str:
    """
    Get torrent trackers
    
    Args:
        hash: Torrent hash value
        
    Returns:
        String containing tracker information
    """
    return await get_torrent_trackers_urls(hash, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def set_global_download_limit(limit: int) -> str:
    """
    Set global download speed limit
    
    Args:
        limit: Speed limit value, in bytes/second
        
    Returns:
        Result message of setting speed limit
    """ 
    return await set_global_download_limit_api(limit)

@app.tool()
async def set_global_upload_limit(limit: int) -> str:
    """
    Set global upload speed limit
    
    Args:
        limit: Speed limit value, in bytes/second
        
    Returns:
        Result message of setting speed limit
    """
    return await set_global_upload_limit_api(limit)

@app.tool()
async def get_application_version() -> str:
    """
    Get qBittorrent version
    
    Returns:
        qBittorrent version
    """
    return await get_application_version_api()

@app.tool()
async def set_file_priority(hash: str, id: str, priority: int) -> str:
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
    return await set_file_priority_api(hash, id, priority, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def set_torrent_download_limit(hash: str, limit: int) -> str:
    """
    Set torrent download speed limit
    
    Args:
        hash: Torrent hash value
        limit: Speed limit value, in bytes/second
        
    Returns:
        Result message of setting torrent download speed limit
    """
    return await set_torrent_download_limit_api(hash, limit, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def set_torrent_upload_limit(hash: str, limit: int) -> str:
    """
    Set torrent upload speed limit
    
    Args:
        hash: Torrent hash value
        limit: Speed limit value, in bytes/second
        
    Returns:
        Result message of setting torrent upload speed limit
    """ 
    return await set_torrent_upload_limit_api(hash, limit, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def add_trackers_to_torrent(hash: str, trackers: str) -> str:
    """
    Add trackers to torrent
    
    Args:
        hash: Torrent hash value
        trackers: Tracker URL, multiple URLs separated by %0A
        
    Returns:
        Result message of adding trackers
    """
    return await add_trackers_to_torrent_api(hash, trackers, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def add_torrent_tags(hash: str, tags: str) -> str:
    """
    Add torrent tags
    
    Args:
        hash: Torrent hash value
        tags: Tag list, multiple tags separated by comma
        
    Returns:
        Result message of adding torrent tags
    """
    return await add_torrent_tags_api(hash, tags, DEFAULT_HOST, DEFAULT_USERNAME, DEFAULT_PASSWORD)

@app.tool()
async def get_torrent_list() -> str:
    """
    Get torrent list
    """
    return await get_torrent_list_api(host=DEFAULT_HOST, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD)

@app.tool()
async def search_torrents(
    pattern: str,
    category: str = 'all',
    plugins: str = 'all',
    max_size_gb: float = 5.0
) -> str:
    """
    搜索种子
    
    Args:
        pattern: 搜索关键词
        category: 搜索类别 (all, movies, anime, books, tv, software等)，默认为all
        plugins: 搜索插件 (all或特定插件)，默认为all
        max_size_gb: 最大文件大小限制(GB)，默认为5GB。结果会过滤掉大于此大小的文件
        
    Returns:
        搜索结果的JSON字符串，包含过滤和排序后的top 10结果，按种子数(nbSeeders)降序排列
    """
    return await search_torrents_api(
        pattern=pattern,
        category=category,
        plugins=plugins,
        max_size_gb=max_size_gb,
        host=DEFAULT_HOST,
        username=DEFAULT_USERNAME,
        password=DEFAULT_PASSWORD
    )

if __name__ == "__main__":
    app.run(transport='stdio')
