# MCP BigQuery Server - Project Brief

## Project Overview

A Model Context Protocol (MCP) server that provides secure access to Google BigQuery datasets through a FastMCP-based Python implementation. The server will be containerized using Docker and use uv for dependency management.

## Core Requirements

### Technical Stack
- **Language**: Python 3.11+
- **Package Manager**: uv
- **MCP Framework**: FastMCP (GoFastMCP)
- **BigQuery Client**: google-cloud-bigquery (v3.38.0+)
- **Container**: Docker
- **Authentication**: Bearer token

### Key Features
1. **BigQuery Operations**
   - Execute SQL queries
   - List datasets and tables
   - Get table schemas
   - Retrieve query results

2. **Security**
   - Bearer token authentication for API requests
   - Secure credential management for BigQuery
   - Environment-based configuration

3. **Containerization**
   - Dockerfile for consistent deployment
   - Docker Compose for local development
   - Environment variable management

## Architecture

```
┌─────────────────┐
│   MCP Client    │
│  (e.g., Claude) │
└────────┬────────┘
         │ Bearer Token Auth
         ▼
┌─────────────────┐
│   MCP Server    │
│   (FastMCP)     │
└────────┬────────┘
         │ Service Account
         ▼
┌─────────────────┐
│  Google BigQuery│
│   API Service   │
└─────────────────┘
```

## Success Criteria

1. ✅ Server runs in Docker container
2. ✅ Successfully authenticates with bearer token
3. ✅ Can execute BigQuery queries
4. ✅ Can list and describe BigQuery resources
5. ✅ Proper error handling and logging
6. ✅ Clear documentation for setup and usage

## Technical Considerations

### BigQuery Authentication
- Use Google Cloud service account JSON key
- Mount credentials securely in Docker
- Support both file-based and environment-based auth

### MCP Protocol
- Implement tools for query execution
- Implement resources for dataset/table listing
- Proper error responses in MCP format

### Dependencies Management with uv
- Fast, reliable dependency resolution
- Lock file for reproducible builds
- Compatible with standard requirements.txt format
