from fastapi import FastAPI, Depends, HTTPException, status, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, Response
from fastapi.openapi.models import Response as OpenAPIResponse
from fastapi import status as http_status
import logging
from typing import Optional

from core.config.db import SessionLocal, Base, engine
from core.domain.cliente import Cliente, ClienteCreate, ClienteUpdate
from core.domain.favorito import (
    FavoritoCreate, FavoritoResponse, FavoritoBatchCreate
)
from core.repository.cliente_repository import ClienteRepository
from core.repository.favorito_repository import FavoritoRepository
from core.service.cliente_service import ClienteService
from core.security.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from core.service.favorito_service import FavoritoService
from externos.fake_store_product import FakeStoreProduct

logger = logging.getLogger("uvicorn.error")
# Configuração do logger
logging.basicConfig(
    level=logging.WARN,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)   

app = FastAPI(title="AqiFome RESTful API")

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_fake_store_product() -> FakeStoreProduct:
    return FakeStoreProduct()

def get_favorito_service(
    db: Session = Depends(get_db),
    fake_store_product: FakeStoreProduct = Depends(get_fake_store_product)
) -> FavoritoService:
    return FavoritoService(
        repository=FavoritoRepository(db),
        fake_store_product=fake_store_product,
    )


def get_admin_user(current_user: Cliente = Depends(get_current_user)):
    """
    Dependência que verifica se o usuário autenticado é um administrador.
    Retorna o usuário se for admin, caso contrário, levanta uma exceção HTTP 403.
    """
    if current_user.tipo != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )
    return current_user


def error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": status_code, "message": message}},
    )

@app.get("/")
def root():
    return {"message": "API Online"}

@app.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
    ):
    cliente_repo = ClienteRepository(db)
    user = cliente_repo.get_by_email(email=form_data.username)
    if not user or not verify_password(form_data.password, user.senha.get_secret_value()):
        return error_response(401, "Usuário ou senha incorretos")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Clientes ---
@app.post(
    "/clientes",
    response_model=Cliente,
    status_code=status.HTTP_201_CREATED,
    summary="Criar um novo cliente",
    responses={
        201: {"description": "Cliente criado com sucesso", "model": Cliente},
        400: {"description": "Erro de validação"},
        500: {"description": "Erro interno"},
    },
)
def criar_cliente(
    cliente: ClienteCreate = Body(..., example={
        "nome": "Edson Bezerra",
        "email": "exemplo@teste.com",
        "senha": "senha123",
        "tipo": 1
    }),
    db: Session = Depends(get_db)
):
    """
    Cria um novo cliente.
    O cliente deve fornecer ao menos nome, e-mail, senha e tipo.
    A senha será armazenada com hash.
    """
    service = ClienteService(ClienteRepository(db))
    try:
        return service.criar_cliente(cliente)
    except ValueError as e:
        logger.warning(f"Erro de validação ao criar cliente: {e}")
        return error_response(400, str(e))
    except Exception as e:
        logger.error(f"Erro inesperado ao criar cliente: {e}", exc_info=True)
        return error_response(500, "Erro interno ao criar cliente")


@app.get("/clientes", response_model=list[Cliente])
def listar_clientes(
    db: Session = Depends(get_db), admin_user: Cliente = Depends(get_admin_user)
):
    """
    Lista todos os clientes. Requer privilégios de administrador.
    """
    try:
        service = ClienteService(ClienteRepository(db))
        return service.listar_clientes()
    except Exception as e:
        logger.error(f"Erro ao listar clientes: {e}", exc_info=True)
        return error_response(500, "Erro interno ao listar clientes")
    

@app.get("/clientes/{cliente_id}", response_model=Cliente)
def buscar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Cliente = Depends(get_current_user),
):
    if current_user.tipo != 1 and current_user.id != cliente_id:
        return error_response(403, "Operação não permitida")
    service = ClienteService(ClienteRepository(db))
    cliente = service.buscar_cliente(cliente_id)
    if not cliente:
        return error_response(404, "Cliente não encontrado")
    return cliente


@app.put("/clientes/{cliente_id}", response_model=Cliente)
def atualizar_cliente(
    cliente_id: int,
    cliente: ClienteUpdate,
    db: Session = Depends(get_db),
    current_user: Cliente = Depends(get_current_user),
):
    if current_user.tipo != 1 and current_user.id != cliente_id:
        return error_response(403, "Operação não permitida")
    service = ClienteService(ClienteRepository(db))
    atualizado = service.atualizar_cliente(cliente_id, cliente)
    if not atualizado:
        return error_response(404, "Cliente não encontrado")
    return atualizado


@app.delete("/clientes/{cliente_id}")
def deletar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Cliente = Depends(get_current_user),
):
    if current_user.tipo != 1 and current_user.id != cliente_id:
        return error_response(403, "Operação não permitida")
    service = ClienteService(ClienteRepository(db))
    if not service.deletar_cliente(cliente_id):
        return error_response(404, "Cliente não encontrado")
    return {"ok": True}


# --- Favoritos ---
@app.post(
    "/clientes/{cliente_id}/favoritos",
    response_model=list[FavoritoResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar um produto aos favoritos de um cliente",
    responses={
        201: {"description": "Favoritos adicionados com sucesso", "model": FavoritoResponse},
        400: {"description": "Erro de validação"},
        403: {"description": "Operação não permitida"},
        500: {"description": "Erro interno"},
    },
    tags=["Favoritos"],
)
async def adicionar_favoritos(
    cliente_id: int,
    request_data: FavoritoBatchCreate = Body(..., example={"produto_ids": [1, 2, 3]}),
    service: FavoritoService = Depends(get_favorito_service),
    current_user: Cliente = Depends(get_current_user),
):
    """
    Adiciona um ou mais produtos aos favoritos do cliente.
    Valida os produtos via API externa e salva no cache Redis.
    """
    if cliente_id != current_user.id:
        return error_response(403, "Operação não permitida")
    try:
        favoritos_criados = await service.adicionar_favoritos(
            cliente_id=cliente_id, produto_ids=request_data.produto_ids
        )
        return favoritos_criados
    except ValueError as e:
        logger.error(f"Erro ao adicionar favoritos: {e}")
        return error_response(400, str(e))
    except Exception as e:
        logger.error(f"Erro ao adicionar favoritos: {e}")
        return error_response(500, f"Ocorreu um erro interno: {e}")


@app.get(
    "/clientes/{cliente_id}/favoritos",
    response_model=list[FavoritoResponse],
    summary="Listar favoritos de um cliente",
    responses={
        200: {"description": "Lista de favoritos do cliente", "model": FavoritoResponse},
        403: {"description": "Operação não permitida"},
        500: {"description": "Erro interno"},
    },
    tags=["Favoritos"],
)
def listar_favoritos(
    cliente_id: int,
    service: FavoritoService = Depends(get_favorito_service),
    current_user: Cliente = Depends(get_current_user),
):
    """
    Lista todos os produtos favoritos de um cliente autenticado.
    """
    if cliente_id != current_user.id:
        return error_response(403, "Operação não permitida")
    return service.listar_favoritos(cliente_id)


@app.delete(
    "/clientes/{cliente_id}/favoritos/{produto_id}",
    status_code=status.HTTP_200_OK,
    summary="Remover um produto dos favoritos de um cliente",
    responses={
        200: {"description": "Favorito removido com sucesso", "content": {"application/json": {"example": {"ok": True}}}},
        403: {"description": "Operação não permitida"},
        404: {"description": "Favorito não encontrado"},
        500: {"description": "Erro interno"},
    },
    tags=["Favoritos"],
)
def remover_favorito(
    cliente_id: int,
    produto_id: int,
    service: FavoritoService = Depends(get_favorito_service),
    current_user: Cliente = Depends(get_current_user),
):
    """
    Remove um produto dos favoritos do cliente autenticado.
    """
    if cliente_id != current_user.id:
        return error_response(403, "Operação não permitida")
    if not service.remover_favorito(cliente_id, produto_id):
        return error_response(404, "Favorito não encontrado")
    return {"ok": True}
