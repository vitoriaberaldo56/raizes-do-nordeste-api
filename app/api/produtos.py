from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.infrastructure.database import get_db
from app.domain.models import Produto
from app.domain.enums import PerfilUsuario
from app.api.auth import get_usuario_atual

router = APIRouter(prefix="/produtos", tags=["Produtos"])

class ProdutoRequest(BaseModel):
    nome: str
    descricao: str = None
    preco: float
    categoria: str

@router.get("")
def listar_produtos(
    page: int = 1,
    limit: int = 10,
    unidade_id: int = None,
    db: Session = Depends(get_db),
    usuario_atual=Depends(get_usuario_atual)
):
    offset = (page - 1) * limit
    query = db.query(Produto).filter(Produto.disponivel_globalmente == True)
    total = query.count()
    produtos = query.offset(offset).limit(limit).all()
    return {
        "data": [
            {
                "id": p.id,
                "nome": p.nome,
                "descricao": p.descricao,
                "preco": p.preco,
                "categoria": p.categoria,
                "disponivel": p.disponivel_globalmente
            } for p in produtos
        ],
        "page": page,
        "limit": limit,
        "total": total
    }

@router.get("/{id}")
def buscar_produto(
    id: int,
    db: Session = Depends(get_db),
    usuario_atual=Depends(get_usuario_atual)
):
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "PRODUTO_NAO_ENCONTRADO",
                "message": "Nenhum produto encontrado com o ID informado.",
                "details": [{"field": "id", "issue": f"ID {id} não existe"}],
                "path": f"/produtos/{id}"
            }
        )
    return {
        "id": produto.id,
        "nome": produto.nome,
        "descricao": produto.descricao,
        "preco": produto.preco,
        "categoria": produto.categoria,
        "disponivel": produto.disponivel_globalmente
    }

@router.post("", status_code=201)
def criar_produto(
    request: ProdutoRequest,
    db: Session = Depends(get_db),
    usuario_atual=Depends(get_usuario_atual)
):
    if usuario_atual.perfil not in [PerfilUsuario.GERENTE, PerfilUsuario.ADMIN]:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "SEM_PERMISSAO",
                "message": "Seu perfil não tem permissão para realizar esta ação.",
                "details": [],
                "path": "/produtos"
            }
        )
    if request.preco <= 0:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "PRECO_INVALIDO",
                "message": "O preço deve ser maior que zero.",
                "details": [{"field": "preco", "issue": f"Valor informado: {request.preco}"}],
                "path": "/produtos"
            }
        )
    novo = Produto(
        nome=request.nome,
        descricao=request.descricao,
        preco=request.preco,
        categoria=request.categoria
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return {
        "id": novo.id,
        "nome": novo.nome,
        "descricao": novo.descricao,
        "preco": novo.preco,
        "categoria": novo.categoria,
        "disponivel": novo.disponivel_globalmente
    }