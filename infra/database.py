import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from core.config import settings


# Base única do projeto: todos os models devem herdar desta classe
class Base(DeclarativeBase):
    pass

# Criando uma conexão com o banco
engine = sa.create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True   # evita conexões “mortas” no pool
)

# Session factory (cada request/uso abre a sua)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Dependency/auxiliar para obter e fechar sessão (útil nas rotas, serviços, etc.)
def gera_sessao():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
