import httpx
from typing import Optional, Dict, Any, List


class RedisApiClient:
    """
    Client for interacting with the FastAPI Redis server.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def set_cache(
        self, key: str, value: str, expiration: Optional[int] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/cache/set"
        payload = {"key": key, "value": value}
        if expiration:
            payload["expiration"] = str(expiration)
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    async def get_cache(self, key: str) -> Optional[str]:
        url = f"{self.base_url}/cache/get/{key}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json().get("value")

    async def invalidate_cache(self, key: str) -> Dict[str, Any]:
        url = f"{self.base_url}/cache/invalidate/{key}"
        async with httpx.AsyncClient() as client:
            response = await client.delete(url)
            response.raise_for_status()
            return response.json()

    async def add_chat_turn(
        self, user_id: str, message: str, role: str
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/history/add"
        payload = {"user_id": user_id, "message": message, "role": role}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    async def get_chat_history(self, user_id: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/history/get/{user_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def clear_chat_history(self, user_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/history/clear/{user_id}"
        async with httpx.AsyncClient() as client:
            response = await client.delete(url)
            response.raise_for_status()
            return response.json()

    async def health_check(self) -> Dict[str, Any]:
        url = f"{self.base_url}/health"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def redis_health_check(self) -> Dict[str, Any]:
        url = f"{self.base_url}/health/redis"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
