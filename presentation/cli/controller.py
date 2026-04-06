"""
CAMADA DE APRESENTAÇÃO — Controller CLI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Padrões aplicados:
  GoF   : Command — delega para objetos ICommand
  MVC   : Controller — coordena View e Model (via Service)
  SOLID : OCP — novas opções de menu = novas classes ICommand
  GRASP : Controller — ponto de entrada das interações do usuário
          Low Coupling — nunca toca em repositório ou ORM
"""

from __future__ import annotations
from typing import Dict

from application.services.gasto_service import GastoService
from .commands import (
    ICommand,
    InserirGastoCommand,
    ListarGastosCommand,
    BuscarGastosCommand,
    AtualizarGastoCommand,
    DeletarGastoCommand,
    EstatisticasCommand,
    LimparTelaCommand,
)
from .view import GastoView

class MenuController:
    """
    Controlador principal — gerencia o loop de interação com o usuário.
    Recebe dependências prontas (já construídas pelo Composition Root).
    """

    def __init__(self, service: GastoService, view: GastoView) -> None:
        self._svc = service
        self._view = view

        # Mapeamento opção → Command (GoF Command + OCP)
        self._comandos: Dict[str, ICommand] = {
            "1": InserirGastoCommand(service, view),
            "2": ListarGastosCommand(service, view),
            "3": BuscarGastosCommand(service, view),
            "4": AtualizarGastoCommand(service, view),
            "5": DeletarGastoCommand(service, view),
            "6": EstatisticasCommand(service, view),
            "7": LimparTelaCommand(view),
        }

    # ── Loop principal ────────────────────────────────────────────────

    def executar(self) -> None:
        while True:
            self._exibir_menu()
            opcao = self._view.solicitar_input("Escolha uma opção: ")
            if opcao == "8":
                print("\n  👋 Encerrando o sistema...\n")
                break
            comando = self._comandos.get(opcao)
            if comando:
                comando.executar()
            else:
                print("  ❌ Opção inválida!")
            self._view.aguardar_continuar()

    # ── Renderização do menu ──────────────────────────────────────────

    @staticmethod
    def _exibir_menu() -> None:
        print("\n" + "═" * 54)
        print("  💰  GERENCIADOR DE GASTOS  v2.0")
        print("═" * 54)
        print("  1.  📝  Inserir novo gasto")
        print("  2.  📋  Listar todos os gastos")
        print("  3.  🔍  Buscar gastos")
        print("  4.  ✏️   Atualizar gasto")
        print("  5.  🗑️   Deletar gasto")
        print("  6.  📊  Estatísticas")
        print("  7.  🧹  Limpar tela")
        print("  8.  ❌  Sair")
        print("═" * 54)
    