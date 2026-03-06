"""
API 模块初始化文件
导出所有 API 函数
"""
from api.auth import login_to_qbittorrent
from api.torrent import (
    add_torrent_api,
    delete_torrent_api,
    pause_torrent_api,
    resume_torrent_api
)
from api.trackers import (
    get_torrent_trackers_urls,
    add_trackers_to_torrent_api
)
from api.limits import (
    set_global_download_limit_api,
    set_global_upload_limit_api,
    set_torrent_download_limit_api,
    set_torrent_upload_limit_api
)
from api.tags import add_torrent_tags_api
from api.search import search_torrents_api
from api.misc import (
    get_application_version_api,
    set_file_priority_api,
    get_torrent_list_api
)

__all__ = [
    # Auth
    'login_to_qbittorrent',
    
    # Torrent
    'add_torrent_api',
    'delete_torrent_api',
    'pause_torrent_api',
    'resume_torrent_api',
    
    # Trackers
    'get_torrent_trackers_urls',
    'add_trackers_to_torrent_api',
    
    # Limits
    'set_global_download_limit_api',
    'set_global_upload_limit_api',
    'set_torrent_download_limit_api',
    'set_torrent_upload_limit_api',
    
    # Tags
    'add_torrent_tags_api',
    
    # Search
    'search_torrents_api',
    
    # Misc
    'get_application_version_api',
    'set_file_priority_api',
    'get_torrent_list_api'
]
