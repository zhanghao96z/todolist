from fastapi import APIRouter, HTTPException, Form, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Union
from models import User
from jwt import PyJWTError
from peewee import IntegrityError
import jwt
import time

router = APIRouter(prefix="/api/user")

SECRET_KEY = "centos"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_token(payload: dict) -> str:
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)

def decode_token(token: str) -> Union[dict, HTTPException]:
    try: 
        return jwt.decode(token, SECRET_KEY, ALGORITHM)
    except PyJWTError as e:
        raise HTTPException(401, f"无效的token,详细: {e}")

@router.post("/register")
def register(username: str = Form(), passwd: str = Form()):
    try:
        User.create(username=username, passwd=passwd)
        return {"code": 200, "msg": f"{username}注册成功"}
    except IntegrityError:
        raise HTTPException(422, "用户已存在")
    except Exception:
        raise HTTPException(500, f"{username}注册失败")

@router.post("/login")
def login(username: str = Form(), passwd: str = Form()):
    user = User.get_or_none(username=username, passwd=passwd)
    if user:
        exp_time = int(time.time()) + 60 * 5
        payload = {"sub": username, "exp": exp_time}
        token = create_token(payload)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(401, f"{username}登录失败")

@router.get('/hhh')
def hello(token: str = Depends(oauth2_scheme)):
    print(token)
    payload = decode_token(token)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(401, f"无效的token:{token}")
    return f"{username} say hello world"


    
