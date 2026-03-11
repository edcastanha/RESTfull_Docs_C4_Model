from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr
from enum import IntEnum

class TipoCliente(IntEnum):
    USER = 0
    ADMIN = 1


class ClienteBase(BaseModel):
    tipo: TipoCliente


class ClienteCreate(ClienteBase):
    nome: str
    email: EmailStr
    senha: SecretStr

class Cliente(ClienteBase):
    id: int
    nome: str
    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "exemplo": {
                "id": 0,
                "nome": "Edson Bezerra",
                "email": "exemplo@teste.com",
            }
        },
    )


class ClienteInDB(Cliente):
    """
    Modelo que inclui a senha, usado para autenticação.
    """
    senha: SecretStr


class ClienteUpdate(BaseModel):
    """
    Schema para atualização de cliente. Apenas nome e senha podem ser alterados.
    Campos vazios (None) não sobrescrevem o valor existente no banco.
    """
    nome: Optional[str] = None
    senha: Optional[SecretStr] = None


class ClienteNaoEncontradoError(Exception):
    """Exceção para cliente não encontrado."""

    pass