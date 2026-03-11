import pytest
from pydantic import ValidationError

from decimal import Decimal
from pydantic import HttpUrl
from core.domain.favorito import (
    Favorito,
    FavoritoBase,
    FavoritoCreate,
    FavoritoBatchCreate,
    FavoritoResponse,
)
from core.domain.produto import ProdutoExterno


def test_favorito_create_request():
    """Testa a criação de uma requisição para adicionar favoritos."""
    request_data = {"produto_ids": [1, 5, 10]}
    request_model = FavoritoBatchCreate(**request_data)
    assert request_model.produto_ids == [1, 5, 10]


def test_favorito_base_model():
    """Testa o modelo base de Favorito."""
    favorito = FavoritoBase(cliente_id=1, produto_id=2)
    assert favorito.cliente_id == 1
    assert favorito.produto_id == 2


def test_favorito_create_model():
    """Testa o DTO interno de criação de Favorito."""
    favorito = FavoritoCreate(cliente_id=1, produto_id=3)
    assert favorito.cliente_id == 1
    assert favorito.produto_id == 3


def test_favorito_domain_model():
    """Testa o modelo de domínio Favorito."""
    favorito = Favorito(id=10, cliente_id=1, produto_id=1)
    assert favorito.id == 10
    assert favorito.cliente_id == 1
    assert favorito.produto_id == 1


def test_produto_externo_model():
    """Testa o modelo de produto externo."""
    from core.domain.produto import Rating
    
    # Teste com rating
    produto = ProdutoExterno(
        id=1,
        title="Teste",
        price=Decimal("10.50"),
        description="Descrição de teste",
        category="Categoria Teste",
        image="https://example.com/image.jpg",
        rating=Rating(rate=4.5, count=120)
    )
    assert produto.id == 1
    assert produto.title == "Teste"
    assert produto.price == Decimal("10.50")
    assert produto.description == "Descrição de teste"
    assert produto.rating.rate == 4.5
    assert produto.rating.count == 120
    
    # Teste sem rating (deve funcionar também)
    produto_sem_rating = ProdutoExterno(
        id=2,
        title="Teste Sem Rating",
        price=Decimal("20.75"),
        description="Descrição de teste sem rating",
        category="Categoria Teste",
        image="https://example.com/image2.jpg"
    )
    assert produto_sem_rating.rating is None


def test_favorito_response_model():
    """Testa o modelo de resposta da API para um favorito."""
    from core.domain.produto import Rating
    
    produto = ProdutoExterno(
        id=1,
        title="Teste",
        price=Decimal("10.50"),
        description="Descrição de teste",
        category="Categoria Teste",
        image="https://example.com/image.jpg",
        rating=Rating(rate=4.5, count=120)
    )
    response = FavoritoResponse(id=20, cliente_id=1, produto=produto)
    assert response.id == 20
    assert response.cliente_id == 1
    assert response.produto.rating is not None
    assert response.produto.rating.rate == 4.5
    assert response.produto.id == 1
