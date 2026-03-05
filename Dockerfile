FROM registry.cn-beijing.aliyuncs.com/lu97/python:3.11-slim

WORKDIR /app

# Copy source files
COPY main.py api.py ./

# Install runtime dependencies
RUN pip install --no-cache-dir httpx "mcp[cli]"

CMD ["python", "main.py"]
