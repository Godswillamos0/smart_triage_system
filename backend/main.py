from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis

from app.db import models
from app.db.database import engine
from app.api.v1 import router
from app.core.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

app = FastAPI(title="Smart Triage System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
   
    models.Base.metadata.create_all(bind=engine)
    

    app.state.redis = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        username="default",
        password=REDIS_PASSWORD,
    )
    print(f"INFO: Connected to Redis at {REDIS_HOST}")

@app.on_event("shutdown")
async def shutdown_event():
    if hasattr(app.state, "redis"):
        app.state.redis.close()


app.include_router(router.endpoint)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)