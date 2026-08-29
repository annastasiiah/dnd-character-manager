import os
import jwt

from pwdlib import PasswordHash
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")

ALGORITHM = "HS256"

def create_access_token(data: dict):    
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt

password_hash = PasswordHash.recommended()

def hash_password(password):
    hashed_password = password_hash.hash(password)
    return hashed_password

def verify_password(password, hashed_password):
    return password_hash.verify(password, hashed_password)


