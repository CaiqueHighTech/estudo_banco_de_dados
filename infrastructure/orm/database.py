"""
CAMADA DE INFRAESTRUTURA — Gerenciador de Sessão
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Padrões aplicados:
  GoF   : Singleton — uma única engine por processo
          Template Method — sessao() garante commit/rollback/close
  SOLID : SRP — gerencia exclusivamente conexões e sessões
  GRASP : Low Coupling — isola o SQLAlchemy do resto da app
"""

from __future__ import annotations
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import _Base

class DatabaseSession:
    """
    Singleton que gerencia a engine e a factory de sessões SQLAlchemy.
    Instanciar múltiplas vezes com o mesmo db_url retorna o mesmo objeto.
    """

    _instance: DatabaseSession | None = None

    def __new__(cls, db_url: str = "sqlite:///estudo.db") -> DatabaseSession:
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._db_url = db_url
            instance._initialized = False
            cls._instance = instance
        return cls._instance

    def __init__(self, db_url: str = "sqlite:///estudo.db") -> None:
        if self._initialized:
            return

        self._engine = create_engine(
            db_url,
            echo=False,
            connect_args={"check_same_thread": False},
        )
        self._factory = sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False, # evita lazy-load após commit
        )
        _Base.metadata.create_all(self._engine)
        self._initialized = True
        print(f"✓ Banco inicializado  [{db_url}]")

    # ── Context Manager (Template Method) ────────────────────────────

    @contextmanager
    def sessao(self) -> Generator[Session, None, None]:
        """
        Abre sessão, comita no sucesso, faz rollback em exceção.
        Uso:
            with db.sessao() as s:
                s.add(model)
        """
        session: Session = self._factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def fechar(self) -> None:
        self._engine.dispose()
        DatabaseSession._instance = None
        print("✓ Conexão encerrada.")

