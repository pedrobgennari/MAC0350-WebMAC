from fastapi import FastAPI, Request, Depends, HTTPException, status, Cookie, Response
from fastapi.templating import Jinja2Templates
from typing import Annotated
from pydantic import BaseModel

app = FastAPI()

# Sintaxe recomendada: diretório como primeiro argumento posicional
templates = Jinja2Templates(directory="templates")

class User(BaseModel):
    nome: str
    senha: str
    bio: str

class LoginRequest(BaseModel):
    nome: str
    senha: str

# Nossa base de dados em memória
users_db = [
    #{"username": "joão", "bio": "Professor de Python"},
    #{"username": "maria", "bio": "Desenvolvedora Web"},
]

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="signup.html")
    
@app.post("/users")
async def users(user: User):
    users_db.append(user)
    return user

@app.get("/login")
async def send_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

# 1. Rota para "Logar" (Define o Cookie)
@app.post("/login")
def login(loginRequest: LoginRequest, response: Response):
    # Buscamos o usuário usando um laço simples
    usuario_encontrado = None
    for u in users_db:
        if u.nome == loginRequest.nome and u.senha == loginRequest.senha:
            usuario_encontrado = u
            break
    
    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # O servidor diz ao navegador: "Guarde esse nome no cookie 'session_user'"
    response.set_cookie(key="session_nome", value=usuario_encontrado.nome)
    response.set_cookie(key="session_senha", value=usuario_encontrado.senha)
    return {"message": "Logado com sucesso"}


# 2. A Dependência: Lendo o Cookie
def get_active_user(session_nome: Annotated[str | None, Cookie()] = None,
                    session_senha: Annotated[str | None, Cookie()] = None):

    # O FastAPI busca automaticamente um cookie chamado 'session_user'
    if not session_nome or not session_senha:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso negado: você não está logado."
        )
    
    user = next((u for u in users_db if u.nome == session_nome and u.senha == session_senha), None)
    
    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    
    return user

# 3. Rota Protegida
@app.get("/profile")
def show_profile(request: Request, user: User = Depends(get_active_user)):    
    return templates.TemplateResponse(
        request=request, 
        name="profile.html", 
        context={"username": user.nome, "bio": user.bio}
    )

@app.get("/getusers")
async def func():
    return users_db
