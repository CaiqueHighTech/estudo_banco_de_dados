"""
PONTO DE ENTRADA — Composition Root
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
O único lugar onde as dependências concretas são instanciadas e conectadas.
Nenhuma outra camada conhece a implementação concreta do repositório.
 
Padrões aplicados:
  GoF   : Abstract Factory (implícito na montagem das dependências)
  SOLID : DIP — tudo depende de abstrações; o wiring fica aqui
  GRASP : Pure Fabrication — classe auxiliar sem responsabilidade de domínio
 
Microsserviços:
  Para escalar para microsserviços real, troque SQLAlchemyGastoRepository
  por uma implementação HTTP (ex.: GastoHttpRepository) que chame o serviço
  remoto. Nenhuma outra linha do projeto precisa mudar.
"""

import sys
from __future__ import annotations

# ── Infraestrutura ────────────────────────────────────────────────────
from infrastructure.orm.database import DatabaseSession
from infrastructure.repositories.gasto_repository import (
    GastoRepository,
)
 
# ── Aplicação ─────────────────────────────────────────────────────────
from application.services.gasto_service import GastoService
 
# ── Shared ────────────────────────────────────────────────────────────
from shared.event_bus import EventBus, LoggingHandler, AuditHandler
 
# ── Apresentação ──────────────────────────────────────────────────────
from presentation.cli.view import GastoView
from presentation.cli.controller import MenuController

def _construir_event_bus() -> EventBus:
    """Monta o barramento de eventos com os handlers desejados."""
    bus = EventBus()
    bus.registrar("GASTO_CRIADO", LoggingHandler)
    bus.registrar("GASTO_CRIADO",     LoggingHandler())
    bus.registrar("GASTO_ATUALIZADO", LoggingHandler())
    bus.registrar("GASTO_REMOVIDO",   LoggingHandler())
    bus.registrar("*",                AuditHandler())
    return bus

def main() -> None:
    db_url = f"sqlite:///{sys.argv[1]}" if len(sys.argv) > 1 else "sqlite:///estudo.db"

    # ── Wiring (Composition Root) ─────────────────────────────────────
    db         = DatabaseSession(db_url)
    repository = GastoRepository(db)
    event_bus  = _construir_event_bus()
    service    = GastoService(repository, event_bus)
    view       = GastoView()
    controller = MenuController(service, view)

    # ── Execução ──────────────────────────────────────────────────────
    try:
        controller.executar()
    finally:
        db.fechar()

if __name__ == "__main__":
    main()

