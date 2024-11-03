from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()


class Database:
    def __init__(self):
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI not found in env")

        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client["meet"]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    async def get_available_tags(self):
        tags = await self.db["tags"].find().to_list(length=None)
        return [tag["name"] for tag in tags]

    async def add_test_tags(self, tags: List[Dict[str, Any]]):
        result = await self.db["tags"].insert_many(tags)
        return [str(tag_id) for tag_id in result.inserted_ids]

    async def update_user_fields(
        self, isu: int, update_fields: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        collection = self.get_collection("users")

        result = await collection.update_one(
            {"isu": ObjectId(isu)}, {"$set": update_fields}
        )

        if result.modified_count > 0:
            updated_user = await collection.find_one({"isu": ObjectId(isu)})
            return updated_user
        else:
            return None


db_instance = Database()
