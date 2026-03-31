"""
CAMADA DE APLICAÇÃO — Serviço de Gastos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Padrões aplicados:
  GoF   : Facade — ponto de entrada único para casos de uso
          Observer — publica eventos via EventBus
  SOLID : SRP (orquestra, não implementa)
          OCP (extensível: novos casos de uso sem alterar os existentes)
          DIP (injeta IGastoRepository e EventBus)
  GRASP : Controller — coordena os use cases da feature de gastos
          Low Coupling — não depende de SQLAlchemy, nem de CLI
 
Este serviço poderia ser exposto via HTTP (FastAPI) sem alterar uma linha.
"""

from __future__ import annotations
from typing import List, TYPE_CHECKING
from ..interfaces.i_gasto_repository import IGastoRepository
from ..dtos import CriarGastoDTO, AtualizarGastoDTO, GastoDTO, EstatisticasDTO
from ...domain.exceptions import GastoNaoEncontradoError

if TYPE_CHECKING:
    from ...shared.event_bus import EventBus
    from ...presentation.strategies.busca_strategies import IBuscaStrategy

class GastoService:
    """
    Serviço de aplicação — implementa os casos de uso do domínio.
    Toda lógica de orquestração passa por aqui.
    """

    def __init__(
        self,
        repository: IGastoRepository,
        event_bus: EventBus,
    ) -> None:
        self._repo = repository
        self._bus = event_bus

    # ── Casos de Uso: Escrita ─────────────────────────────────────────

    def registrar_gasto(self, dto: CriarGastoDTO) -> GastoDTO:
        gasto = self._repo.criar(dto)
        self._bus.publicar("GASTO_CRIADO", {"id": gasto.id, "descricao": gasto.descricao})
        return gasto
    
    def modificar_gasto(self, dto: AtualizarGastoDTO) -> GastoDTO:
        self._garantir_existencia(dto.id)
        gasto = self._repo.atualizar(dto)
        self._bus.publicar("GASTO_ATUALIZADO", {"id": dto.id})
        return gasto
    
    def remover_gasto(self, id: int) -> None:
        self._garantir_existencia(id)
        self._repo.deletar(id)
        self._bus.publicar("GASTO_REMOVIDO", {"id": id})

    # ── Casos de Uso: Leitura ─────────────────────────────────────────

    def listar_gastos(self) -> List[GastoDTO]:
        return self._repo.buscar_todos()
    
    def obter_gasto(self, id: int) -> GastoDTO:
        return self._garantir_existencia(id)
    
    def buscar_gastos(self, estrategia: IBuscaStrategy) -> List[GastoDTO]:
        """
        Strategy Pattern: delega a lógica de filtragem à estratégia injetada.
        Aberto para novas estratégias, fechado para modificação.
        """
        return estrategia.executar(self._repo)
    
    def obter_estatisticas(self) -> EstatisticasDTO:
        return self._repo.obter_estatisticas()

    # ── Helpers privados ──────────────────────────────────────────────

    def _garantir_existencia(self, id: int) -> GastoDTO:
        gasto = self._repo.buscar_por_id(id)
        if gasto is None:
            raise GastoNaoEncontradoError(id)
        return gasto
        