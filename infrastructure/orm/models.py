"""
CAMADA DE INFRAESTRUTURA — Modelos ORM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Segurança:
  • Esta classe é PRIVADA à camada de infraestrutura.
  • Nomes de tabela e colunas ficam AQUI. Nunca chegam ao domínio
    ou à aplicação. As camadas superiores só enxergam DTOs.
  • O prefixo-convenção '_' sinaliza uso interno ao pacote.
 
Padrões aplicados:
  GoF   : Data Mapper — mapeia entre objeto de domínio e tabela
  SOLID : SRP — responsabilidade exclusiva de descrever o schema
"""

from __future__ import annotations
from datetime import date
from decimal import Decimal
from sqlalchemy import Integer, String, Numeric, Date, CheckConstraint
from sqlalchemy import DeclarativeBase, Mapped, mapped_column

class _Base(DeclarativeBase):
    """Base para os modelos ORM — não exposta fora da infraestrutura."""
    pass

class _GastoORM(_Base):
    """
    Modelo ORM interno.
    Prefixo '_' sinaliza: use apenas dentro deste pacote.
    O mapeamento de nomes (colunas ↔ atributos) fica centralizado aqui.
    """

    __tablename__ = "controle_de_gastos"
    __table_args__ = (
        CheckConstraint("gasto" > 0, name="ck_gasto_positivo")
    )

    # Mapeamento explícito: atributo Python ↔ coluna do banco

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    descricao: Mapped[str] = mapped_column("descricao", String(255), nullable=False)
    gasto: Mapped[Decimal] = mapped_column("gasto", Numeric(12, 2), nullable=False)
    data_gasto: Mapped[date] = mapped_column("data_gasto", Date, nullable=False)

    def __repr__(self) -> str:
        return f"<_GastoORM id={self.id}>"