# REST API Documentation

AENTS provides a FastAPI service with OpenAPI specification at `/docs`.

## Key Endpoints
- `POST /api/v1/tasks`: Dispatch new task
- `GET /api/v1/tasks/{task_id}`: Retrieve task details
- `GET /api/v1/tasks/{task_id}/trace`: Retrieve execution trace
- `GET /api/v1/agents`: List registered specialist agents and performance metrics
- `GET /api/v1/events`: Real-time Server-Sent Events (SSE) stream
- `POST /api/v1/approvals/{approval_id}/approve`: Approve HITL request
- `GET /health` & `GET /metrics`: Service health and metrics
