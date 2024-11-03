from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

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
    
    # async def get_available_tags(self):
    #     tags = await self.db["tags"].find().to_list(length=None)
    #     return [tag["name"] for tag in tags]
    
    # async def update_user_tags(self, selected_tags):
    #     user = {"tags": selected_tags}
    #     result = await self.db["users"].insert_one(user)
    #     return str(result.inserted_id)


db_instance = Database()
