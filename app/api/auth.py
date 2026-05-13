from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.infrastructure.database import get_db
from app.domain.models import Usuario
from app.domain.enums import PerfilUsuario
from app.application.auth_service import (
    hash_senha, verificar_senha, criar_token,
    decodificar_token, buscar_usuario_por_email
)

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class CadastroRequest(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: PerfilUsuario
    consentimento_lgpd: bool

def get_usuario_atual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decodificar_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "NAO_AUTENTICADO",
                "message": "Token de acesso ausente ou inválido.",
                "details": [],
                "path": "/auth"
            }
        )
    usuario = db.query(Usuario).filter(
        Usuario.id == int(payload.get("sub"))
    ).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado.")
    return usuario

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    usuario = buscar_usuario_por_email(db, request.email)
    if not usuario or not verificar_senha(request.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=401,
            detail={
                "error": "CREDENCIAIS_INVALIDAS",
                "message": "E-mail ou senha inválidos.",
                "details": [],
                "path": "/auth/login"
            }
        )
    token = criar_token({"sub": str(usuario.id), "perfil": usuario.perfil})
    return {
        "accessToken": token,
        "tokenType": "Bearer",
        "expiresIn": 3600,
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "perfil": usuario.perfil
        }
    }

@router.post("/cadastro", status_code=201)
def cadastro(request: CadastroRequest, db: Session = Depends(get_db)):
    if buscar_usuario_por_email(db, request.email):
        raise HTTPException(
            status_code=409,
            detail={
                "error": "EMAIL_JA_CADASTRADO",
                "message": "Este e-mail já está em uso.",
                "details": [{"field": "email", "issue": "Já existe conta com este e-mail"}],
                "path": "/auth/cadastro"
            }
        )
    novo = Usuario(
        nome=request.nome,
        email=request.email,
        senha_hash=hash_senha(request.senha),
        perfil=request.perfil,
        consentimento_lgpd=request.consentimento_lgpd,
        data_consentimento=datetime.utcnow() if request.consentimento_lgpd else None
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return {
        "id": novo.id,
        "nome": novo.nome,
        "email": novo.email,
        "perfil": novo.perfil,
        "created_at": novo.created_at
    }