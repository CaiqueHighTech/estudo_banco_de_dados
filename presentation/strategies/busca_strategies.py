"""
CAMADA DE APRESENTAÇÃO — Estratégias de Busca
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Padrões aplicados:
  GoF   : Strategy — algoritmo de busca encapsulado e intercambiável
  SOLID : OCP — novas buscas sem alterar GastoService ou o controller
          ISP — interface mínima (apenas executar)
  GRASP : Polymorphism — comportamento diferente pela mesma interface
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from application.interfaces.i_gasto_repository import IGastoRepository
from application.dtos import GastoDTO
from decimal import Decimal

class IBuscaStrategy(ABC):
    """Contrato de estratégia de busca."""

    @abstractmethod
    def executar(self, repo: IGastoRepository) -> List[GastoDTO]: ...

class BuscaPorDescricao(IBuscaStrategy):
    def __init__(self, termo: str) -> None:
        self._termo = termo
    
    def executar(self, repo: IGastoRepository) -> List[GastoDTO]:
        return repo.buscar_por_descricao(self._termo)
    
class BuscaPorValorMinimo(IBuscaStrategy):
    def __init__(self, valor_min: Decimal) -> None:
        self._valor_min = valor_min

    def executar(self, repo: IGastoRepository) -> List[GastoDTO]:
        return repo.buscar_por_valor_minimo(self._valor_min)
    
class BuscaPorValorMaximo(IBuscaStrategy):
    def __init__(self, valor_max: Decimal) -> None:
        self._valor_max = valor_max
 
    def executar(self, repo: IGastoRepository) -> List[GastoDTO]:
        return repo.buscar_por_valor_maximo(self._valor_max)

class BuscaPorPeriodo(IBuscaStrategy):
    def __init__(self, inicio: str, fim: str) -> None:
        self._inicio = inicio
        self._fim    = fim
 
    def executar(self, repo: IGastoRepository) -> List[GastoDTO]:
        return repo.buscar_por_periodo(self._inicio, self._fim)

class BuscaPorMesAnoDia(IBuscaStrategy):
    def __init__(self, mes_ano: str) -> None:
        self._mes_ano = mes_ano
 
    def executar(self, repo: IGastoRepository) -> List[GastoDTO]:
        return repo.buscar_por_mes_ano_dia(self._mes_ano)