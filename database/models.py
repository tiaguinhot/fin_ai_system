from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import os
import sys

Base = declarative_base()

# --- MODELOS (Estrutura das Tabelas) ---
class Conta(Base):
    __tablename__ = 'contas'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    tipo = Column(String)
    saldo_inicial = Column(Float, default=0.0)
    dia_fechamento = Column(Integer, nullable=True)
    dia_vencimento = Column(Integer, nullable=True)
    transacoes = relationship("Transacao", back_populates="conta")

class Categoria(Base):
    __tablename__ = 'categorias'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    is_despesa = Column(Boolean, default=True)
    transacoes = relationship("Transacao", back_populates="categoria")

class Transacao(Base):
    __tablename__ = 'transacoes'
    id = Column(Integer, primary_key=True)
    descricao = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
    data = Column(DateTime, default=datetime.now)
    conta_id = Column(Integer, ForeignKey('contas.id'))
    conta = relationship("Conta", back_populates="transacoes")
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    categoria = relationship("Categoria", back_populates="transacoes")

# --- LÓGICA DE PERSISTÊNCIA (CRÍTICO PARA .EXE) ---
def get_db_path():
    """
    Retorna o caminho absoluto para o banco de dados.
    Funciona tanto rodando como script Python quanto como executável compilado.
    """
    if getattr(sys, 'frozen', False):
        # Se for executável (PyInstaller), pega a pasta onde o .exe está
        base_path = os.path.dirname(sys.executable)
    else:
        # Se for script, pega a pasta raiz do projeto (sobe 2 níveis de database/models.py)
        # database/models.py -> database/ -> raiz/
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, 'minhas_financas.db')

db_url = f"sqlite:///{get_db_path()}"
engine = create_engine(db_url)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)