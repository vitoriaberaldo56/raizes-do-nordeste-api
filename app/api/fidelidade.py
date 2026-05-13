from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.domain.models import PontosFidelidade
from app.domain.enums import PerfilUsuario
from app.api.auth import get_usuario_atual

router = APIRouter(prefix="/fidelidade", tags=["Fidelidade"])

@router.get("/saldo")
def consultar_saldo(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    usuario_atual=Depends(get_usuario_atual)
):
    if not usuario_atual.consentimento_lgpd:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "CONSENTIMENTO_LGPD_AUSENTE",
                "message": "Você precisa aceitar os termos do programa de fidelidade para acessar este recurso.",
                "details": [],
                "path": "/fidelidade/saldo"
            }
        )
    offset = (page - 1) * limit
    historico = db.query(PontosFidelidade).filter(
        PontosFidelidade.usuario_id == usuario_atual.id
    ).offset(offset).limit(limit).all()

    total = db.query(PontosFidelidade).filter(
        PontosFidelidade.usuario_id == usuario_atual.id
    ).count()

    creditos = sum(p.pontos for p in historico if p.tipo == "CREDITO")
    debitos = sum(p.pontos for p in historico if p.tipo == "DEBITO")
    saldo = creditos - debitos

    return {
        "usuario_id": usuario_atual.id,
        "saldo_pontos": saldo,
        "historico": [
            {
                "pedido_id": p.pedido_id,
                "pontos": p.pontos,
                "tipo": p.tipo,
                "data": p.created_at
            } for p in historico
        ],
        "page": page,
        "limit": limit,
        "total": total
    }