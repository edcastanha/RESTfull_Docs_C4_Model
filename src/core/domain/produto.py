from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, HttpUrl, Field
from decimal import Decimal

class Rating(BaseModel):
    """
    Modelo para avaliações de produtos (rating).
    Contém a nota média e quantidade de avaliações.
    """
    rate: float
    count: int
    
    model_config = ConfigDict(frozen=True)

class ProdutoExterno(BaseModel):
    """
    Modelo que representa um produto externo proveniente de APIs terceiras (FakeStore).
    Mantém os dados do produto de forma consistente dentro da aplicação.
    """
    id: int
    title: str
    price: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2, description="Preço do produto (positivo, máximo 2 casas decimais)")]
    description: str
    category: str
    image: str  # String URL - validação feita apenas quando necessário
    rating: Optional[Rating] = None  # Alguns produtos podem não ter avaliações
    
    model_config = ConfigDict(from_attributes=True, frozen=True)
