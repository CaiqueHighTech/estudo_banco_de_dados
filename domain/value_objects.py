"""
CAMADA DE DOMÍNIO — Value Objects
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Padrões aplicados:
  GoF   : Value Object (tipo especial de objeto imutável)
  SOLID : SRP — cada VO tem uma única responsabilidade semântica
  GRASP : Information Expert — cada VO valida a si mesmo
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from configs.config import configs

@dataclass(frozen=True)
class Valor:
    """
    Value Object: quantia monetária em BRL.
    Imutável, auto-validante, sem identidade.
    """
    quantia: Decimal

    def __post_init__(self) -> None:
        if not (isinstance(self.quantia, Decimal)):
            # permite criar com float/int para conveniência
            object.__setattr__(self, 'quantia', Decimal(str(self.quantia)))

        if self.quantia <= 0:
            raise ValueError("O valor deve ser maior que zero.")

    @classmethod
    def de(cls, valor: Decimal | int | str) -> Valor:
        try:
            return cls(quantia=Decimal(str(valor)))
        except InvalidOperation:
            raise ValueError(f"Valor monetário inválido: '{valor}'")
    
    def __str__(self) -> str:
        return f"R$ {self.quantia:.2f}"

@dataclass(frozen=True)
class DataGasto:
    """
    Value Object: data em que o gasto ocorreu.
    Imutável e auto-validante.
    """

    data: date

    @classmethod
    def de_string(cls, data_str: str) -> DataGasto:
        try:
            return cls(data=datetime.strptime(data_str, "%Y-%m-%d").date())
        except ValueError:
            raise ValueError(f"Data inválida: '{data_str}'. Use o formato YYYY-MM-DD.")
        
    @classmethod
    def hoje(cls) -> DataGasto:
        return cls(data=date.today())
    
    def __str__(self) -> str:
        return self.data.strftime("%Y-%m-%d")

@dataclass(frozen=True)
class Descricao:

    """
    Value Object: texto descritivo de um gasto.
    Limite e sanitização embutidos.
    """

    texto: str

    def __post_init__(self) -> None:
        texto = self.texto.strip() if self.texto else ""
        object.__setattr__(self, "texto", texto)
        if not texto:
            raise ValueError("Descrição não pode estar vazia.")
        if len(texto) > configs.MAX_LEN:
            raise ValueError(f"Descrição não pode exceder {configs.MAX_LEN} caracteres.")
        
    def __str__(self) -> str:
        return self.texto