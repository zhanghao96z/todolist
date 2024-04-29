from fastapi import APIRouter, Form, Depends, HTTPException, Request
from views.user import oauth2_scheme, decode_token
from models import Todolist, User
from peewee import IntegrityError, DoesNotExist
from pydantic import BaseModel, constr

router = APIRouter(prefix="/api/todo")

@router.post('/create')
def createTodo(title: str = Form(), description: str = Form(), due_date: str = Form(), token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(401, f"无效的token: {token}")
    try:
        user = User.get(username=username)
        todo = Todolist.get_or_none(title=title, user=user)
        if todo is None:
            Todolist.create(title=title, description=description, due_date=due_date, user=user)
            return {"code": 200, "msg": f"任务:{title}创建成功"}
        raise HTTPException(422, "任务已存在")
    except Exception as e:
        raise HTTPException(500, f"创建任务失败:{e}")

@router.get('/list')
def listTodo(token: str = Depends(oauth2_scheme)):
    data = []
    payload = decode_token(token)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(401, f"无效的token: {token}")
    user = User.get(username=username)
    todos = Todolist.select().where(Todolist.user == user)
    if todos is None:
        raise HTTPException(400, "还没有创建任务")
    for todo in todos:
        todo_data = {"id": todo.id, "title": todo.title, "description": todo.description, "due_date": todo.due_date, "status": todo.status}
        data.append(todo_data)
    return {"code": 200, "data": data}

@router.post('/delete/{pk}')
def deleteTodo(pk: int ,token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(401, f"无效的token: {token}")
    delete_row = Todolist.delete_by_id(pk)
    if delete_row == 0:
        raise IntegrityError("删除失败：未找到要删除的数据或违反了约束条件")
    return {"code": 200, "msg": "删除成功"}

class UpdateTodoRequest(BaseModel):
    pk: int
    title: str = None
    description: str = None
    due_date: str = None
    status: str = None

@router.post("/update")
def updateTodo(request_data: UpdateTodoRequest, token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(401, f"无效的token: {token}")
    try:
        todo = Todolist.get_by_id(request_data.pk)
    except DoesNotExist:
        raise HTTPException(404, f"未找到指定的 Todolist 数据")
    update_fields = {}
    if request_data.title is not None:
        update_fields["title"] = request_data.title
    if request_data.description is not None:
        update_fields["description"] = request_data.description
    if request_data.due_date is not None:
        update_fields["due_date"] = request_data.due_date
    if request_data.status is not None:
        update_fields["status"] = request_data.status

    try:
        todo.update(**update_fields).execute()
    except IntegrityError:
        raise HTTPException(500, "更新失败：违反了约束条件")

    return {"code": 200, "msg": "更新成功"}