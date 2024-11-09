from fastapi import FastAPI
from app.api import tags
from app.api import quizes
from app.api import quizes_results
from app.api import auth
from app.api import register
from app.api import profile


app = FastAPI()
app.include_router(tags.router)
app.include_router(quizes.router, prefix="/tests")
app.include_router(quizes_results.router, prefix="/results")
app.include_router(auth.router, prefix="/auth")
app.include_router(register.router, prefix="/auth")
app.include_router(profile.router, prefix="/profile")


def main():
    return "Hello, world!"


if __name__ == "__main__":
    main()
