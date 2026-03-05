#!/usr/bin/env bash
set -euo pipefail

# 默认参数
IMAGE_NAME="qbittorrent-mcp"
IMAGE_TAG="latest"
PLATFORM=""
NO_CACHE=false

usage() {
  cat <<'EOF'
用法:
  bash build-image.sh [选项]

选项:
  -n, --name <name>        镜像名称（默认: qbittorrent-mcp）
  -t, --tag <tag>          镜像标签（默认: latest）
  -p, --platform <value>   目标平台（例如: linux/amd64）
      --no-cache           构建时不使用缓存
  -h, --help               查看帮助

示例:
  bash build-image.sh
  bash build-image.sh -n my-qb-mcp -t v1.0.0
  bash build-image.sh -p linux/amd64 --no-cache
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -n|--name)
      IMAGE_NAME="${2:-}"
      shift 2
      ;;
    -t|--tag)
      IMAGE_TAG="${2:-}"
      shift 2
      ;;
    -p|--platform)
      PLATFORM="${2:-}"
      shift 2
      ;;
    --no-cache)
      NO_CACHE=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "未知参数: $1"
      usage
      exit 1
      ;;
  esac
done

if [[ -z "${IMAGE_NAME}" || -z "${IMAGE_TAG}" ]]; then
  echo "错误: 镜像名称和标签不能为空"
  exit 1
fi

# 保证在脚本所在目录执行，避免从其他目录运行时上下文错误
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

CMD=(docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .)

if [[ -n "${PLATFORM}" ]]; then
  CMD=(docker build --platform "${PLATFORM}" -t "${IMAGE_NAME}:${IMAGE_TAG}" .)
fi

if [[ "${NO_CACHE}" == "true" ]]; then
  CMD+=(--no-cache)
fi

echo "开始构建镜像: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "执行命令: ${CMD[*]}"
"${CMD[@]}"
echo "构建完成: ${IMAGE_NAME}:${IMAGE_TAG}"
