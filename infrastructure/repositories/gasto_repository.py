"""
CAMADA DE INFRAESTRUTURA — Repositório SQLAlchemy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Padrões aplicados:
  GoF   : Repository Pattern (implementação concreta)
          Data Mapper — _para_dto() converte ORM → DTO sem vazar o modelo
  SOLID : OCP — nova implementação (ex.: PostgreSQL) sem tocar na interface
          LSP — pode substituir IGastoRepository onde quer que seja usada
          DIP — implementa a abstração da camada de aplicação
  GRASP : Low Coupling — app nunca importa esta classe diretamente
 
Segurança:
  • Único lugar do sistema onde nomes de tabela/coluna existem (nos models).
  • Queries são construídas via ORM (SQLAlchemy) — sem f-string com SQL cru.
  • O método _para_dto() é o único portão de saída: converte modelo → DTO.
"""
 
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import func, extract
from sqlalchemy.exc import SQLAlchemyError
from ...application.interfaces.i_gasto_repository import IGastoRepository
from ...application.dtos import (
    CriarGastoDTO, AtualizarGastoDTO,
    GastoDTO, EstatisticasDTO,
)
from ...domain.exceptions import GastoNaoEncontradoError, RepositorioError
from ..orm.database import DatabaseSession
from ..orm.models import _GastoORM

class GastoRepository(IGastoRepository):
    """
    Repositório concreto: SQLite/PostgreSQL via SQLAlchemy.
    Toda interação com o banco passa por aqui e APENAS por aqui.
    """
    def __init__(self, db: DatabaseSession) -> None:
        self._db = db

    # ── Mapper privado (Data Mapper) ──────────────────────────────────

    @staticmethod
    def _para_dto(m: _GastoORM) -> GastoDTO:
        """Converte modelo ORM → DTO de saída. Nunca expõe _GastoORM."""
        return GastoDTO(
            id=m.id,
            descricao=m.descricao,
            valor=float(m.valor),
            data_gasto=m.data_gasto.strftime("%Y-%m-%d")
        )

    # ── Escrita ───────────────────────────────────────────────────────

    def criar(self, dto: CriarGastoDTO) -> GastoDTO:
        try:
            data = (
                datetime.strptime(dto.data_gasto, "%Y-%m-%d").date()
                if dto.data_gasto else datetime.today().date()
            )
            with self._db.sessao() as s:
                model = _GastoORM(
                    descricao=dto.descricao,
                    valor=Decimal(str(dto.valor)),
                    data_gasto=data
                )
                s.add(model)
                s.flush()
                return self._para_dto(model)
        except SQLAlchemyError as e:
            raise RepositorioError(f"Erro ao criar gasto: {str(e)}") from e

    def atualizar(self, dto: AtualizarGastoDTO) -> GastoDTO:
        try:
            with self._db.sessao() as s:
                model: Optional[_GastoORM] = s.query(_GastoORM).filter(_GastoORM.id == dto.id).first()
                if model is None:
                    raise GastoNaoEncontradoError(dto.id)
                if dto.descricao is not None:
                    model.descricao = dto.descricao
                if dto.valor is not None:
                    model.valor = Decimal(str(dto.valor))
                if dto.data_gasto is not None:
                    model.data_gasto = datetime.strptime(dto.data_gasto, "%Y-%m-%d").date()

                s.flush()
                return self._para_dto(model)
        except GastoNaoEncontradoError:
            raise
        except SQLAlchemyError as e:
            raise RepositorioError(f"Erro ao atualizar gasto: {str(e)}") from e
    
    def deletar(self, id: int) -> None:
        try:
            with self._db.sessao() as s:
                model = s.query(_GastoORM).filter(_GastoORM.id == id).first()
                if model:
                    s.delete(model)
        except SQLAlchemyError as e:
            raise RepositorioError(f"Erro ao deletar gasto: {str(e)}") from e

    # ── Leitura ───────────────────────────────────────────────────────

    def buscar_todos(self) -> List[GastoDTO]:
        try:
            with self._db.sessao() as s:
                rows = s.query(_GastoORM).order_by(_GastoORM.data_gasto.desc()).all()
                return [self._para_dto(r) for r in rows]
        except SQLAlchemyError as e:
            raise RepositorioError(f"Erro ao buscar gastos: {str(e)}") from e
        
    def buscar_por_id(self, id: int) -> Optional[GastoDTO]:
        try:
            with self._db.sessao() as s:
                model = s.query(_GastoORM).filter(_GastoORM.id == id).first()
                return self._para_dto(model) if model else None
        except SQLAlchemyError as e:
            raise RepositorioError(f"Erro ao buscar gasto por ID: {str(e)}") from e
        
    def buscar_por_descricao(self, termo: str) -> List[GastoDTO]:
        try:
            with self._db.sessao() as s:
                rows = (
                    s.query(_GastoORM)
                    .filter(_GastoORM.descricao.ilike(f"%{termo}%")
                    .order_by(_GastoORM.data_gasto.desc())
                    .all()
                )
                return [self._para_dto(r) for r in rows]
        except SQLAlchemyError as e:
            raise RepositorioError(f"Erro ao buscar gastos por descrição: {str(e)} from e

    def buscar_por_valor_minimo(self, valor_min: Decimal) -> List[GastoDTO]:
        try:
            with self._db.sessao() as s:
                rows = (
                    s.query(_GastoORM)
                    .filter(_GastoORM.valor >= valor_min)
                    .order_by(_GastoORM.data_gasto.desc())
                    .all()
                )
                return [self._para_dto(r) for r in rows]
        except SQLAlchemyError as e:
            raise RepositorioError(f"Erro ao buscar gastos por valor mínimo: {str(e)}") from e

    def buscar_por_valor_maximo(self, valor_max: float) -> List[GastoDTO]:
        try:
            with self._db.sessao() as s:
                rows = (
                    s.query(_GastoORM)
                    .filter(_GastoORM.valor <= valor_max)
                    .order_by(_GastoORM.data_gasto.desc())
                    .all()
                )
                return [self._para_dto(r) for r in rows]
        except SQLAlchemyError as e:
            raise RepositorioError(f"Falha na busca por valor máximo: {str(e)}") from e

    def buscar_por_periodo(self, inicio: str, fim: str) -> List[GastoDTO]:
        try:
            d_inicio = datetime.strptime(inicio, "%Y-%m-%d").date()
            d_fim = datetime.strptime(fim, "%Y-%m-%d").date()
            with self._db.sessao() as s:
                rows = (
                    s.query(_GastoORM)
                    .filter(_GastoORM.data_gasto.between(d_inicio, d_fim))
                    .order_by(_GastoORM.data_gasto.desc())
                    .all()
                )
                return [self._para_dto(r) for r in rows]
        except SQLAlchemyError as e:
            raise RepositorioError(f"Erro ao buscar gastos por período: {str(e)}") from e

    def buscar_por_mes_ano(self, mes_ano: str) -> List[GastoDTO]:
        try:
            ano, mes = map(int, mes_ano.split("-"))
            with self._db.sessao() as s:
                rows = (
                    s.query(_GastoORM)
                    .filter(
                        extract("year", _GastoORM.data_gasto) == ano,
                        extract("month", _GastoORM.data_gasto) == mes
                    )
                    .order_by(_GastoORM.data_gasto.desc())
                    .all()
                )
                return [self._para_dto(r) for r in rows]
        except SQLAlchemyError as e:
            raise RepositorioError(f"Erro ao buscar gastos por mês/ano: {str(e)}") from e

    # ── Agregação ─────────────────────────────────────────────────────

    def obter_estatisticas(self) -> EstatisticasDTO:
        try:
            with self._db.sessao() as s:
            total: int = s.query(func.count(_GastoORM.id)).scalar() or 0

            if total:
                return EstatisticasDTO(
                    total_registros=0,
                    soma_total=0.0,
                    media=0,
                    maior_gasto={},
                    menor_gasto={},
                    por_mes=[],
                )
            soma = Decimal(s.query(func.sum(_GastoORM.valor)).scalar() or 0)
            media = Decimal(s.query(func.avg(_GastoORM.valor)).scalar() or 0)
            maior = s.query(_GastoORM).order_by(_GastoORM.valor.desc()).first()
            menor = s.query(_GastoORM).order_by(_GastoORM.valor.asc()).first()

            # Agrupamento por mês via SQLAlchemy (sem SQL cru)
            por_mes_q = (
                s.query(
                    func.strftime("%Y-%m", _GastoORM.data_gasto).label("mes_ano"),
                    func.count(_GastoORM.id).label("quantidade"),
                    func.sum(_GastoORM.valor).label("total"),
                )
                .group_by("mes")
                .order_by(func.strftime("%Y-%m", _GastoORM.data_gasto).desc())
                .all()
            )

            return EstatisticasDTO(
                total_registros=total,
                soma_total=soma,
                media=media,
                maior_gasto={"valor": Decimal(maior.valor), "descricao": maior.descricao} if maior else {},
                menor_gasto={"valor": Decimal(menor.valor), "descricao": menor.descricao} if menor else {},
                por_mes=[
                    {"mes": r.mes, "quantidade": r.quantidade, "total": Decimal(r.total) for r in por_mes_q}
                ],
            )
        except SQLAlchemyError as e:
            raise RepositorioError(f"Erro ao obter estatísticas: {str(e)}") from e
    
    


