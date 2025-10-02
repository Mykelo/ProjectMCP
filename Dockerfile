# Multi-stage Dockerfile for MCP BigQuery Server
# Stage 1: Build stage with uv
FROM python:3.13-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Copy source code
COPY src/ ./src/

# Install dependencies
RUN uv sync --no-dev

# Stage 2: Runtime stage
FROM python:3.13-slim

# Create non-root user
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --from=builder /app/src /app/src
COPY --from=builder /app/pyproject.toml /app/

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV HOME=/app

# Create directory for credentials (to be mounted)
RUN mkdir -p /app/credentials && chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Expose port (optional, for SSE transport)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app/src'); from mcp_bigquery.config import get_settings; get_settings()" || exit 1

# Run the FastAPI application
CMD ["uvicorn", "src.mcp_bigquery.server:app", "--host", "0.0.0.0", "--port", "8000"]
