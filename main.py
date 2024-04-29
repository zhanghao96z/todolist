from fastapi import FastAPI
from views.user import router as user_router
from views.todolist import router as todo_router

app = FastAPI()

app.include_router(user_router)
app.include_router(todo_router)

@app.get("/")
def index():
    return "hello world"
