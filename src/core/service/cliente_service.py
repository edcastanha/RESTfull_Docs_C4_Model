from core.domain.cliente import (
    Cliente,
    ClienteCreate,
    ClienteUpdate,  # Alterado de ClienteUpdateRequest
    ClienteNaoEncontradoError,
)
from core.repository.cliente_repository import ClienteRepository
from core.security.security import get_password_hash
from pydantic import SecretStr

class ClienteService:
    """
    Serviço de regras de negócio para clientes.

    Responsável por validações e operações de alto nível envolvendo clientes.
    """
    def __init__(self, repository: ClienteRepository):
        """
        Inicializa o serviço de clientes.

        Args:
            repository (ClienteRepository): Instância do repositório de clientes.
        """
        self.repository = repository

    def criar_cliente(self, cliente_data: ClienteCreate) -> Cliente:
        """
        Cria um novo cliente após validação de unicidade do e-mail e hashing da senha.

        Args:
            cliente_data (ClienteCreate): Dados do cliente a ser criado.
        Returns:
            Cliente: Cliente criado.
        Raises:
            ValueError: Se o e-mail já estiver cadastrado.
        """
        if self.repository.get_by_email(cliente_data.email):
            raise ValueError("E-mail já cadastrado")
        # Hash da senha antes de salvar
        hashed_password = get_password_hash(cliente_data.senha.get_secret_value())
        cliente_com_senha_hash = cliente_data.model_copy(
            update={"senha": SecretStr(hashed_password)}
        )

        return self.repository.create(cliente_com_senha_hash)

    def listar_clientes(self):
        """
        Lista todos os clientes cadastrados.

        Returns:
            list[Cliente]: Lista de clientes.
        """
        return self.repository.list()

    def buscar_cliente(self, cliente_id: int):
        """
        Busca um cliente pelo ID.

        Args:
            cliente_id (int): ID do cliente.
        Returns:
            Cliente ou None: Cliente encontrado ou None.
        """
        """
        Busca um cliente pelo ID.

        Args:
            cliente_id (int): ID do cliente.
        Returns:
            Cliente ou None: Cliente encontrado ou None.
        """
        return self.repository.get_by_id(cliente_id)

    def atualizar_cliente(
        self, cliente_id: int, cliente_update: ClienteUpdate
    ) -> Cliente:
        """
        Atualiza um cliente existente.

        Args:
            cliente_id (int): O ID do cliente a ser atualizado.
            cliente_update (ClienteUpdate): Os dados de atualização do cliente.

        Returns:
            Cliente: O cliente atualizado.

        Raises:
            ClienteNaoEncontradoError: Se o cliente não for encontrado.
        """
        # O repositório agora lida com o objeto Pydantic diretamente
        cliente_atualizado = self.repository.update(cliente_id, cliente_update)

        if not cliente_atualizado:
            raise ClienteNaoEncontradoError()

        return cliente_atualizado

    def deletar_cliente(self, cliente_id: int):
        """
        Remove um cliente do banco de dados.

        Args:
            cliente_id (int): ID do cliente a ser removido.
        Returns:
            bool: True se removido, False caso contrário.
        """
        """
        Remove um cliente do banco de dados.

        Args:
            cliente_id (int): ID do cliente a ser removido.
        Returns:
            bool: True se removido, False caso contrário.
        """
        return self.repository.delete(cliente_id)
