import datetime

from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()


async def create_users(db, tags, special_tags):
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
    user_ids = (await db["users"].insert_many(users)).inserted_ids
    print(f"Inserted users: {user_ids}")
    return user_ids


async def create_tags(db):
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
    tag_ids = (await db["tags"].insert_many(tags)).inserted_ids
    print(f"Inserted tags: {tag_ids}")
    return tag_ids[:4], tag_ids[4:]  # Возвращаем специальные и обычные теги отдельно


async def create_chats(db, user_ids):
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
    chat_ids = (await db["chats"].insert_many(chats)).inserted_ids
    print(f"Inserted chats: {chat_ids}")
    return chat_ids


async def create_messages(db, chat_ids):
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
    message_ids = (await db["messages"].insert_many(messages)).inserted_ids
    print(f"Inserted messages: {message_ids}")


async def create_interactions(db, user_ids):
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
    interaction_ids = (await db["interactions"].insert_many(interactions)).inserted_ids
    print(f"Inserted interactions: {interaction_ids}")


async def create_questions(db):
    questions = []
    for i in range(10):
        questions.append({"_id": ObjectId(), "description": f"Question {i + 1}: Do you enjoy outdoor activities?"})
    question_ids = (await db["questions"].insert_many(questions)).inserted_ids
    print(f"Inserted questions: {question_ids}")
    return question_ids


async def create_tests(db, question_ids):
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
    test_ids = (await db["tests"].insert_many(tests)).inserted_ids
    print(f"Inserted tests: {test_ids}")
    return test_ids


async def create_results(db, test_ids):
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
    result_ids = (await db["results"].insert_many(results)).inserted_ids
    print(f"Inserted results: {result_ids}")


async def create_stories(db):
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
    story_ids = (await db["stories"].insert_many(stories)).inserted_ids
    print(f"Inserted stories: {story_ids}")
