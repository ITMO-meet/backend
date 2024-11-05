from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from minio import Minio

load_dotenv()


class Database:
    def __init__(self):
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI not found in env")

        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client["meet"]

        minio_endpoint = os.getenv("MINIO_ENDPOINT")
        minio_access_key = os.getenv("MINIO_ACCESS_KEY")
        minio_secret_key = os.getenv("MINIO_SECRET_KEY")
        self.minio_bucket_name = os.getenv("MINIO_BUCKET_NAME")
        minio_use_ssl = os.getenv("MINIO_USE_SSL", "False").lower() == "true"

        if not all(
            [minio_endpoint, minio_access_key, minio_secret_key, self.minio_bucket_name]
        ):
            raise ValueError("MINIO not found in env")

        self.minio_instance = Minio(
            minio_endpoint, minio_access_key, minio_secret_key, secure=minio_use_ssl
        )

        if not self.minio_instance.bucket_exists(self.minio_bucket_name):
            self.minio_instance.make_bucket(self.minio_bucket_name)

    def upload_file_to_minio(self, data, filename, content_type):
        self.minio_instance.put_object(
            self.minio_bucket_name,
            filename,
            data,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type=content_type,
        )
        return f"{self.minio_bucket_name}/{filename}"

    def get_collection(self, collection_name):
        return self.db[collection_name]

    async def get_available_tags(self):
        tags = await self.db["tags"].find().to_list(length=None)
        return [tag["name"] for tag in tags]

    async def add_test_tags(self, tags: List[Dict[str, Any]]):
        result = await self.db["tags"].insert_many(tags)
        return [str(tag_id) for tag_id in result.inserted_ids]


db_instance = Database()
