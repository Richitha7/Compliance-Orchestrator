from __future__ import annotations
from typing import Any, Dict
import os, json, asyncio
from datetime import datetime
from ..utils.config import settings

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except Exception:
    AsyncIOMotorClient = None  # type: ignore

class Store:
    """Mongo store with JSON file fallback."""
    def __init__(self):
        self._mongo = None
        self._db = None
        self.fallback_dir = "data/fallback"
        os.makedirs(self.fallback_dir, exist_ok=True)

    async def init(self):
        if AsyncIOMotorClient and settings.MONGODB_URI:
            self._mongo = AsyncIOMotorClient(settings.MONGODB_URI)
            self._db = self._mongo[settings.MONGODB_DB]

    async def append_history(self, session_id: str, entry: Dict[str, Any]):
        if self._db:
            await self._db.history.update_one(
                {"session_id": session_id},
                {"$push": {"entries": entry}},
                upsert=True
            )
        else:
            path = os.path.join(self.fallback_dir, f"{session_id}.json")
            data = {"session_id": session_id, "entries": []}
            if os.path.exists(path):
                data = json.load(open(path, "r"))
            data["entries"].append(entry)
            json.dump(data, open(path, "w"))

    async def get_history(self, session_id: str) -> Dict[str, Any]:
        if self._db:
            doc = await self._db.history.find_one({"session_id": session_id})
            return doc or {"session_id": session_id, "entries": []}
        else:
            path = os.path.join(self.fallback_dir, f"{session_id}.json")
            if os.path.exists(path):
                return json.load(open(path, "r"))
            return {"session_id": session_id, "entries": []}

store = Store()
