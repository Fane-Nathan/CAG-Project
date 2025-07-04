from redis.asyncio.client import Redis
from typing import List, Dict, Any
import json


class HistoryService:
    """
    A service for managing chat history in Redis.
    """

    def __init__(self, settings):
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    async def add_turn(self, user_id: str, message: str, role: str):
        """
        Adds a turn to the chat history.
        """
        history_key = f"history:{user_id}"
        chat_turn = {"message": message, "role": role}
        await self.redis.rpush(history_key, json.dumps(chat_turn))

    async def get_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Gets the chat history for a user.
        """
        history_key = f"history:{user_id}"
        history_raw = await self.redis.lrange(history_key, 0, -1)
        history = [json.loads(turn) for turn in history_raw]
        return history

    async def clear_history(self, user_id: str):
        """
        Clears the chat history for a user.
        """
        history_key = f"history:{user_id}"
        await self.redis.delete(history_key)
