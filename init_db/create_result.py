import asyncio
from db import db_instance


async def create_and_complete_test_result():
    user_id = 386871
    test_id = "672b5303309b6efb86698881"

    result_id = await db_instance.create_result(user_id=user_id, test_id=test_id)
    print(f"Создан результат теста с ID: {result_id}")

    answers = [1, 3, 5, 6]
    for answer in answers:
        updated_answers = await db_instance.update_result(result_id, answer)
        print(f"Ответы обновлены: {updated_answers}")

    score = await db_instance.complete_test(result_id)
    print(f"Тест завершен. Итоговый балл: {score}")

    result = await db_instance.get_result(result_id)
    print("Итоговый результат теста:", result)


if __name__ == "__main__":
    asyncio.run(create_and_complete_test_result())
