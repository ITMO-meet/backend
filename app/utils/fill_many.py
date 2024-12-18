import datetime
import os

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def get_db():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI not found in env")
    client = MongoClient(mongo_uri)
    return client["meet-test"]


db = get_db()


def create_users(tags, special_tags):
    users = []
    for i in range(10):
        user_tags = tags[i % len(tags) : i % len(tags) + 2]  # Два обычных тега
        relationship_preference = [special_tags[i % len(special_tags)]]  # Один специальный тег
        users.append(
            {
                "_id": ObjectId(),
                "isu": 386871 + i,
                "username": f"user_{i}",
                "bio": f"Bio for user_{i}",
                "photos": {
                    "logo": f"meet/logos/{i}_logo.png",
                    "carousel": [f"meet/carousel/{i}_{j}.jpg" for j in range(5)],
                },
                "tags": user_tags,
                "person_params": {
                    "given_name": f"Name_{i}",
                    "family_name": f"Surname_{i}",
                    "gender": "male" if i % 2 == 0 else "female",
                    "birthdate": "2000-01-01",
                    "faculty": "Faculty of Something",
                    "hair_color": "brown",
                    "height": 170 + i,
                    "weight": 60 + i,
                    "zodiac_sign": "Aries",
                },
                "preferences": {"relationship_preference": relationship_preference, "gender_preference": "everyone"},
            }
        )
    user_ids = db.users.insert_many(users).inserted_ids
    print(f"Inserted users: {user_ids}")
    return user_ids


def create_tags():
    tags = [
        {"_id": ObjectId(), "name": "Communication", "is_special": 1, "description": "Общение"},
        {"_id": ObjectId(), "name": "Dates", "is_special": 1, "description": "Свидания"},
        {"_id": ObjectId(), "name": "Relationships", "is_special": 1, "description": "Отношения"},
        {"_id": ObjectId(), "name": "Friendship", "is_special": 1, "description": "Дружба"},
    ]
    for i in range(6):
        tags.append(
            {"_id": ObjectId(), "name": f"Tag {i + 1}", "is_special": 0, "description": f"Description for Tag {i + 1}"}
        )
    tag_ids = db.tags.insert_many(tags).inserted_ids
    print(f"Inserted tags: {tag_ids}")
    return tag_ids[:4], tag_ids[4:]  # Возвращаем специальные и обычные теги отдельно


def create_chats(user_ids):
    chats = []
    for i in range(5):
        chats.append(
            {
                "_id": ObjectId(),
                "chat_id": ObjectId(),  # ObjectId для chat_id
                "isu_1": 386871 + i,
                "isu_2": 386871 + (i + 1) % len(user_ids),
                "created_at": datetime.datetime.now(datetime.timezone.utc),
                "status": "active" if i % 2 == 0 else "inactive",
            }
        )
    chat_ids = db.chats.insert_many(chats).inserted_ids
    print(f"Inserted chats: {chat_ids}")
    return chat_ids


def create_messages(chat_ids):
    messages = []
    for i, chat_id in enumerate(chat_ids):
        messages.append(
            {
                "_id": ObjectId(),
                "chat_id": chat_id,  # Используем ObjectId чата
                "sender_id": 386871 + i,
                "receiver_id": 386871 + (i + 1) % 10,
                "text": f"test_message_{i}",
                "timestamp": datetime.datetime.now(datetime.timezone.utc),
            }
        )
    message_ids = db.messages.insert_many(messages).inserted_ids
    print(f"Inserted messages: {message_ids}")


def create_interactions(user_ids):
    interactions = []
    for i in range(10):
        interactions.append(
            {
                "_id": ObjectId(),
                "person_id": 386871 + (i + 1) % len(user_ids),
                "user_id": 386871 + i,
                "interaction": "superlike" if i % 2 == 0 else "like",
                "timestamp": datetime.datetime.now(datetime.timezone.utc),
            }
        )
    interaction_ids = db.interactions.insert_many(interactions).inserted_ids
    print(f"Inserted interactions: {interaction_ids}")


def create_questions():
    questions = []
    for i in range(10):
        questions.append({"_id": ObjectId(), "description": f"Question {i + 1}: Do you enjoy outdoor activities?"})
    question_ids = db.questions.insert_many(questions).inserted_ids
    print(f"Inserted questions: {question_ids}")
    return question_ids


def create_tests(question_ids):
    tests = []
    for i in range(5):
        tests.append(
            {
                "_id": ObjectId(),
                "name": f"Test {i + 1}",
                "description": "A sample test description.",
                "question_ids": question_ids[:4],
            }
        )
    test_ids = db.tests.insert_many(tests).inserted_ids
    print(f"Inserted tests: {test_ids}")
    return test_ids


def create_results(user_ids, test_ids):
    results = []
    for i in range(5):
        results.append(
            {
                "_id": ObjectId(),
                "user_id": 386871 + i,
                "test_id": test_ids[i % len(test_ids)],
                "answers": [5, 0, 5, 0],
                "score": 41.66666666666667,
                "completed": i % 2 == 0,
            }
        )
    result_ids = db.results.insert_many(results).inserted_ids
    print(f"Inserted results: {result_ids}")


def create_stories(user_ids):
    stories = []
    for i in range(10):
        stories.append(
            {
                "_id": ObjectId(),
                "isu": 386871 + i,
                "url": f"meet/stories/386871_story_{i}.jpg",
                "expiration_date": int(datetime.datetime.now().timestamp()) + 3600,
            }
        )
    story_ids = db.stories.insert_many(stories).inserted_ids
    print(f"Inserted stories: {story_ids}")


if __name__ == "__main__":
    # Удаляем старые данные
    db.users.delete_many({})
    db.chats.delete_many({})
    db.messages.delete_many({})
    db.tags.delete_many({})
    db.questions.delete_many({})
    db.tests.delete_many({})
    db.results.delete_many({})
    db.stories.delete_many({})
    db.interactions.delete_many({})

    print("Old data cleared.")

    # Заполнение новых данных
    special_tags, normal_tags = create_tags()
    user_ids = create_users(normal_tags, special_tags)
    chat_ids = create_chats(user_ids)
    create_messages(chat_ids)
    create_interactions(user_ids)
    question_ids = create_questions()
    test_ids = create_tests(question_ids)
    create_results(user_ids, test_ids)
    create_stories(user_ids)
