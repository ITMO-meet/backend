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
        {"name": "Шизофрения", "is_special": 1, "description": "Тут все понятно."},
        {"name": "Test Tag", "is_special": 0, "description": "Тест"},
    ]

    inserted_ids = await db_instance.add_test_tags(test_tags)
    print(f"Inserted test tags with IDs: {inserted_ids}")


if __name__ == "__main__":
    asyncio.run(populate_tags())
