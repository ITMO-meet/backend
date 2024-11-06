from fastapi import FastAPI
from app.api import tags
from app.api import tests
from app.api import test_results

app = FastAPI()
app.include_router(tags.router)
app.include_router(tests.router, prefix="/tests")
app.include_router(test_results.router, prefix="/results")


def main():
    return "Hello, world!"


if __name__ == "__main__":
    main()
