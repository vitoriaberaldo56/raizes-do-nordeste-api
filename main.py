from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.infrastructure.database import engine, Base
from app.api import auth, unidades, produtos, estoque, pedidos, pagamentos, fidelidade
import traceback

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Raízes do Nordeste API",
    description="API Back-end da rede de lanchonetes Raízes do Nordeste",
    version="1.0.0"
)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    print("ERRO INTERNO:")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )

app.include_router(auth.router)
app.include_router(unidades.router)
app.include_router(produtos.router)
app.include_router(estoque.router)
app.include_router(pedidos.router)
app.include_router(pagamentos.router)
app.include_router(fidelidade.router)

@app.get("/")
def root():
    return {"message": "Raízes do Nordeste API está rodando!"}