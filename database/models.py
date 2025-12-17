from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Conta(Base):
    __tablename__ = 'contas'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    tipo = Column(String)
    saldo_inicial = Column(Float, default=0.0)
    
    # NOVOS CAMPOS PARA CARTÃO DE CRÉDITO
    dia_fechamento = Column(Integer, nullable=True) # Ex: 5
    dia_vencimento = Column(Integer, nullable=True) # Ex: 10
    
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

engine = create_engine('sqlite:///minhas_financas.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)