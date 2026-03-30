from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

curtidas = 0

@app.get("/home",response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"pagina": "/home/pagina_curtidas", "curtidas": curtidas, "patual": "curtidas"})

@app.get("/home/pagina_curtidas",response_class=HTMLResponse)
async def pagc(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request=request, name="index.html", context={"pagina": "/home/pagina_curtidas", "curtidas": curtidas, "patual": "curtidas"})
    return templates.TemplateResponse(request=request, name="curtidas.html", context={"curtidas": curtidas, "patual": "curtidas"})

@app.get("/home/pagina_jupiter", response_class=HTMLResponse)
async def pagj(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request=request, name="index.html", context={"pagina": "/home/pagina_jupiter", "patual": "jupiter"})
    return templates.TemplateResponse(request=request, name="pagina_jupiter/index.html", context={"patual": "jupiter"})

@app.get("/home/pagina_professor", response_class=HTMLResponse)
async def pagp(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request=request, name="index.html", context={"pagina": "/home/pagina_professor", "patual": "professor"})
    return templates.TemplateResponse(request=request, name="pagina_professor/index.html", context={"patual": "professor"})

@app.post("/curtir")
async def curtir():
    global curtidas
    curtidas += 1
    return curtidas

@app.delete("/remover_curtidas")
async def remover_curtidas():
    global curtidas
    curtidas = 0
    return curtidas