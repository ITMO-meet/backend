# app/api/push.py
from fastapi import APIRouter, HTTPException, Body
from pywebpush import webpush, WebPushException
import os
import json

router = APIRouter()

# Храним подписки по пользователям: { user_id: [subscription, ...] }
subscriptions = {}  # dict: int -> list of dict

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_CLAIMS = {
    "sub": "mailto:arrtemij96@gmail.com"
}

@router.post("/subscribe")
async def subscribe(data: dict = Body(...)):
    """
    Ожидается, что на клиенте будут отправлены данные вида:
    {
        "subscription": { ... },  # объект подписки
        "user_id": <идентификатор пользователя>
    }
    """
    subscription = data.get('subscription')
    user_id = data.get('user_id')
    if not subscription or user_id is None:
        raise HTTPException(status_code=400, detail="Необходимо передать subscription и user_id")
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="user_id должен быть числом")

    if user_id not in subscriptions:
        subscriptions[user_id] = []
    # Проверка на дублирование подписки
    if subscription not in subscriptions[user_id]:
        subscriptions[user_id].append(subscription)
    return {"status": "ok"}

@router.post("/send")
async def send_push(message: dict = Body(...)):
    if not subscriptions:
        raise HTTPException(status_code=400, detail="Нет подписок")
    data = message.get("data", {})
    results = []
    for user_subs in subscriptions.values():
        for sub in user_subs:
            try:
                webpush(
                    subscription_info=sub,
                    data=json.dumps(data),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims=VAPID_CLAIMS
                )
                results.append({"subscription": sub, "status": "sent"})
            except WebPushException as ex:
                results.append({"subscription": sub, "status": "error", "detail": str(ex)})
    return results

def send_push_internally(data: dict, target_user_id: int):
    """
    Отправляет push-уведомление только на устройства пользователя с идентификатором target_user_id.
    """
    if target_user_id not in subscriptions:
        return
    for sub in subscriptions[target_user_id]:
        try:
            webpush(
                subscription_info=sub,
                data=json.dumps(data),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS
            )
        except WebPushException as ex:
            print("Push error:", ex)
