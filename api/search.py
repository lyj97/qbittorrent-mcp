"""
搜索相关 API
提供种子搜索功能
"""
import asyncio
import json
import httpx
from utils.logger import setup_logger
from api.auth import login_to_qbittorrent
from utils.decorators import inject_config
from config import settings

logger = setup_logger(__name__)


@inject_config
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
        category: 搜索类别 (all, movies, anime, books, tv, software 等)
        plugins: 搜索插件 (all 或特定插件)
        max_size_gb: 最大文件大小限制 (GB)
        limit: 结果数量限制
        offset: 结果偏移量
        host: qBittorrent WebUI 地址
        username: 用户名
        password: 密码
    
    Returns:
        搜索结果的 JSON 字符串，包含过滤和排序后的 top 10 结果
    """
    logger.info(f"搜索请求：pattern={pattern}, category={category}, max_size_gb={max_size_gb}")
    
    cookies = await login_to_qbittorrent(username, password, host)
    if not cookies:
        logger.error("登录失败")
        return json.dumps({"error": "登录失败，无法获取 SID"})
    
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
            logger.debug("启动搜索任务")
            response = await client.post(
                f"{host}/api/v2/search/start",
                data=search_data,
                cookies=cookies,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"启动搜索失败：HTTP {response.status_code}")
                return json.dumps({
                    "error": f"启动搜索失败：状态码 {response.status_code}",
                    "response": response.text
                })
            
            # 获取搜索 ID
            search_result = response.json()
            search_id = search_result.get('id')
            
            if not search_id:
                logger.error("未能获取搜索 ID")
                return json.dumps({
                    "error": "未能获取搜索 ID",
                    "response": search_result
                })
            
            logger.info(f"搜索任务已启动，ID: {search_id}")
            
            # Step 2: 轮询获取搜索结果
            torrents = []
            status = None
            
            for attempt in range(settings.search_max_retries):
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
                    logger.error(f"获取搜索结果失败：HTTP {response.status_code}")
                    return json.dumps({
                        "error": f"获取搜索结果失败：状态码 {response.status_code}",
                        "response": response.text
                    })
                
                results = response.json()
                status = results.get('status')
                torrents = results.get('results', [])
                
                logger.debug(f"第{attempt + 1}次轮询：status={status}, results={len(torrents)}")
                
                # 如果搜索完成，跳出循环
                if status == 'Stopped':
                    logger.info(f"搜索完成，获取到 {len(torrents)} 个结果")
                    break
                
                # 如果已有结果且已经尝试多次，返回现有结果
                if torrents and attempt >= 2:
                    logger.info(f"提前返回，获取到 {len(torrents)} 个结果")
                    break
                
                # 等待后重试
                if attempt < settings.search_max_retries - 1:
                    await asyncio.sleep(settings.search_retry_delay)
            
            # 检查是否获取到结果
            if not torrents and status != 'Stopped':
                logger.warning("搜索超时")
                return json.dumps({
                    "error": "搜索超时，未能获取到结果",
                    "search_id": search_id,
                    "status": status
                })
            
            # Step 3: 过滤大于 max_size_gb 的文件
            max_size_bytes = max_size_gb * 1024 * 1024 * 1024
            filtered_torrents = [
                torrent for torrent in torrents 
                if torrent.get('fileSize', 0) <= max_size_bytes
            ]
            
            if len(filtered_torrents) < len(torrents):
                logger.info(f"过滤后剩余 {len(filtered_torrents)}/{len(torrents)} 个结果")
            
            # Step 4: 按 nbSeeders 降序排序
            sorted_torrents = sorted(
                filtered_torrents,
                key=lambda x: x.get('nbSeeders', 0),
                reverse=True
            )
            
            # Step 5: 返回 top 10
            top_10 = sorted_torrents[:10]
            
            result = json.dumps({
                "search_id": search_id,
                "pattern": pattern,
                "total_results": len(torrents),
                "filtered_results": len(filtered_torrents),
                "results": top_10
            }, ensure_ascii=False, indent=2)
            
            logger.info(f"搜索完成，返回 {len(top_10)} 个结果")
            return result
            
    except Exception as e:
        logger.error(f"搜索异常：{str(e)}")
        return json.dumps({
            "error": f"错误：{str(e)}"
        })
