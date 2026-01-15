# FastAPI Custom Auth & RBAC System

## Prerequisites
UV and Docker are required

## Setup
```bash
# Windows CMD -> 'copy .env.example .env'
cp .env.example .env
docker-compose up -d
uv sync
uv run alembic upgrade head
uv run python initial_data.py
uv run uvicorn app.main:app --reload
```
## Default Accounts
**Admin:**
- Email: admin@example.com
- Password: admin123
- Access: Full access to all resources

**User:**
- Email: user@example.com
- Password: user123
- Access: Access only to your orders