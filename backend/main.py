from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
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

app = FastAPI(
    title="D&D Character Manager API",
    description=(
        "Accounts, characters and the D&D reference data (races, classes, "
        "backgrounds, spells) behind the character manager."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
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


@app.get("/health", tags=["Meta"])
def health():
    """Liveness probe for deploys and for the frontend's dev-time API check."""
    return {"status": "ok", "version": app.version}
