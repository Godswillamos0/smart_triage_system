from datetime import timedelta
from fastapi import Request
from starlette.concurrency import run_in_threadpool
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES

async def get_key(request: Request, key:str):
    r = request.app.state.redis
    value = await run_in_threadpool(r.get, key)
    return value


async def set_key(request: Request, key: str, value: str, exp):
    r = request.app.state.redis
    if isinstance(exp, timedelta):
        exp = int(exp.total_seconds())
    
    await run_in_threadpool(r.setex, key, exp, value)
    
async def delete_key(request: Request, key: str):
    r = request.app.state.redis
    await run_in_threadpool(r.delete, key)