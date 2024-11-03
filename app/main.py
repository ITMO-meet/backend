from fastapi import FastAPI
from app.api import auth
from app.api import register
from app.api import tags

app = FastAPI()
app.include_router(tags.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(register.router, prefix="/auth")




def main():
    return "Hello, world!"


if __name__ == "__main__":
    main()
