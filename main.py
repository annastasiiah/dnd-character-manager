from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "D&D Character Manager API"}

