from fastapi import FastAPI, Form, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Union
import jwt
import time

app = FastAPI(title="test")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

user = {"username": "cxk", "password": "centos"}

books = [
    {
        "title": "Python Crash Course",
        "author": "Eric Matthes",
        "year": 2015,
        "genre": "Programming"
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "year": 1949,
        "genre": "Dystopian Fiction"
    },
    {
        "title": "The Hitchhiker's Guide to the Galaxy",
        "author": "Douglas Adams",
        "year": 1979,
        "genre": "Science Fiction"
    }
]

SECRET_KEY = "qazwsx"
ALGORITHM = "HS256"

def create_token(payload: dict) -> str:
    access_token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return access_token

def decode_token(token: str) -> Union[dict, HTTPException]:
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(401, f"无效的token{e}")


@app.post('/login')
def login(username: str = Form(), password: str = Form()):
    if username == user["username"] and password == user["password"]:
        user_data = {"sub": username, "exp": int(time.time()) + 60 * 5}
        access_token = create_token(user_data)
        return {"access_token": access_token, "token_type": "bearer"}
    return "no"

@app.get('/books')
def getBooks(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    username = payload.get("sub")
    current_timestamp = int(time.time())  # 获取当前时间戳
    remaining_time = payload.get("exp") - current_timestamp  # 计算剩余时间
    print(f"Token 还有 {remaining_time} 秒过期。")
    if username is None:
        raise HTTPException(401, "无效的token")
    return books    