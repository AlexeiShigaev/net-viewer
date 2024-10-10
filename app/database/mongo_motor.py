from typing import Optional

import motor.motor_asyncio
from pydantic import BaseModel


class MongoMotorEngine:
    _connection_uri: str
    _db_name: str
    _client: Optional[motor.motor_asyncio.AsyncIOMotorClient]
    _db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase]

    def __init__(self, connection_uri: str, database: str):
        """
        Для инициализации подключения указать connection URI
        В стиле 'mongodb://localhost:27017'
        Таким образом экземпляр будет привязан к конкретному хосту, порту и базе.
        """
        self._connection_uri = connection_uri
        self._db_name = database
        self._client = None
        self._db = None

    def is_connected(self, disconnect: bool = False) -> bool:
        if disconnect:
            if self._client is not None:
                # TODO check flush
                self._client.close()
            self._client, self._db = (None, None)
            return False
        if self._client is None:
            self._client = motor.motor_asyncio.AsyncIOMotorClient(self._connection_uri)
            self._db = self._client[self._db_name]
        return True

    async def insert_one(self, collection: str, document: BaseModel):
        if self.is_connected():
            result = await self._db[collection].insert_one(document.model_dump())
            return result
        return None

    def find(self, collection, find_filter: dict):
        if self.is_connected():
            return self._db[collection].find(filter=find_filter)
        return None

    async def find_one(self, collection, find_filter: dict):
        if self.is_connected():
            return await self._db[collection].find_one(filter=find_filter)
        return None

    async def drop_collection(self, collection):
        if self.is_connected():
            return await self._db.drop_collection(collection)
        return None

    async def update_one(self, collection, find_filter: dict, new_data: dict):
        if self.is_connected():
            return await self._db[collection].update_one(filter=find_filter, update=new_data, upsert=True)
        return None

    async def update_many(self, collection, find_filter: dict, new_data: dict):
        if self.is_connected():
            return await self._db[collection].update_many(filter=find_filter, update=new_data, upsert=True)
        return None
