from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import Aluno
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, create_engine, Session, select, col, func

@asynccontextmanager
async def initFunction(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=initFunction)

arquivo_sqlite = "HTMX2.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

templates = Jinja2Templates(directory=["templates", "templates/partials"])

ultima_pagina = 0

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
 
def buscar_alunos(busca, pagina: int = 0, alunos_por_pagina:int = 10):
    with Session(engine) as session:
        query = select(Aluno).where(col(Aluno.nome).contains(busca)).offset(pagina*alunos_por_pagina).limit(alunos_por_pagina)#x.order_by(Aluno.nome)
        
        total_alunos = session.exec(select(func.count(Aluno.id)).where(col(Aluno.nome).contains(busca))).one()
        global ultima_pagina
        ultima_pagina = total_alunos // alunos_por_pagina
        
        return session.exec(query).all()


@app.get("/busca", response_class=HTMLResponse)
def busca(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/lista", response_class=HTMLResponse)
def lista(request: Request, busca: str | None='', pagina: int = 0, alunos_por_pagina:int = 10):
    alunos = buscar_alunos(busca, pagina, alunos_por_pagina)
    global ultima_pagina
    return templates.TemplateResponse(request, "lista.html", {"alunos": alunos, "pagina":pagina, "ultima_pagina":ultima_pagina})

@app.get("/editarAlunos")
def novoAluno(request: Request):
    return templates.TemplateResponse(request, "options.html")

@app.post("/novoAluno", response_class=HTMLResponse)
def criar_aluno(nome: str = Form(...)):
    with Session(engine) as session:
        novo_aluno = Aluno(nome=nome)
        session.add(novo_aluno)
        session.commit()
        session.refresh(novo_aluno)
        return HTMLResponse(content=f"<p>O(a) aluno(a) {novo_aluno.nome} foi registrado(a)!</p>")
    
@app.delete("/deletaAluno", response_class=HTMLResponse)
def deletar_aluno(id: int):
    with Session(engine) as session:
        query = select(Aluno).where(Aluno.id == id)
        aluno = session.exec(query).first()
        if (not aluno):
            raise HTTPException(404, "Aluno não encontrado")
        session.delete(aluno)
        session.commit()
        return HTMLResponse(content=f"<p>O(a) aluno(a) {aluno.nome} foi deletado(a)!</p>")

@app.put("/atualizaAluno", response_class=HTMLResponse)
def atualizar_aluno(id: int = Form(...), novoNome: str = Form(...)):
    with Session(engine) as session:
        query = select(Aluno).where(Aluno.id == id)
        aluno = session.exec(query).first()
        if (not aluno):
            raise HTTPException(404, "Aluno não encontrado")
        nomeAntigo = aluno.nome
        aluno.nome = novoNome
        session.commit()
        session.refresh(aluno)
        return HTMLResponse(content=f"<p>O(a) aluno(a) {nomeAntigo} foi atualizado(a) para {aluno.nome}!</p>")

@app.delete("/apagar", response_class=HTMLResponse)
def apagar():
    return ""