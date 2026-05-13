from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.infrastructure.database import Base
from app.domain.enums import CanalPedido, StatusPedido, PerfilUsuario, StatusPagamento, TipoMovimentacao

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    senha_hash = Column(String, nullable=False)
    perfil = Column(SAEnum(PerfilUsuario), nullable=False)
    consentimento_lgpd = Column(Boolean, default=False)
    data_consentimento = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    pedidos = relationship("Pedido", back_populates="usuario")
    pontos = relationship("PontosFidelidade", back_populates="usuario")

class Unidade(Base):
    __tablename__ = "unidades"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cidade = Column(String, nullable=False)
    estado = Column(String, nullable=False)
    ativa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    pedidos = relationship("Pedido", back_populates="unidade")
    estoques = relationship("Estoque", back_populates="unidade")

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    preco = Column(Float, nullable=False)
    categoria = Column(String, nullable=False)
    disponivel_globalmente = Column(Boolean, default=True)
    estoques = relationship("Estoque", back_populates="produto")
    itens = relationship("ItemPedido", back_populates="produto")

class Estoque(Base):
    __tablename__ = "estoque"
    id = Column(Integer, primary_key=True, index=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, default=0)
    unidade = relationship("Unidade", back_populates="estoques")
    produto = relationship("Produto", back_populates="estoques")

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    canal_pedido = Column(SAEnum(CanalPedido), nullable=False)
    status = Column(SAEnum(StatusPedido), default=StatusPedido.AGUARDANDO_PAGAMENTO)
    total = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    usuario = relationship("Usuario", back_populates="pedidos")
    unidade = relationship("Unidade", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido")
    pagamento = relationship("Pagamento", back_populates="pedido", uselist=False)
    pontos = relationship("PontosFidelidade", back_populates="pedido")

class ItemPedido(Base):
    __tablename__ = "itens_pedido"
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto", back_populates="itens")

class Pagamento(Base):
    __tablename__ = "pagamentos"
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    forma_pagamento = Column(String, nullable=False)
    status_pagamento = Column(SAEnum(StatusPagamento), default=StatusPagamento.PENDENTE)
    payload_resposta = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    pedido = relationship("Pedido", back_populates="pagamento")

class PontosFidelidade(Base):
    __tablename__ = "pontos_fidelidade"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=True)
    pontos = Column(Integer, nullable=False)
    tipo = Column(SAEnum(TipoMovimentacao), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    usuario = relationship("Usuario", back_populates="pontos")
    pedido = relationship("Pedido", back_populates="pontos")