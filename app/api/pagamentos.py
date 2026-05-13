from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.infrastructure.database import get_db
from app.domain.models import Pedido, Pagamento
from app.domain.enums import StatusPagamento, StatusPedido, PerfilUsuario
from app.api.auth import get_usuario_atual
import random

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])

class PagamentoRequest(BaseModel):
    forma_pagamento: str

@router.post("/{pedido_id}/processar")
def processar_pagamento(
    pedido_id: int,
    request: PagamentoRequest,
    db: Session = Depends(get_db),
    usuario_atual=Depends(get_usuario_atual)
):
    if usuario_atual.perfil not in [PerfilUsuario.CLIENTE, PerfilUsuario.ATENDENTE]:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "SEM_PERMISSAO",
                "message": "Seu perfil não tem permissão para processar pagamentos.",
                "details": [],
                "path": f"/pagamentos/{pedido_id}/processar"
            }
        )
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "PEDIDO_NAO_ENCONTRADO",
                "message": "Pedido não encontrado.",
                "details": [{"field": "pedido_id", "issue": f"ID {pedido_id} não existe"}],
                "path": f"/pagamentos/{pedido_id}/processar"
            }
        )
    if pedido.pagamento:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "PAGAMENTO_JA_PROCESSADO",
                "message": "Este pedido já possui um pagamento registrado.",
                "details": [{"field": "pedido_id", "issue": f"Pagamento já registrado para o pedido {pedido_id}"}],
                "path": f"/pagamentos/{pedido_id}/processar"
            }
        )

    # Simulação do mock — 80% aprovado, 20% recusado
    aprovado = random.random() > 0.2

    if aprovado:
        status_pagamento = StatusPagamento.APROVADO
        pedido.status = StatusPedido.EM_PREPARO
        payload = {
            "transacao_id": f"mock-txn-{pedido_id}-{random.randint(1000,9999)}",
            "mensagem": "Pagamento aprovado com sucesso (simulado)"
        }
    else:
        status_pagamento = StatusPagamento.RECUSADO
        payload = {
            "mensagem": "Saldo insuficiente (simulado)"
        }

    novo_pagamento = Pagamento(
        pedido_id=pedido_id,
        forma_pagamento=request.forma_pagamento,
        status_pagamento=status_pagamento,
        payload_resposta=str(payload)
    )
    db.add(novo_pagamento)
    db.commit()

    return {
        "pedido_id": pedido_id,
        "status_pagamento": status_pagamento,
        "status_pedido_atualizado": pedido.status,
        "payload": payload
    }