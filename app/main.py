from fastapi import FastAPI

from app import setup_rollbar
from app.api import auth, chats, db, matches, profile, quizes, quizes_results, register, stories, tags

app = FastAPI()
setup_rollbar.init_rollbar()
app.include_router(tags.router)
app.include_router(quizes.router, prefix="/tests")
app.include_router(quizes_results.router, prefix="/results")
app.include_router(auth.router, prefix="/auth")
app.include_router(register.router, prefix="/auth")
app.include_router(profile.router, prefix="/profile")
app.include_router(chats.router, prefix="/chats")
app.include_router(stories.router, prefix="/stories")
app.include_router(matches.router, prefix="/matches")
app.include_router(db.router, prefix="/db")


def main():
    return "Hello, world!"


if __name__ == "__main__":
    main()
