from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.infrastructure.database import get_db
from app.domain.models import Pedido, ItemPedido, Produto, Unidade, Estoque
from app.domain.enums import CanalPedido, StatusPedido, PerfilUsuario
from app.api.auth import get_usuario_atual

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

class ItemRequest(BaseModel):
    produto_id: int
    quantidade: int

class PedidoRequest(BaseModel):
    unidade_id: int
    canalPedido: CanalPedido
    itens: List[ItemRequest]
    forma_pagamento: str

class StatusRequest(BaseModel):
    status: StatusPedido

# Transições de status permitidas
TRANSICOES_VALIDAS = {
    StatusPedido.AGUARDANDO_PAGAMENTO: [StatusPedido.EM_PREPARO, StatusPedido.CANCELADO],
    StatusPedido.EM_PREPARO: [StatusPedido.PRONTO, StatusPedido.CANCELADO],
    StatusPedido.PRONTO: [StatusPedido.ENTREGUE],
    StatusPedido.ENTREGUE: [],
    StatusPedido.CANCELADO: []
}

@router.post("", status_code=201)
def criar_pedido(
    request: PedidoRequest,
    db: Session = Depends(get_db),
    usuario_atual=Depends(get_usuario_atual)
):
    if usuario_atual.perfil not in [PerfilUsuario.CLIENTE, PerfilUsuario.ATENDENTE]:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "SEM_PERMISSAO",
                "message": "Seu perfil não tem permissão para criar pedidos.",
                "details": [],
                "path": "/pedidos"
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
                "path": "/pedidos"
            }
        )
    itens_validados = []
    total = 0.0

    for item in request.itens:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if not produto:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "PRODUTO_NAO_ENCONTRADO",
                    "message": f"Produto ID {item.produto_id} não encontrado.",
                    "details": [{"field": "produto_id", "issue": f"ID {item.produto_id} não existe"}],
                    "path": "/pedidos"
                }
            )
        estoque = db.query(Estoque).filter(
            Estoque.unidade_id == request.unidade_id,
            Estoque.produto_id == item.produto_id
        ).first()
        if not estoque or estoque.quantidade < item.quantidade:
            disponivel = estoque.quantidade if estoque else 0
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "ESTOQUE_INSUFICIENTE",
                    "message": "Não há quantidade suficiente para um ou mais itens do pedido.",
                    "details": [{"field": f"itens[{request.itens.index(item)}].quantidade", "issue": f"Disponível: {disponivel}, solicitado: {item.quantidade}"}],
                    "path": "/pedidos"
                }
            )
        itens_validados.append({
            "produto": produto,
            "estoque": estoque,
            "quantidade": item.quantidade,
            "preco_unitario": produto.preco
        })
        total += produto.preco * item.quantidade

    novo_pedido = Pedido(
        usuario_id=usuario_atual.id,
        unidade_id=request.unidade_id,
        canal_pedido=request.canalPedido,
        status=StatusPedido.AGUARDANDO_PAGAMENTO,
        total=total
    )
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    itens_response = []
    for item_data in itens_validados:
        novo_item = ItemPedido(
            pedido_id=novo_pedido.id,
            produto_id=item_data["produto"].id,
            quantidade=item_data["quantidade"],
            preco_unitario=item_data["preco_unitario"]
        )
        db.add(novo_item)
        itens_response.append({
            "produto_id": item_data["produto"].id,
            "nome": item_data["produto"].nome,
            "quantidade": item_data["quantidade"],
            "preco_unitario": item_data["preco_unitario"]
        })

    db.commit()

    return {
        "pedido_id": novo_pedido.id,
        "status": novo_pedido.status,
        "canal_pedido": novo_pedido.canal_pedido,
        "unidade_id": novo_pedido.unidade_id,
        "total": novo_pedido.total,
        "itens": itens_response,
        "created_at": novo_pedido.created_at
    }

@router.get("")
def listar_pedidos(
    canalPedido: CanalPedido = None,
    status: StatusPedido = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    usuario_atual=Depends(get_usuario_atual)
):
    offset = (page - 1) * limit
    query = db.query(Pedido)

    if usuario_atual.perfil == PerfilUsuario.CLIENTE:
        query = query.filter(Pedido.usuario_id == usuario_atual.id)
    if canalPedido:
        query = query.filter(Pedido.canal_pedido == canalPedido)
    if status:
        query = query.filter(Pedido.status == status)

    total = query.count()
    pedidos = query.offset(offset).limit(limit).all()

    return {
        "data": [
            {
                "pedido_id": p.id,
                "usuario_id": p.usuario_id,
                "canal_pedido": p.canal_pedido,
                "status": p.status,
                "total": p.total,
                "created_at": p.created_at
            } for p in pedidos
        ],
        "page": page,
        "limit": limit,
        "total": total
    }

@router.get("/{id}")
def buscar_pedido(
    id: int,
    db: Session = Depends(get_db),
    usuario_atual=Depends(get_usuario_atual)
):
    pedido = db.query(Pedido).filter(Pedido.id == id).first()
    if not pedido:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "PEDIDO_NAO_ENCONTRADO",
                "message": "Pedido não encontrado.",
                "details": [{"field": "id", "issue": f"ID {id} não existe"}],
                "path": f"/pedidos/{id}"
            }
        )
    if usuario_atual.perfil == PerfilUsuario.CLIENTE and pedido.usuario_id != usuario_atual.id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "ACESSO_NEGADO",
                "message": "Você não tem permissão para acessar este pedido.",
                "details": [],
                "path": f"/pedidos/{id}"
            }
        )
    return {
        "pedido_id": pedido.id,
        "usuario_id": pedido.usuario_id,
        "unidade_id": pedido.unidade_id,
        "canal_pedido": pedido.canal_pedido,
        "status": pedido.status,
        "total": pedido.total,
        "itens": [
            {
                "produto_id": i.produto_id,
                "nome": i.produto.nome,
                "quantidade": i.quantidade,
                "preco_unitario": i.preco_unitario
            } for i in pedido.itens
        ],
        "pagamento": {
            "status_pagamento": pedido.pagamento.status_pagamento,
            "forma_pagamento": pedido.pagamento.forma_pagamento
        } if pedido.pagamento else None,
        "created_at": pedido.created_at
    }

@router.patch("/{id}/status")
def atualizar_status(
    id: int,
    request: StatusRequest,
    db: Session = Depends(get_db),
    usuario_atual=Depends(get_usuario_atual)
):
    if usuario_atual.perfil not in [PerfilUsuario.COZINHA, PerfilUsuario.GERENTE, PerfilUsuario.ADMIN]:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "SEM_PERMISSAO",
                "message": "Seu perfil não tem permissão para atualizar status.",
                "details": [],
                "path": f"/pedidos/{id}/status"
            }
        )
    pedido = db.query(Pedido).filter(Pedido.id == id).first()
    if not pedido:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "PEDIDO_NAO_ENCONTRADO",
                "message": "Pedido não encontrado.",
                "details": [{"field": "id", "issue": f"ID {id} não existe"}],
                "path": f"/pedidos/{id}/status"
            }
        )
    if request.status not in TRANSICOES_VALIDAS[pedido.status]:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "TRANSICAO_STATUS_INVALIDA",
                "message": f"Não é possível alterar um pedido com status {pedido.status}.",
                "details": [{"field": "status", "issue": f"Transição {pedido.status} → {request.status} não permitida"}],
                "path": f"/pedidos/{id}/status"
            }
        )
    status_anterior = pedido.status
    pedido.status = request.status
    db.commit()
    return {
        "pedido_id": pedido.id,
        "status_anterior": status_anterior,
        "status_atual": pedido.status
    }