"""
CAMADA DE APRESENTAÇÃO — View CLI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Padrões aplicados:
  GoF   : Template Method — exibir_cabecalho como template de layout
  SOLID : SRP — responsabilidade única: renderizar dados para o terminal
  GRASP : Low Coupling — recebe apenas DTOs, nunca entidades ou modelos ORM
"""

import os
from __future__ import annotations
from typing import List
from ...application.dtos import GastoDTO, EstatisticasDTO

class GastoView:
    """Responsável exclusivamente pela apresentação no terminal."""
 
    # ── Layout ────────────────────────────────────────────────────────

    @staticmethod
    def limpar_tela() -> None:
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def exibir_cabecalho(titulo: str) -> None:
        largura = 54
        print(f"\n{'═' * largura}")
        print(f"  {titulo}")
        print(f"{'═' * largura}")

    @staticmethod
    def aguardar_continuar() -> None:
        input("\n  Pressione Enter para continuar...")

    # ── Listas ────────────────────────────────────────────────────────

    @staticmethod
    def exibir_lista_gastos(gastos: List[GastoDTO]) -> None:
        if not gastos:
            print("\n  📭 Nenhum gasto encontrado.")
            return
        print(f"\n  {'ID':<6} {'Descrição':<32} {'Valor':>12}  {'Data'}")
        print(f"  {'─' * 62}")

        total = 0.0
        for g in gastos:
            desc = g.descricao[:30] + ".." if  len(g.descricao) > 30 else g.descricao
            print(f"  {g.id:<6} {desc:<32} R${g.valor:>9.2f}  {g.data_gasto}")
            total += g.valor
        
        print(f"  {'─' * 62}")
        print(f"  {'TOTAL':<38} R${total:>9.2f}\n")

    # ── Estatísticas ─────────────────────────────────────────────────

    @staticmethod
    def exibir_estatisticas(stats: EstatisticasDTO) -> None:
        if stats.total_registros == 0:
            print("\n  📭 Nenhum dado para estatísticas.")
            return

        print(f"\n  📊 Total de registros : {stats.total_registros}")
        print(f"  💰 Soma total         : R$ {stats.soma_total:.2f}")
        print(f"  📈 Média              : R$ {stats.media:.2f}")

        if stats.maior_gasto:
             print(f"  ⬆️  Maior gasto        : R$ {stats.maior_gasto['valor']:.2f}"
                  f"  ({stats.maior_gasto['descricao']})")
        if stats.menor_gasto:
            print(f"  ⬇️  Menor gasto        : R$ {stats.menor_gasto['valor']:.2f}"
                  f"  ({stats.menor_gasto['descricao']})")
        
        if stats.por_mes:
            print(f"\n  {'Mês':<10} {'Qtd':>6}  {'Total':>12}")
            print(f"  {'─' * 34}")
            for r in stats.por_mes:
                print(f"  {r['mes']:<10} {r['quantidade']:>6}  R${r['total']:>9.2f}")

    # ── Input ─────────────────────────────────────────────────────────

    @staticmethod
    def solicitar_input(mensagem: str) -> str:
        return input(f"  {mensagem}").strip() 