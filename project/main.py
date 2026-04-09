# Imports
from fastapi import FastAPI, Request, Form, HTTPException, Depends, status, Cookie, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import User, Task
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, create_engine, Session, select, col, func
from typing import Annotated
from datetime import date
from datetime import datetime
import calendar

# Init FastAPI
@asynccontextmanager
async def initFunction(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=initFunction)

arquivo_sqlite = "HTMX2.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

# Static and Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory=["templates", "templates/partials"])

# Create DB
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

########
# ROOT #
########

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="signup.html")

########
# USER #
########

@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

# Log In
@app.post("/login")
async def send_login(user: User, response: Response):
    with Session(engine) as session:
        query = select(User).where(User.name == user.name).where(User.password == user.password)
        found_user = session.exec(query).first()
    
    if not found_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    response.set_cookie(key="session_user", value=found_user.name)
    return {"message": "Logado com sucesso"}

# Create New User
@app.post("/newuser")
async def create_user(user: User):
    with Session(engine) as session:
        query = select(User).where(User.name == user.name)
        if session.exec(query).first():
            return {"message": "Nome de usuário não disponível"}
        
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"message": "Usuário criado!"}

# Get Current Active User
def get_active_user(session_user: Annotated[str | None, Cookie()] = None):
    if not session_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Acesso negado: você não está logado.")
    
    with Session(engine) as session:
        query = select(User).where(User.name == session_user)
        user = session.exec(query).first()

    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    
    return user

########
# TASK #
########

# Search for Tasks
def search_tasks(id: int | None = None,
                 name = '',
                 date = None,
                 user: User | None = None):
    with Session(engine) as session:
        query = select(Task).where(col(Task.name).contains(name))
        if date: query = query.where(Task.date == date)
        if user: query = query.where(Task.user_id == user.id)
        if id: query = query.where(Task.id == id)

        return session.exec(query).all()

# Return tasks
@app.get("/tasklist", response_class=HTMLResponse)
async def get_user_tasks(request: Request,
                   name: str | None='',
                   date: date | None=None,
                   user: User = Depends(get_active_user),
                   page: int = 1,
                   tasks_per_page: int = 5):
    tasks = search_tasks(name=name, date=date, user=user)
    first = (page-1)*tasks_per_page
    last = first + tasks_per_page
    return templates.TemplateResponse(request=request,
                                      name="list.html",
                                      context={"tasklist": tasks[first:last],
                                               "page": page,
                                               "last_page": (len(tasks)-1)//tasks_per_page+1})

# Create New Task
@app.get("/newtask")
async def new(request: Request):
    return templates.TemplateResponse(request, "new-task.html")

@app.post("/newtask", response_class=HTMLResponse)
async def new_tasks(name: str = Form(...),
                description: str = Form(...),
                date: date = Form(...),
                user: User = Depends(get_active_user)):
    print(user)
    with Session(engine) as session:
        task = Task(name=name, description=description, date=date, user_id=user.id)

        session.add(task)
        session.commit()
        session.refresh(task)
        return HTMLResponse(content=f"<p>Tarefa registrada!</p>")

# Update task
@app.get("/updatetask")
async def update(request: Request):
    return templates.TemplateResponse(request, "update-task.html")

@app.put("/updatetask", response_class=HTMLResponse)
async def update_task(id: int = Form(...),
                newName: Annotated[str | None, Form(...)] = None,
                newDescription: Annotated[str | None, Form(...)] = None,
                newDate: Annotated[date | None, Form(...)] = None,
                user: User = Depends(get_active_user)):
    with Session(engine) as session:
        query = select(Task).where(Task.id == id).where(Task.user_id == user.id)
        task = session.exec(query).first()

        if not task:
            raise HTTPException(404, "Tarefa não encontrada")

        if newName: task.name = newName
        if newDescription: task.description = newDescription
        if newDate: task.date = newDate

        session.commit()
        session.refresh(task)
        return HTMLResponse(content="Tarefa Atualizada!</p>")

# Delete task
@app.get("/deletetask")
async def delete(request: Request):
    return templates.TemplateResponse(request, "delete-task.html")

@app.delete("/deletetask", response_class=HTMLResponse)
async def delete_tasks(id: int, user: User = Depends(get_active_user)):
    with Session(engine) as session:
        query = select(Task).where(Task.id == id).where(Task.user_id == user.id)
        task = session.exec(query).first()
        
        if not task:
            raise HTTPException(404, "Tarefa não encontrada")
        
        session.delete(task)
        session.commit()
        return HTMLResponse(content="Tarefa Apagada!")


############
# CALENDAR #
############

# Display the calendar
@app.get("/calendar")
async def show_calendar(request: Request,
                  month: int | None = None,
                  year: int | None = None,
                  user: User = Depends(get_active_user)):

    days =  ["D", "S", "T", "Q", "Q", "S", "S"]
    months = ["Janeiro", "F"]

    current_day = datetime.now().day
    current_month = datetime.now().month
    current_year = datetime.now().year

    if not month: month = current_month
    if not year: year = current_year
    
    first_weekday, days_in_month = calendar.monthrange(year, month)

    tasks = search_tasks(user=user)

    return templates.TemplateResponse(
        request=request,
        name="calendar.html", 
        context={"username": user.name,
                 "current_day": current_day,
                 "current_month": current_month,
                 "current_year": current_year,
                 "days": days,
                 "months": months,
                 "month": month,
                 "year": year,
                 "first_weekday": (first_weekday+1)%7,
                 "days_in_month": days_in_month,
                 "tasks": tasks}
    )
