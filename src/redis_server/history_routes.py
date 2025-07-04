from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio.client import Redis
from typing import List, Dict, Any
import json

from src.redis_server.database import get_redis_history_client

router = APIRouter()


@router.post("/add")
async def add_chat_turn(
    user_id: str,
    message: str,
    role: str,
    history_client: Redis = Depends(get_redis_history_client),
):
    """
    Adds a new chat turn to a user's history.
    The history is stored as a list of JSON strings in Redis.
    """
    try:
        history_key = f"history:{user_id}"
        chat_turn = {"message": message, "role": role}
        await history_client.rpush(history_key, json.dumps(chat_turn))  # type: ignore
        return {"message": f"Chat turn added for user '{user_id}'."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add chat turn: {e}")


@router.get("/get/{user_id}")
async def get_chat_history(
    user_id: str, history_client: Redis = Depends(get_redis_history_client)
) -> List[Dict[str, Any]]:
    """
    Retrieves the full chat history for a given user.
    """
    try:
        history_key = f"history:{user_id}"
        history_raw = await history_client.lrange(history_key, 0, -1)  # type: ignore
        history = [json.loads(turn) for turn in history_raw]
        return history
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve chat history: {e}"
        )


@router.delete("/clear/{user_id}")
async def clear_chat_history(
    user_id: str, history_client: Redis = Depends(get_redis_history_client)
):
    """
    Clears the entire chat history for a given user.
    """
    try:
        history_key = f"history:{user_id}"
        deleted_count = await history_client.delete(history_key)
        if deleted_count == 0:
            raise HTTPException(
                status_code=404, detail=f"Chat history for user '{user_id}' not found."
            )
        return {"message": f"Chat history cleared for user '{user_id}'."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to clear chat history: {e}"
        )
