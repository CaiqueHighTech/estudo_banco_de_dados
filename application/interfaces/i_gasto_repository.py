"""
CAMADA DE APLICAÇÃO — Interface do Repositório
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Padrões aplicados:
  GoF   : Repository Pattern (interface)
  SOLID : DIP — aplicação depende desta abstração, não do SQLAlchemy
          ISP — interface coesa com operações relacionadas
  GRASP : Polymorphism — implementações trocáveis

A aplicação NUNCA importa do pacote infrastructure diretamente.
O 'wiring' é feito apenas no main.py (Composition Root).
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional

from ..dtos import CriarGastoDTO, AtualizarGastoDTO, GastoDTO, EstatisticasDTO


class IGastoRepository(ABC):
    """Contrato que qualquer implementação de persistência deve honrar."""

    # ── Escrita ───────────────────────────────────────────────────────

    @abstractmethod
    def criar(self, dto: CriarGastoDTO) -> GastoDTO: ...

    @abstractmethod
    def atualizar(self, dto: AtualizarGastoDTO) -> GastoDTO: ...

    @abstractmethod
    def deletar(self, id: int) -> None: ...

    # ── Leitura ───────────────────────────────────────────────────────

    @abstractmethod
    def buscar_todos(self) -> List[GastoDTO]: ...

    @abstractmethod
    def buscar_por_id(self, id: int) -> Optional[GastoDTO]: ...

    @abstractmethod
    def buscar_por_descricao(self, termo: str) -> List[GastoDTO]: ...

    @abstractmethod
    def buscar_por_valor_minimo(self, valor_min: float) -> List[GastoDTO]: ...

    @abstractmethod
    def buscar_por_valor_maximo(self, valor_max: float) -> List[GastoDTO]: ...

    @abstractmethod
    def buscar_por_periodo(self, inicio: str, fim: str) -> List[GastoDTO]: ...

    @abstractmethod
    def buscar_por_mes_ano(self, mes_ano: str) -> List[GastoDTO]: ...

    # ── Agregação ─────────────────────────────────────────────────────

    @abstractmethod
    def obter_estatisticas(self) -> EstatisticasDTO: ...