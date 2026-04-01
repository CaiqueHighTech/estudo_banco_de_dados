"""
SHARED — Event Bus
━━━━━━━━━━━━━━━━━━
Padrões aplicados:
  GoF   : Observer — publishers e subscribers desacoplados
          Singleton — bus único por processo
  SOLID : OCP — novos handlers sem tocar no EventBus
          DIP — GastoService depende do EventBus, não de prints
  GRASP : Low Coupling — serviços nunca chamam uns aos outros diretamente
 
Uso:
    bus = EventBus()
    bus.registrar("GASTO_CRIADO", LoggingHandler())
    bus.publicar("GASTO_CRIADO", {"id": 1})
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any

# ── Contrato do Observer ──────────────────────────────────────────────
class IEventHandler(ABC):
    @abstractmethod
    def handle(self, event_type: str, payload: Dict[str, Any]) -> None: ...

# ── Implementações concretas de Handlers ─────────────────────────────
class LoggingHandler(IEventHandler):
    """Loga todos os eventos com timestamp."""
 
    _EMOJIS = {
        "GASTO_CRIADO":     "📥",
        "GASTO_ATUALIZADO": "✏️ ",
        "GASTO_REMOVIDO":   "🗑️ ",
    }

    def handle(self, event_type: str, payload: Dict[str, Any]) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        emoji = self._EMOJIS.get(event_type, "📌")
        print(f"  [{ts}] {emoji} {event_type} → {payload}")

class AuditHandler(IEventHandler):
    """Mantém histórico em memória (poderia persistir em arquivo/DB)."""


    def __init__(self) -> None:
        self._historico: List[Dict[str, Any]] = []

    def handle(self, event_type: str, payload: Dict[str, Any]) -> None:
        self._historico.append({
            "ts": datetime.now().isoformat(),
            "event_type": event_type,
            "payload":    payload,
        })

    @property
    def historico(self) -> List[Dict[str, Any]]:
        return list(self._historico)

# ── Event Bus (Singleton + Observer Subject) ─────────────────────────
class EventBus:
    """
    Barramento de eventos — Singleton.
    Desacopla emissores (services) de receptores (handlers).
    """

    _instance: EventBus | None = None

    def __new__(cls) -> EventBus:
        if cls._instance is None:
            obj = super().__new__(cls)
            obj._handlers: Dict[str, List[IEventHandler]] = {}
            cls._instance = obj
        return cls._instance

    def registrar(self, event_type: str, handler: IEventHandler) -> None:
        """Registra um handler para um tipo de evento (ou '*' para todos)."""
        self._handlers.setdefault(event_type, []).append(handler)

    def publicar(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Notifica todos os handlers registrados para o evento."""
        for h in self._handlers.get(event_type, []):
            h.handle(event_type, payload)
        for h in self._handlers.get("*", []):
            h.handle(event_type, payload)