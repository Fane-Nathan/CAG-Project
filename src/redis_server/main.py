from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.redis_server.database import RedisClient
from src.redis_server.cache_routes import router as cache_router
from src.redis_server.history_routes import router as history_router
from src.redis_server.health_routes import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    print("FastAPI app starting up...")
    # Redis clients are initialized on first use via Depends, but we can ensure connection here if needed
    # await RedisClient.get_cache_client()
    # await RedisClient.get_history_client()
    yield
    # Shutdown event
    print("FastAPI app shutting down...")
    await RedisClient.close_connections()


app = FastAPI(
    lifespan=lifespan,
    title="Redis Cache and History API",
    description="API for managing Redis cache and chat history for the AI agent.",
    version="1.0.0",
)

app.include_router(cache_router, prefix="/cache", tags=["Cache Management"])
app.include_router(history_router, prefix="/history", tags=["Chat History Management"])
app.include_router(health_router, prefix="/health", tags=["Health Checks"])
