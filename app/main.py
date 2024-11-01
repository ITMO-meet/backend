from fastapi import FastAPI
from app.api import auth

app = FastAPI()
app.include_router(auth.router, prefix="/auth")


def main():
    return "Hello, world!"


if __name__ == "__main__":
    main()
