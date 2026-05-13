from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.infrastructure.database import get_db
from app.domain.models import Estoque, Produto, Unidade
from app.domain.enums import PerfilUsuario
from app.api.auth import get_usuario_atual

router = APIRouter(prefix="/estoque", tags=["Estoque"])

class EntradaEstoqueRequest(BaseModel):
    unidade_id: int
    produto_id: int
    quantidade: int

@router.get("")
def consultar_estoque(
    unidade_id: int,
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
                "path": "/estoque"
            }
        )
    unidade = db.query(Unidade).filter(Unidade.id == unidade_id).first()
    if not unidade:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "UNIDADE_NAO_ENCONTRADA",
                "message": "Unidade não encontrada.",
                "details": [{"field": "unidade_id", "issue": f"ID {unidade_id} não existe"}],
                "path": "/estoque"
            }
        )
    estoques = db.query(Estoque).filter(Estoque.unidade_id == unidade_id).all()
    return {
        "unidade_id": unidade_id,
        "unidade_nome": unidade.nome,
        "data": [
            {
                "produto_id": e.produto_id,
                "nome_produto": e.produto.nome,
                "quantidade": e.quantidade
            } for e in estoques
        ]
    }

@router.post("/entrada")
def registrar_entrada(
    request: EntradaEstoqueRequest,
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
                "path": "/estoque/entrada"
            }
        )
    if request.quantidade <= 0:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "QUANTIDADE_INVALIDA",
                "message": "A quantidade deve ser um número inteiro maior que zero.",
                "details": [{"field": "quantidade", "issue": f"Valor informado: {request.quantidade}"}],
                "path": "/estoque/entrada"
            }
        )
    produto = db.query(Produto).filter(Produto.id == request.produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "PRODUTO_NAO_ENCONTRADO",
                "message": "Produto não encontrado.",
                "details": [{"field": "produto_id", "issue": f"ID {request.produto_id} não existe"}],
                "path": "/estoque/entrada"
            }
        )
    unidade = db.query(Unidade).filter(Unidade.id == request.unidade_id).first()
    if not unidade:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "UNIDADE_NAO_ENCONTRADA",
                "message": "Unidade não encontrada.",
                "details": [{"field": "unidade_id", "issue": f"ID {request.unidade_id} não existe"}],
                "path": "/estoque/entrada"
            }
        )
    estoque = db.query(Estoque).filter(
        Estoque.unidade_id == request.unidade_id,
        Estoque.produto_id == request.produto_id
    ).first()
    if estoque:
        quantidade_anterior = estoque.quantidade
        estoque.quantidade += request.quantidade
    else:
        quantidade_anterior = 0
        estoque = Estoque(
            unidade_id=request.unidade_id,
            produto_id=request.produto_id,
            quantidade=request.quantidade
        )
        db.add(estoque)
    db.commit()
    db.refresh(estoque)
    return {
        "produto_id": request.produto_id,
        "nome_produto": produto.nome,
        "unidade_id": request.unidade_id,
        "quantidade_anterior": quantidade_anterior,
        "quantidade_atual": estoque.quantidade
    }