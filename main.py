from fastapi import FastAPI
from app.infrastructure.database import engine, Base
from app.api import auth, unidades, produtos, estoque, pedidos, pagamentos, fidelidade

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Raízes do Nordeste API",
    description="API Back-end da rede de lanchonetes Raízes do Nordeste",
    version="1.0.0"
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