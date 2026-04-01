"""
CAMADA DE DOMÍNIO — Entidade
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Padrões aplicados:
  GoF   : Factory Method (from_primitives), encapsulamento de estado
  SOLID : SRP, OCP (extensível sem alteração)
  GRASP : Information Expert, Low Coupling (sem dep. de infra)
"""

from __future__ import annotations
from typing import Optional
from .value_objects import Descricao, Valor, DataGasto
from decimal import Decimal

class Gasto:
    """
    Entidade de domínio central.
    Invariantes de negócio protegidas por propriedades e Value Objects.
    Sem qualquer conhecimento de banco de dados ou framework.
    """

    def __init__(
        self,
        descricao: Descricao,
        valor: Valor,
        data_gasto: DataGasto,
        id: Optional[int] = None,
    ) -> None:
        self._id = id
        self._descricao = descricao
        self._valor = valor
        self._data_gasto = data_gasto

    # ── Factory Method ───────────────────────────────────────────────

    @classmethod
    def novo(
        cls,
        descricao: str,
        valor: Decimal | int | str,
        data_gasto: Optional[str] = None,
    ) -> Gasto:
        """Cria um Gasto transiente (sem ID) a partir de primitivos."""
        return cls(
            descricao=Descricao(descricao),
            valor=Valor.de(valor),
            data_gasto=DataGasto.de_string(data_gasto) if data_gasto else DataGasto.hoje(),
        )
    
    # ── Propriedades (read-only) ──────────────────────────────────────

    @property
    def id(self) -> Optional[int]:
        return self._id
 
    @property
    def descricao(self) -> Descricao:
        return self._descricao
 
    @property
    def valor(self) -> Valor:
        return self._valor
 
    @property
    def data_gasto(self) -> DataGasto:
        return self._data_gasto
    
    # ── Comportamentos de domínio ─────────────────────────────────────

    def alterar_descricao(self, nova: str) -> None:
        self._descricao = Descricao(nova)

    def alterar_valor(self, novo: float | int | str) -> None:
        self._valor = Valor.de(novo)

    def alterar_data(self, nova: str) -> None:
        self._data_gasto = DataGasto.de_string(nova)

    # ── Representação ─────────────────────────────────────────────────

    def __str__(self) -> str:
        return (
            f"ID: {self._id} | Descrição: {self._descricao} "
            f"| Valor: {self._valor} | Data: {self._data_gasto}"
        )
    
    def __repr__(self) -> str:
        return (
            f"Gasto(id={self._id!r}, descricao={str(self._descricao)!r}, "
            f"valor={str(self._valor)!r}, data={str(self._data_gasto)!r})"
        )