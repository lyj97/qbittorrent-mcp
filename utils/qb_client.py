"""
qBittorrent HTTP 客户端封装
提供统一的认证和请求方法，自动记录日志
"""
import httpx
from typing import Optional, Dict, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)


class QBClient:
    """qBittorrent API 客户端"""
    
    def __init__(self, host: str, username: str, password: str):
        """
        初始化客户端
        
        Args:
            host: qBittorrent WebUI 地址
            username: 用户名
            password: 密码
        """
        self.host = host.rstrip('/')
        self.username = username
        self.password = password
        self._cookies: Optional[httpx.Cookies] = None
    
    async def login(self) -> bool:
        """
        登录到 qBittorrent WebUI
        
        Returns:
            登录成功返回 True，失败返回 False
        """
        logger.debug(f"尝试登录到 {self.host}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.host}/api/v2/auth/login",
                    data={"username": self.username, "password": self.password}
                )
                
                if response.status_code == 200:
                    self._cookies = response.cookies
                    logger.info("登录成功")
                    return True
                else:
                    logger.error(f"登录失败：HTTP {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"登录异常：{str(e)}")
            return False
    
    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[httpx.Response]:
        """
        发送 HTTP 请求（自动携带认证信息并记录日志）
        
        Args:
            method: HTTP 方法 (GET/POST)
            endpoint: API 端点路径
            params: URL 查询参数
            data: 表单数据
            files: 上传的文件
            headers: HTTP 头
        
        Returns:
            响应对象，失败时返回 None
        """
        if not self._cookies:
            logger.warning("未登录，尝试重新登录")
            if not await self.login():
                return None
        
        url = f"{self.host}{endpoint}"
        
        # 构建默认请求头
        default_headers = {
            "Accept": "*/*",
        }
        if headers:
            default_headers.update(headers)
        
        # 记录请求信息
        logger.debug(f"发送 {method} 请求到 {url}")
        if params:
            logger.debug(f"请求参数：{params}")
        if data:
            logger.debug(f"请求数据：{data}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    files=files,
                    cookies=self._cookies,
                    headers=default_headers
                )
                
                # 记录响应信息
                logger.debug(f"响应状态码：{response.status_code}")
                
                # 如果收到 403，可能是会话过期，尝试重新登录
                if response.status_code == 403:
                    logger.warning("会话可能已过期，尝试重新登录")
                    if await self.login():
                        # 重试一次
                        response = await client.request(
                            method=method,
                            url=url,
                            params=params,
                            data=data,
                            files=files,
                            cookies=self._cookies,
                            headers=default_headers
                        )
                        logger.debug(f"重试后响应状态码：{response.status_code}")
                
                return response
                
        except Exception as e:
            logger.error(f"请求异常：{str(e)}")
            return None
    
    async def get(self, endpoint: str, **kwargs) -> Optional[httpx.Response]:
        """发送 GET 请求"""
        return await self.request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> Optional[httpx.Response]:
        """发送 POST 请求"""
        return await self.request("POST", endpoint, **kwargs)
