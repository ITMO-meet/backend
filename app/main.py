from fastapi import FastAPI
from app.api import tags
from app.api import quizes
from app.api import quizes_results
from app.api import auth
from app.api import register
from app.api import profile
from app.api import chats
from app.api import stories
from app.api import matches
from app.api import db
from app import setup_rollbar
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
setup_rollbar.init_rollbar()
app.include_router(tags.router)

app.add_middleware(

    CORSMiddleware,
    allow_origins=["http://localhost:3070"],
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
app.include_router(db.router, prefix="/db")