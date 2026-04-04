"""
CAMADA DE APLICAÇÃO — DTOs (Data Transfer Objects)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Padrões aplicados:
  GoF   : DTO (variação de Value Object para transferência de dados)
  SOLID : ISP — interfaces de entrada e saída separadas
  GRASP : Information Expert, Low Coupling
 
Segurança:
  • Os DTOs de SAÍDA (GastoDTO, EstatisticasDTO) são o que cruza
    fronteiras de camada. O modelo ORM jamais é exposto externamente.
  • Os DTOs de ENTRADA (CriarGastoDTO, AtualizarGastoDTO) carregam
    apenas primitivos — sem referência a tabelas ou colunas.
"""

from __future__ import annotations
from decimal import Decimal
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

# ── Entrada (Commands) ────────────────────────────────────────────────

@dataclass
class CriarGastoDTO:
    """Dados necessários para registrar um novo gasto."""
    valor: Decimal
    descricao: Optional[str] = None
    data_gasto: Optional[str] = None # None → hoje

@dataclass
class AtualizarGastoDTO:
    """Dados para atualização parcial (PATCH semântico)."""
    id: int
    descricao: Optional[str] = None
    valor: Optional[Decimal] = None
    data_gasto: Optional[str] = None

@dataclass
class FiltroBuscaDTO:
    """Critérios de pesquisa avançada."""
    descricao: Optional[str] = None
    valor_minimo: Optional[Decimal] = None
    valor_maximo: Optional[Decimal] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    mes_ano: Optional[str] = None       # formato YYYY-MM

# ── Saída (Query Results) ─────────────────────────────────────────────
 
@dataclass(frozen=True)
class GastoDTO:
    """Representação de leitura de um gasto — imutável e seguro."""
    id: int
    valor: Decimal
    descricao: Optional[str] = None
    data_gasto: Optional[str] = None
 
 
@dataclass(frozen=True)
class EstatisticasDTO:
    """Resumo agregado dos gastos."""
    total_registros: int
    soma_total: Optional[Decimal] = None
    media: Optional[Decimal] = None
    maior_gasto: Optional[Dict[str, Decimal]] = None
    menor_gasto: Optional[Dict[str, Decimal]] = None
    por_mes_ano_dia: List[Dict[str, Any]] = field(default_factory=list)