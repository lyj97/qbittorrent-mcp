# qBittorrent MCP Service

qBittorrent MCP is a service based on FastMCP that provides functional interfaces for interacting with the qBittorrent WebUI API.

## Feature List

This service provides the following features:

### Torrent Management
- `add_torrent`: Add torrent files to qBittorrent
- `delete_torrent`: Delete specified torrents (optionally delete files)
- `pause_torrent`: Pause torrent downloads
- `resume_torrent`: Resume torrent downloads
- `get_torrent_list`: Get list of all torrents
- `search_torrents`: Search torrents

### Trackers and Tags
- `get_torrent_trackers`: Get tracker list for a torrent
- `add_trackers_to_torrent`: Add new trackers to a torrent
- `add_torrent_tags`: Add tags to a torrent

### Speed and Priority Control
- `set_global_download_limit`: Set global download speed limit
- `set_global_upload_limit`: Set global upload speed limit
- `set_torrent_download_limit`: Set download speed limit for a specific torrent
- `set_torrent_upload_limit`: Set upload speed limit for a specific torrent
- `set_file_priority`: Set download priority for a specific file

### System Information
- `get_application_version`: Get qBittorrent application version

## Configuration

The service uses the following configuration parameters:
- `QB_HOST`: qBittorrent WebUI host address (default: `http://127.0.0.1:8080`)
- `QB_USERNAME`: qBittorrent WebUI username (default: `admin`)
- `QB_PASSWORD`: qBittorrent WebUI password (default: `adminadmin`)

## Usage

1. Ensure required dependencies are installed:
   ```
   pip install httpx mcp
   ```

2. Run the MCP service:
   ```
   python main.py
   ```

## Docker

1. Build image:
   ```
   docker build -t qbittorrent-mcp .
   ```

2. Run container:
   ```
   docker run --rm -i \
     -e QB_HOST="http://host.docker.internal:8080" \
     -e QB_USERNAME="admin" \
     -e QB_PASSWORD="adminadmin" \
     qbittorrent-mcp
   ```

3. If your torrent files are on host and need to be uploaded by file path, mount them:
   ```
   docker run --rm -i \
     -v /path/to/torrents:/torrents \
     -e QB_HOST="http://host.docker.internal:8080" \
     -e QB_USERNAME="admin" \
     -e QB_PASSWORD="adminadmin" \
     qbittorrent-mcp
   ```

## Development

The service is divided into two main files:
- `main.py`: Defines MCP service interface and configuration parameters
- `api.py`: Implements interaction logic with qBittorrent WebUI
```json
   "mcp_servers": [
        {
            "command": "uv",
            "args": [
                "--directory",
                "/workspace/PC-Canary/apps/qBittorrent/qbittorrent_mcp",
                "run",
                "qbittorrent.py"
            ]
        }
    ]
```
