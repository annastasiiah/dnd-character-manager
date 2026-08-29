from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import text


from database import get_db

app = FastAPI()

@app.get("/db")
def test_db(db: Session = Depends(get_db)):
    row = db.execute(text(('SELECT 1')))
    return {'result': row.scalar()}

