from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from minio import Minio
from bson import ObjectId

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
    
    async def get_special_tags(self):
        special_tags = await self.db["tags"].find({"is_special": 1}).to_list(length=None)
        return [{"id": str(tag["_id"]), "name": tag["name"]} for tag in special_tags]


    async def add_test_tags(self, tags: List[Dict[str, Any]]):
        result = await self.db["tags"].insert_many(tags)
        return [str(tag_id) for tag_id in result.inserted_ids]

    async def create_test(
        self, name: str, description: str, question_ids: List[ObjectId]
    ):
        test_data = {
            "name": name,
            "description": description,
            "question_ids": question_ids,
        }
        result = await self.db["tests"].insert_one(test_data)
        return str(result.inserted_id)

    async def get_test(self, test_id: str):
        return await self.db["tests"].find_one({"_id": ObjectId(test_id)})

    async def create_question(self, description: str):
        question_data = {"description": description}
        result = await self.db["questions"].insert_one(question_data)
        return str(result.inserted_id)

    async def get_question_by_id(self, question_id: str):
        question = await self.db["questions"].find_one({"_id": ObjectId(question_id)})
        return question

    # review
    async def create_result(self, user_id: int, test_id: str, questions_count: int):
        result_data = {
            "user_id": user_id,
            "test_id": ObjectId(test_id),
            "answers": [-1] * questions_count,
            "score": None,
            "completed": False,
        }
        result = await self.db["results"].insert_one(result_data)
        return str(result.inserted_id)

    async def update_result(self, result_id: str, question_index: int, answer: int):
        result = await self.db["results"].find_one({"_id": ObjectId(result_id)})

        if not result or result["completed"]:
            return None

        answers = result["answers"]
        if question_index < 0 or question_index >= len(answers):
            return None
        answers[question_index] = answer

        await self.db["results"].update_one(
            {"_id": ObjectId(result_id)}, {"$set": {"answers": answers}}
        )
        return answers

    async def get_answers(self, result_id: str):
        result = await self.db["results"].find_one({"_id": ObjectId(result_id)})
        if not result:
            return None
        return result["answers"]

    async def get_status(self, result_id: str):
        status = await self.db["results"].find_one({"_id": ObjectId(result_id)})
        if not status:
            return None
        return status["completed"]

    async def complete_test(self, result_id: str):
        result = await self.db["results"].find_one({"_id": ObjectId(result_id)})
        if not result:
            return None

        score = sum(result["answers"]) / (len(result["answers"]) * 6) * 100
        await self.db["results"].update_one(
            {"_id": ObjectId(result_id)}, {"$set": {"score": score, "completed": True}}
        )
        return score

    async def get_result(self, result_id: str):
        result = await self.db["results"].find_one({"_id": ObjectId(result_id)})
        return result

        return [str(tag_id) for tag_id in result.inserted_ids]


db_instance = Database()
