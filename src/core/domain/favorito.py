from typing import List
from pydantic import BaseModel, ConfigDict
from core.domain.produto import ProdutoExterno

class FavoritoBase(BaseModel):
    """Modelo base para Favorito com campos comuns."""
    cliente_id: int
    produto_id: int
    
    model_config = ConfigDict(frozen=True)

class Favorito(FavoritoBase):
    """
    Modelo de domínio principal para Favorito.
    Representa um favorito como ele existe no banco de dados.
    """
    id: int

    model_config = ConfigDict(from_attributes=True, frozen=True)

# Mantido por clareza semântica - indica claramente seu uso na criação
class FavoritoCreate(FavoritoBase):
    """DTO para criar um favorito (cliente_id, produto_id)."""
    pass

class FavoritoResponse(BaseModel):
    """
    DTO para retornar um favorito com detalhes do produto.
    """
    id: int
    cliente_id: int
    produto: ProdutoExterno

    model_config = ConfigDict(from_attributes=True, frozen=True)

class FavoritoBatchCreate(BaseModel):
    """
    DTO para criação de múltiplos favoritos de uma vez.
    Recebe uma lista de IDs de produtos a serem favoritados por um cliente.
    """
    produto_ids: List[int]
    
    model_config = ConfigDict(frozen=True)
