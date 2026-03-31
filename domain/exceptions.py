"""
CAMADA DE DOMÍNIO — Exceções
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Exceções semânticas do domínio.
Camadas superiores nunca lançam exceções de infraestrutura ao usuário.
"""

class GastoNaoEncontradoError(Exception):
    """Gasto inexistente para o ID informado."""
    def __init__(self, id: int):
        super().__init__(f"Gasto com ID {id} não encontrado.")
        self.id = id

class RepositorioError(Exception):
    """Falha na camada de persistência — encapsula erros de infra."""
    pass

class RegraDeNegocioError(ValueError):
    """Violação de regra de negócio (ex.: valor negativo)."""
    pass