import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch
from app.api.chats import (
    create_chat,
    get_chats_for_user,
    send_message,
    get_messages,
)
from app.models.chat import CreateChat, SendMessage


@pytest.mark.asyncio
async def test_create_chat_same_user():
    payload = CreateChat(isu_1=123456, isu_2=123456)

    with pytest.raises(HTTPException) as exc_info:
        await create_chat(payload)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "chat cannot be created for the same user"


@pytest.mark.asyncio
async def test_create_chat_success():
    payload = CreateChat(isu_1=123456, isu_2=789012)

    with patch("app.api.chats.db_instance.create_chat", new_callable=AsyncMock) as mock_create_chat:
        result = await create_chat(payload)
        assert "chat_id" in result
        assert isinstance(result["chat_id"], str)

        mock_create_chat.assert_awaited_once_with(chat_id=result["chat_id"], isu_1=payload.isu_1, isu_2=payload.isu_2)


@pytest.mark.asyncio
async def test_get_chats_for_user_not_found():
    isu = 123456

    with patch("app.api.chats.db_instance.get_chats_by_user", new_callable=AsyncMock) as mock_get_chats_by_user:
        mock_get_chats_by_user.return_value = []

        with pytest.raises(HTTPException) as exc_info:
            await get_chats_for_user(isu)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "chats not found for this user"

        mock_get_chats_by_user.assert_awaited_once_with(isu)


@pytest.mark.asyncio
async def test_get_chats_for_user_success():
    isu = 123456
    chats = [{"chat_id": "meowmeowkillmenow1111"}, {"chat_id": "r4nd0m"}]

    with patch("app.api.chats.db_instance.get_chats_by_user", new_callable=AsyncMock) as mock_get_chats_by_user:
        mock_get_chats_by_user.return_value = chats

        result = await get_chats_for_user(isu)
        assert result == {"chats": chats}

        mock_get_chats_by_user.assert_awaited_once_with(isu)


@pytest.mark.asyncio
async def test_send_message_success():
    payload = SendMessage(chat_id="aboba123", sender_id=123456, receiver_id=789012, text="meow")

    with patch("app.api.chats.db_instance.create_message", new_callable=AsyncMock) as mock_create_message:
        mock_create_message.return_value = "message_id_123"

        result = await send_message(payload)
        assert result == {"message_id": "message_id_123"}

        mock_create_message.assert_awaited_once_with(
            chat_id=payload.chat_id, sender_id=payload.sender_id, receiver_id=payload.receiver_id, text=payload.text
        )


@pytest.mark.asyncio
async def test_get_messages_not_found():
    chat_id = "abobus123"
    limit = 5
    offset = 0

    with patch("app.api.chats.db_instance.get_messages", new_callable=AsyncMock) as mock_get_messages:
        mock_get_messages.return_value = []

        with pytest.raises(HTTPException) as exc_info:
            await get_messages(chat_id, limit, offset)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "messages not found"

        mock_get_messages.assert_awaited_once_with(chat_id=chat_id, limit=limit, offset=offset)


@pytest.mark.asyncio
async def test_get_messages_success():
    chat_id = "abobus131"
    limit = 5
    offset = 0
    messages = [
        {
            "chat_id": "abobus131",
            "message_id": "msg1",
            "sender_id": 123456,
            "receiver_id": 789012,
            "text": "meow",
            "timestamp": "2023-01-01T00:00:00Z",
        }
    ]

    with patch("app.api.chats.db_instance.get_messages", new_callable=AsyncMock) as mock_get_messages:
        mock_get_messages.return_value = messages

        result = await get_messages(chat_id, limit, offset)
        assert result == {"messages": messages}

        mock_get_messages.assert_awaited_once_with(chat_id=chat_id, limit=limit, offset=offset)
