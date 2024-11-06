import asyncio
from db import db_instance
from bson import ObjectId


async def create_test_with_questions():
    test_name = "Пример теста"
    test_description = "Это тест для проверки вашего отношения к разным темам."
    question_descriptions = [
        "Вам нравится гулять на свежем воздухе?",
        "Часто ли вы посещаете культурные мероприятия?",
        "Любите ли вы проводить время в компании друзей?",
        "Вы предпочитаете спокойный отдых?",
    ]

    question_ids = []
    for question_text in question_descriptions:
        question_id = await db_instance.create_question(question_text)
        question_ids.append(ObjectId(question_id))
        print(f"Создан вопрос с ID: {question_id}")

    test_id = await db_instance.create_test(
        name=test_name, description=test_description, question_ids=question_ids
    )
    print(f"Создан тест с ID: {test_id}")


if __name__ == "__main__":
    asyncio.run(create_test_with_questions())
