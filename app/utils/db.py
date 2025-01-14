import datetime
import os
import io
import json
from typing import Any, Dict, List, Optional

from bson import ObjectId
from dotenv import load_dotenv
from minio import Minio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import timedelta

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
            self.minio_calendar_bucket_name = os.getenv("MINIO_CALENDAR_BUCKET_NAME") + "-test"
        else:
            self.db_name = "meet"
            self.db = self.client[self.db_name]
            self.minio_bucket_name = os.getenv("MINIO_BUCKET_NAME")
            self.minio_calendar_bucket_name = os.getenv("MINIO_CALENDAR_BUCKET_NAME")

        minio_endpoint = os.getenv("MINIO_ENDPOINT")
        minio_access_key = os.getenv("MINIO_ACCESS_KEY")
        minio_secret_key = os.getenv("MINIO_SECRET_KEY")
        minio_use_ssl = os.getenv("MINIO_USE_SSL", "False").lower() == "true"

        if not all([minio_endpoint, minio_access_key, minio_secret_key, self.minio_bucket_name]):
            raise ValueError("MINIO not found in env")

        self.minio_instance = Minio(minio_endpoint, minio_access_key, minio_secret_key, secure=minio_use_ssl)

        if not self.minio_instance.bucket_exists(self.minio_bucket_name):
            self.minio_instance.make_bucket(self.minio_bucket_name)

        minio_calendar_access_key = os.getenv("MINIO_CALENDAR_ACCESS_KEY")
        minio_calendar_secret_key = os.getenv("MINIO_CALENDAR_SECRET_KEY")

        if not all([minio_calendar_access_key, minio_calendar_secret_key, self.minio_calendar_bucket_name]):
            raise ValueError("MINIO calendar not found in env")

        self.minio_calendar_instance = Minio(minio_endpoint, minio_calendar_access_key, minio_calendar_secret_key, secure=minio_use_ssl)

        if not self.minio_calendar_instance.bucket_exists(self.minio_calendar_bucket_name):
            self.minio_calendar_instance.make_bucket(self.minio_calendar_bucket_name)

        if self.is_test_env:
            import asyncio
            asyncio.create_task(self.setup_test_db())

    @property
    def is_test_env(self) -> bool:
        return self.environment in self.test_env

    @rollbar_handler
    async def setup_test_db(self):
        if not self.is_test_env:
            return

        # Cleanup test database
        await self.db["users"].delete_many({})
        await self.db["chats"].delete_many({})
        await self.db["messages"].delete_many({})
        await self.db["tags"].delete_many({})
        await self.db["questions"].delete_many({})
        await self.db["tests"].delete_many({})
        await self.db["results"].delete_many({})
        await self.db["stories"].delete_many({})
        await self.db["interactions"].delete_many({})

        # Create sample data
        special_tags, normal_tags = await create_tags(self.db)
        user_ids = await create_users(self.db, normal_tags, special_tags)
        chat_ids = await create_chats(self.db, user_ids)
        await create_messages(self.db, chat_ids)
        await create_interactions(self.db, user_ids)
        question_ids = await create_questions(self.db)
        test_ids = await create_tests(self.db, question_ids)
        await create_results(self.db, test_ids)
        await create_stories(self.db)

    @rollbar_handler
    def generate_presigned_url(self, object_name: str, expiration: timedelta = timedelta(hours=1)) -> str:
        try:
            url = self.minio_instance.presigned_get_object(self.minio_bucket_name, object_name, expires=expiration)
            return url
        except Exception as e:
            raise ValueError(f"Failed to generate presigned URL for {object_name}: {e}")

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
    def uplod_json_to_minio(self, data: dict, filename):
        json_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        json_stream = io.BytesIO(json_data)

        self.minio_calendar_instance.put_object(
            self.minio_calendar_bucket_name,
            filename,
            json_stream,
            len(json_data),
            content_type="application/json",
        )

        return f"{self.minio_calendar_bucket_name}/{filename}"

    @rollbar_handler
    def get_json_from_minio(self, filename) -> dict:
        try:
            response = self.minio_calendar_instance.get_object(
                self.minio_calendar_bucket_name,
                filename,
            )
            json_data = json.load(response)

            response.close()
            response.release_conn()

            return json_data
        except Exception as e:
            raise ValueError(f"Failed to get json calendar from minio: {e}")

    @rollbar_handler
    def delete_json_from_minio(self, filename):
        try:
            self.minio_calendar_instance.remove_object(
                self.minio_calendar_bucket_name,
                filename,
            )
        except Exception as e:
            raise ValueError(f"Failed to remove calendar data from minio: {e}")

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

        pipeline = [
            {"$match": {"isu": {"$ne": current_user_id, "$nin": disliked_ids}}},
            {"$sample": {"size": 1}},
        ]

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
