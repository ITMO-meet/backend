from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app import setup_rollbar
from app.api import (
    auth,
    calendar,
    chats,
    db,
    matches,
    profile,
    quizes,
    quizes_results,
    register,
    stories,
    tags,
    premium,
)
from app.utils import scheduler

app = FastAPI()
setup_rollbar.init_rollbar()
app.include_router(tags.router)

#app.add_middleware(TrustedHostMiddleware, allowed_hosts=["itmomeet.ru", "www.itmomeet.ru"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(quizes.router, prefix="/tests")
app.include_router(quizes_results.router, prefix="/results")
app.include_router(auth.router, prefix="/auth")
app.include_router(register.router, prefix="/auth")
app.include_router(profile.router, prefix="/profile")
app.include_router(chats.router, prefix="/chats")
app.include_router(stories.router, prefix="/stories")
app.include_router(matches.router, prefix="/matches")
app.include_router(calendar.router, prefix="/calendar")
app.include_router(premium.router, prefix="/premium")
app.include_router(db.router, prefix="/db")

@app.on_event("startup")
async def startup_event():
    print("Scheduler started")
    scheduler.start_scheduler()

def main():
    return "Hello, world!"


if __name__ == "__main__":
    main()
