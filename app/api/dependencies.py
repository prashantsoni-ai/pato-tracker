from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from ..db.database import db_manager
from ..services.query_processor import QueryProcessor
from ..core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

async def get_query_processor():
    async with db_manager.get_session() as session:
        yield QueryProcessor(session)
