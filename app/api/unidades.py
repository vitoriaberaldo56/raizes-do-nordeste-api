from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.domain.models import Unidade
from app.api.auth import get_usuario_atual

router = APIRouter(prefix="/unidades", tags=["Unidades"])

@router.get("")
def listar_unidades(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    usuario_atual=Depends(get_usuario_atual)
):
    offset = (page - 1) * limit
    unidades = db.query(Unidade).filter(Unidade.ativa == True).offset(offset).limit(limit).all()
    total = db.query(Unidade).filter(Unidade.ativa == True).count()
    return {
        "data": [
            {
                "id": u.id,
                "nome": u.nome,
                "cidade": u.cidade,
                "estado": u.estado,
                "ativa": u.ativa
            } for u in unidades
        ],
        "page": page,
        "limit": limit,
        "total": total
    }

@router.get("/{id}")
def buscar_unidade(
    id: int,
    db: Session = Depends(get_db),
    usuario_atual=Depends(get_usuario_atual)
):
    unidade = db.query(Unidade).filter(Unidade.id == id).first()
    if not unidade:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "UNIDADE_NAO_ENCONTRADA",
                "message": "Nenhuma unidade encontrada com o ID informado.",
                "details": [{"field": "id", "issue": f"ID {id} não existe"}],
                "path": f"/unidades/{id}"
            }
        )
    return {
        "id": unidade.id,
        "nome": unidade.nome,
        "cidade": unidade.cidade,
        "estado": unidade.estado,
        "ativa": unidade.ativa,
        "created_at": unidade.created_at
    }