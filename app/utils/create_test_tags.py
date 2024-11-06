import asyncio
from db import db_instance


async def populate_tags():
    test_tags = [
        {"name": "Музыка", "is_special": 0, "description": "Человек любит музыку."},
        {
            "name": "Анекдоты",
            "is_special": 0,
            "description": "Человек фанат анекдотов.",
        },
        {"name": "Шизофрения", "is_special": 0, "description": "Тут все понятно."},
        {"name": "Test Tag", "is_special": 0, "description": "Тест"},
        {"name": "Dates", "is_special": 1, "description": "Свидания"},
        {"name": "Relationships", "is_special": 1, "description": "Отношения"},
        {"name": "Friendship", "is_special": 1, "description": "Дружба"},
        {"name": "Communication", "is_special": 1, "description": "Общение"},

        
    ]

    inserted_ids = await db_instance.add_test_tags(test_tags)
    print(f"Inserted test tags with IDs: {inserted_ids}")


if __name__ == "__main__":
    asyncio.run(populate_tags())
