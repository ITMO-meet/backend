from fastapi import FastAPI
from app.api import tags
from app.api import quizes
from app.api import quizes_results
from app.api import auth
from app.api import register
from app.api import profile
from app.api import chats
from app import setup_rollbar

app = FastAPI()
setup_rollbar.init_rollbar()
app.include_router(tags.router)
app.include_router(quizes.router, prefix="/tests")
app.include_router(quizes_results.router, prefix="/results")
app.include_router(auth.router, prefix="/auth")
app.include_router(register.router, prefix="/auth")
app.include_router(profile.router, prefix="/profile")
app.include_router(chats.router, prefix="/chats")


def main():
    return "Hello, world!"


if __name__ == "__main__":
    main()
