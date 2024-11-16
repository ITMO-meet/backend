from fastapi import FastAPI
from app.api import tags, contacts, stories, people
from app.api import quizes
from app.api import quizes_results
from app.api import auth
from app.api import register
from app.api import profile
from app.api import chats
from app import setup_rollbar
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
setup_rollbar.init_rollbar()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3070", "http://127.0.0.1:3070", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tags.router)
app.include_router(quizes.router, prefix="/tests")
app.include_router(quizes_results.router, prefix="/results")
app.include_router(auth.router, prefix="/auth")
app.include_router(register.router, prefix="/auth")
app.include_router(profile.router, prefix="/profile")
app.include_router(chats.router, prefix="/chats")
app.include_router(contacts.router)
app.include_router(stories.router)
app.include_router(people.router)


# Логирование каждого запроса, нужно только для отладки
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response
