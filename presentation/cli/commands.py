"""
CAMADA DE APRESENTAÇÃO — Comandos CLI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Padrões aplicados:
  GoF   : Command — cada operação do menu é um objeto executável
          Factory Method — criar_busca_* produz estratégias corretas
  SOLID : SRP — cada Command encapsula UM caso de uso
          OCP — novo item de menu = nova classe, sem tocar no Controller
          DIP — recebe GastoService e GastoView por injeção
  GRASP : Creator — Commands criam as Strategies de que precisam
 
Segurança:
  • Os Commands manipulam apenas DTOs e primitivos.
  • Exceções de domínio são capturadas e traduzidas em mensagens amigáveis.
  • Nenhum SQL, nenhum modelo ORM chega aqui.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, Dict
from application.dtos import CriarGastoDTO, AtualizarGastoDTO
from application.services.gasto_service import GastoService
from domain.exceptions import GastoNaoEncontradoError, RepositorioError
from ..strategies.busca_strategies import (
    IBuscaStrategy,
    BuscaPorDescricao, BuscaPorValorMinimo,
    BuscaPorValorMaximo, BuscaPorPeriodo, BuscaPorMesAnoDia,
)
from .view import GastoView
from decimal import Decimal

# ── Interface base ────────────────────────────────────────────────────

class ICommand(ABC):
    @abstractmethod
    def executar(self) -> None: ...

# ── Comandos concretos ────────────────────────────────────────────────

class InserirGastoCommand(ICommand):
    def __init__(self, service: GastoService, view: GastoView) -> None:
        self._svc = service
        self._view = view

    def executar(self) -> None:
        self._view.exibir_cabecalho("INSERIR NOVO GASTO")
        try:
            descricao = self._view.solicitar_input("Descrição: ")
            valor_str = self._view.solicitar_input("Valor (R$): ")
            data_str  = self._view.solicitar_input("Data (YYYY-MM-DD) ou Enter para hoje: ")

            dto = CriarGastoDTO(
                descricao=descricao,
                valor=Decimal(str(valor_str)),
                data_gasto=data_str or None,
            )
            gasto = self._svc.registrar_gasto(dto)
            print(f"\n  ✓ Gasto registrado com sucesso! ID: {gasto.id}")
        except ValueError as exc:
            print(f"\n  ❌ Dados inválidos: {exc}")
        except RepositorioError as exc:
            print(f"\n  ❌ Erro ao persistir: {exc}")

class ListarGastosCommand(ICommand):
    def __init__(self, service: GastoService, view: GastoView) -> None:
        self._svc = service
        self._view = view

    def executar(self) -> None:
        self._view.exibir_cabecalho("LISTA DE GASTOS")
        gastos = self._svc.listar_gastos()
        self._view.exibir_lista_gastos(gastos)

class BuscarGastosCommand(ICommand):
    """
    Command + Factory Method:
    O menu de busca constrói a Strategy correta e a injeta no serviço.
    """

    def __init__(self, service: GastoService, view: GastoView) -> None:
        self._svc = service
        self._view = view

        self._factories: Dict[str, Callable[[], IBuscaStrategy]] = {
            "1": self._busca_descricao,
            "2": self._busca_valor_minimo,
            "3": self._busca_valor_maximo,
            "4": self._busca_periodo,
            "5": self._busca_mes_ano_dia,
        }

    def executar(self) -> None:
        self._view.exibir_cabecalho("BUSCAR GASTOS")
        print("  1. Por descrição")
        print("  2. Por valor mínimo")
        print("  3. Por valor máximo")
        print("  4. Por período")
        print("  5. Por mês/ano/dia")

        opcao = self._view.solicitar_input("\nOpção: ")
        factory = self._factories.get(opcao)

        if factory is None:
            print("  ❌ Opção inválida!")
            return
        
        try:
            estrategia = factory()
            gastos = self._svc.buscar_gastos(estrategia)
            self._view.exibir_lista_gastos(gastos)
        except ValueError as exc:
            print(f"  ❌ Entrada inválida: {exc}")
        except RepositorioError as exc:
            print(f"  ❌ Erro na busca: {exc}")

    # Factory Methods privados
    def _busca_descricao(self) -> IBuscaStrategy:
        t = self._view.solicitar_input("Termo da descrição: ")
        return BuscaPorDescricao(t)

    def _busca_valor_minimo(self) -> IBuscaStrategy:
        v = Decimal(self._view.solicitar_input("Valor mínimo (R$): "))
        return BuscaPorValorMinimo(v) 

    def _busca_valor_maximo(self) -> IBuscaStrategy:
        v = Decimal(self._view.solicitar_input("Valor máximo (R$): "))
        return BuscaPorValorMaximo(v)

    def _busca_periodo(self) -> IBuscaStrategy:
        i = self._view.solicitar_input("Data inicial (YYYY-MM-DD): ")
        f = self._view.solicitar_input("Data final   (YYYY-MM-DD): ")
        return BuscaPorPeriodo(i, f)

    def _busca_mes_ano_dia(self) -> IBuscaStrategy:
        m = self._view.solicitar_input("Mês/Ano/Dia (YYYY-MM-DD): ")
        return BuscaPorMesAnoDia(m)
    
class AtualizarGastoCommand(ICommand):
    def __init__(self, service: GastoService, view: GastoView) -> None:
        self._svc = service
        self._view = view
        

        self._atualizadores: Dict[str, Callable[[AtualizarGastoDTO], None]] = {
            "1": self._atualizar_descricao,
            "2": self._atualizar_valor,
            "3": self._atualizar_data,
            "4": self._atualizar_tudo,
        }
    def executar(self) -> None:
        self._view.exibir_cabecalho("ATUALIZAR GASTO")
        try:
            id_gasto = int(self._view.solicitar_input("ID do gasto: "))
            gasto = self._svc.obter_gasto(id_gasto)
            print(f"\n  Gasto atual: {gasto.id} | {gasto.descricao} | R$ {gasto.valor:.2f} | {gasto.data_gasto}")
 
            print("\n  O que atualizar?")
            print("  1. Descrição")
            print("  2. Valor")
            print("  3. Data")
            print("  4. Todos os campos")
 
            opcao = self._view.solicitar_input("\nOpção: ")
            fn    = self._atualizadores.get(opcao)

            if fn is None:
                print("  ❌ Opção inválida!")
                return

            dto = AtualizarGastoDTO(id=id_gasto)
            fn(dto)
            self._svc.modificar_gasto(dto)
            print("  ✓ Gasto atualizado com sucesso!")
 
        except GastoNaoEncontradoError as exc:
            print(f"  ❌ {exc}")
        except ValueError:
            print("  ❌ ID inválido!")
        except RepositorioError as exc:
            print(f"  ❌ Erro ao atualizar: {exc}")
    
    def _atualizar_descricao(self, dto: AtualizarGastoDTO) -> None:
        dto.descricao = self._view.solicitar_input("Nova descrição: ")

    def _atualizar_valor(self, dto: AtualizarGastoDTO) -> None:
        dto.valor = float(self._view.solicitar_input("Novo valor (R$): "))
 
    def _atualizar_data(self, dto: AtualizarGastoDTO) -> None:
        dto.data_gasto = self._view.solicitar_input("Nova data (YYYY-MM-DD): ")

    def _atualizar_tudo(self, dto: AtualizarGastoDTO) -> None:
        self._atualizar_descricao(dto)
        self._atualizar_valor(dto)
        self._atualizar_data(dto)

class DeletarGastoCommand(ICommand):
    def __init__(self, service: GastoService, view: GastoView) -> None:
        self._svc  = service
        self._view = view
 
    def executar(self) -> None:
        self._view.exibir_cabecalho("DELETAR GASTO")
        try:
            id_gasto = int(self._view.solicitar_input("ID do gasto: "))
            gasto    = self._svc.obter_gasto(id_gasto)
            print(f"\n  {gasto.id} | {gasto.descricao} | R$ {gasto.valor:.2f} | {gasto.data_gasto}")

            confirmar = self._view.solicitar_input("Confirmar exclusão? (s/n): ").lower()
            if confirmar == 's':
                self._svc.remover_gasto(id_gasto)
                print("  ✓ Gasto removido com sucesso!")
            else:
                print("  ↩️  Operação cancelada.")

        except GastoNaoEncontradoError as exc:
            print(f"  ❌ {exc}")
        except ValueError:
            print("  ❌ ID inválido!")
        except RepositorioError as exc:
            print(f"  ❌ Erro ao deletar: {exc}")

class EstatisticasCommand(ICommand):
    def __init__(self, service: GastoService, view: GastoView) -> None:
        self._svc  = service
        self._view = view

    def executar(self) -> None:
        self._view.exibir_cabecalho("ESTATÍSTICAS")
        stats = self._svc.obter_estatisticas()
        self._view.exibir_estatisticas(stats)

class LimparTelaCommand(ICommand):
    def __init__(self, view: GastoView) -> None:
        self._view = view

    def executar(self) -> None:
        self._view.limpar_tela()




