from fastapi import FastAPI

from routers import admin, auth, characters, races

app = FastAPI()

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(characters.router)
app.include_router(races.router)
