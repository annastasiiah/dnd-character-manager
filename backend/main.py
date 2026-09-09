from fastapi import FastAPI

from routers import admin, auth, characters, races, spells, user, classes, backgrounds

app = FastAPI()

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(characters.router)
app.include_router(races.router)
app.include_router(spells.router)
app.include_router(user.router)
app.include_router(classes.router)
app.include_router(backgrounds.router)