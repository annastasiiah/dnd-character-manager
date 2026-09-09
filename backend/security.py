from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY

ALGORITHM = "HS256"


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


password_hash = PasswordHash.recommended()


def hash_password(password):
    hashed_password = password_hash.hash(password)
    return hashed_password


def verify_password(password, hashed_password):
    return password_hash.verify(password, hashed_password)
