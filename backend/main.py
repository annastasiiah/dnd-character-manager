from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import (
    admin,
    auth,
    backgrounds,
    characters,
    classes,
    races,
    spells,
    user,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(characters.router)
app.include_router(races.router)
app.include_router(spells.router)
app.include_router(user.router)
app.include_router(classes.router)
app.include_router(backgrounds.router)