import datetime
import os
from typing import Any, Dict, List, Optional

from bson import ObjectId
from dotenv import load_dotenv
from minio import Minio
from motor.motor_asyncio import AsyncIOMotorClient

from app.setup_rollbar import rollbar_handler

from .fill_many import (
    create_chats,
    create_interactions,
    create_messages,
    create_questions,
    create_results,
    create_stories,
    create_tags,
    create_tests,
    create_users,
)

load_dotenv()


class Database:
    test_env = ["dev", "test"]

    def __init__(self):
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI not found in env")

        self.client = AsyncIOMotorClient(mongo_uri)

        self.environment = os.getenv("ENVIRONMENT", "prod")

        if self.is_test_env:
            self.db_name = "meet-test"
            self.db = self.client[self.db_name]
            self.minio_bucket_name = os.getenv("MINIO_BUCKET_NAME") + "-test"
        else:
            self.db_name = "meet"
            self.db = self.client[self.db_name]
            self.minio_bucket_name = os.getenv("MINIO_BUCKET_NAME")

        minio_endpoint = os.getenv("MINIO_ENDPOINT")
        minio_access_key = os.getenv("MINIO_ACCESS_KEY")
        minio_secret_key = os.getenv("MINIO_SECRET_KEY")
        minio_use_ssl = os.getenv("MINIO_USE_SSL", "False").lower() == "true"

        if not all([minio_endpoint, minio_access_key, minio_secret_key, self.minio_bucket_name]):
            raise ValueError("MINIO not found in env")

        self.minio_instance = Minio(minio_endpoint, minio_access_key, minio_secret_key, secure=minio_use_ssl)

        if not self.minio_instance.bucket_exists(self.minio_bucket_name):
            self.minio_instance.make_bucket(self.minio_bucket_name)

        if self.is_test_env:
            self.setup_test_db()

    @property
    def is_test_env(self) -> bool:
        return self.environment in self.test_env

    @rollbar_handler
    def setup_test_db(self):
        if not self.is_test_env:
            return

        # Cleanup test database
        self.client.drop_database(self.db_name)

        self.db["users"].delete_many({})
        self.db["chats"].delete_many({})
        self.db["messages"].delete_many({})
        self.db["tags"].delete_many({})
        self.db["questions"].delete_many({})
        self.db["tests"].delete_many({})
        self.db["results"].delete_many({})
        self.db["stories"].delete_many({})
        self.db["interactions"].delete_many({})

        # Create sample data
        special_tags, normal_tags = create_tags()
        user_ids = create_users(normal_tags, special_tags)
        chat_ids = create_chats(user_ids)
        create_messages(chat_ids)
        create_interactions(user_ids)
        question_ids = create_questions()
        test_ids = create_tests(question_ids)
        create_results(user_ids, test_ids)
        create_stories(user_ids)

    @rollbar_handler
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

    @rollbar_handler
    def get_collection(self, collection_name):
        return self.db[collection_name]

    @rollbar_handler
    async def get_available_tags(self):
        tags = await self.db["tags"].find().to_list(length=None)
        return [{"id": str(tag["_id"]), "name": tag["name"]} for tag in tags]

    @rollbar_handler
    async def get_special_tags(self):
        special_tags = await self.db["tags"].find({"is_special": 1}).to_list(length=None)
        return [{"id": str(tag["_id"]), "name": tag["name"]} for tag in special_tags]

    @rollbar_handler
    async def add_test_tags(self, tags: List[Dict[str, Any]]):
        result = await self.db["tags"].insert_many(tags)
        return [str(tag_id) for tag_id in result.inserted_ids]

    @rollbar_handler
    async def create_test(self, name: str, description: str, question_ids: List[ObjectId]):
        test_data = {
            "name": name,
            "description": description,
            "question_ids": question_ids,
        }
        result = await self.db["tests"].insert_one(test_data)
        return str(result.inserted_id)

    @rollbar_handler
    async def get_test(self, test_id: str):
        return await self.db["tests"].find_one({"_id": ObjectId(test_id)})

    @rollbar_handler
    async def create_question(self, description: str):
        question_data = {"description": description}
        result = await self.db["questions"].insert_one(question_data)
        return str(result.inserted_id)

    @rollbar_handler
    async def get_question_by_id(self, question_id: str):
        question = await self.db["questions"].find_one({"_id": ObjectId(question_id)})
        return question

    # review
    @rollbar_handler
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

    @rollbar_handler
    async def update_result(self, result_id: str, question_index: int, answer: int):
        result = await self.db["results"].find_one({"_id": ObjectId(result_id)})

        if not result or result["completed"]:
            return None

        answers = result["answers"]
        if question_index < 0 or question_index >= len(answers):
            return None
        answers[question_index] = answer

        await self.db["results"].update_one({"_id": ObjectId(result_id)}, {"$set": {"answers": answers}})
        return answers

    @rollbar_handler
    async def get_answers(self, result_id: str):
        result = await self.db["results"].find_one({"_id": ObjectId(result_id)})
        if not result:
            return None
        return result["answers"]

    @rollbar_handler
    async def get_status(self, result_id: str):
        status = await self.db["results"].find_one({"_id": ObjectId(result_id)})
        if not status:
            return None
        return status["completed"]

    @rollbar_handler
    async def complete_test(self, result_id: str):
        result = await self.db["results"].find_one({"_id": ObjectId(result_id)})
        if not result:
            return None

        score = sum(result["answers"]) / (len(result["answers"]) * 6) * 100
        await self.db["results"].update_one({"_id": ObjectId(result_id)}, {"$set": {"score": score, "completed": True}})
        return score

    @rollbar_handler
    async def get_result(self, result_id: str):
        result = await self.db["results"].find_one({"_id": ObjectId(result_id)})
        return result

        return [str(tag_id) for tag_id in result.inserted_ids]

    @rollbar_handler
    async def create_chat(self, chat_id: str, isu_1: int, isu_2: int, status: Optional[str] = "active"):
        chat_data = {
            "chat_id": chat_id,
            "isu_1": isu_1,
            "isu_2": isu_2,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "status": status,
        }
        result = await self.db["chats"].insert_one(chat_data)
        return str(result)

    @rollbar_handler
    async def get_chats_by_user(self, isu: int):
        result = await self.db["chats"].find({"$or": [{"isu_1": isu}, {"isu_2": isu}]}).to_list(length=None)
        return [{"chat_id": chat["chat_id"]} for chat in result]

    @rollbar_handler
    async def create_message(self, chat_id: str, sender_id: int, receiver_id: int, text: str):
        message_data = {
            "chat_id": chat_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "text": text,
            "timestamp": datetime.datetime.now(datetime.timezone.utc),
        }

        result = await self.db["messages"].insert_one(message_data)
        return str(result.inserted_id)

    @rollbar_handler
    async def get_messages(self, chat_id: str, limit: int = 5, offset: int = 0):
        messages = (
            await self.db["messages"]
            .find({"chat_id": chat_id})
            .sort("sent_at", -1)
            .skip(offset)
            .limit(limit)
            .to_list(length=None)
        )
        return [
            {
                "message_id": str(message["_id"]),
                "sender_id": message["sender_id"],
                "receiver_id": message["receiver_id"],
                "text": message["text"],
                "timestamp": message["timestamp"],
            }
            for message in messages
        ]

    @rollbar_handler
    async def get_random_person(self, current_user_id: int) -> Optional[Dict[str, Any]]:
        disliked_users = await self.db["dislikes"].find({"user_id": current_user_id}).to_list(length=None)
        disliked_ids = [d["target_id"] for d in disliked_users]

        pipeline = [{"$match": {"isu": {"$ne": current_user_id, "$nin": disliked_ids}}}, {"$sample": {"size": 1}}]

        person = await self.db["users"].aggregate(pipeline).to_list(length=1)
        return person[0] if person else None

    @rollbar_handler
    async def like_user(self, user_id: int, target_id: int):
        await self.db["likes"].insert_one(
            {"user_id": user_id, "target_id": target_id, "created_at": datetime.datetime.now(datetime.timezone.utc)}
        )

        mutual_like = await self.db["likes"].find_one({"user_id": target_id, "target_id": user_id})

        if mutual_like:
            chat_id = str(ObjectId())
            await self.create_chat(chat_id=chat_id, isu_1=user_id, isu_2=target_id)
            return {"matched": True, "chat_id": chat_id}
        return {"matched": False, "chat_id": None}

    @rollbar_handler
    async def dislike_user(self, user_id: int, target_id: int):
        await self.db["dislikes"].insert_one(
            {"user_id": user_id, "target_id": target_id, "created_at": datetime.datetime.now(datetime.timezone.utc)}
        )


db_instance = Database()
