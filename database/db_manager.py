from sqlalchemy.orm import Session
from database.models import engine, Transacao, Conta, Categoria, Base
from datetime import datetime

Base.metadata.create_all(engine)

def get_session():
    return Session(engine)

def adicionar_transacao(descricao, valor, tipo="despesa", categoria_nome="Outros", data_str=None):
    session = get_session()
    
    valor_final = -abs(float(valor)) if tipo == "despesa" else abs(float(valor))
    
    # Busca ou cria categoria
    categoria = session.query(Categoria).filter(Categoria.nome == categoria_nome).first()
    if not categoria:
        nova_cat = Categoria(nome=categoria_nome, is_despesa=(tipo == "despesa"))
        session.add(nova_cat)
        session.commit()
        categoria = nova_cat
    
    # Trata a data (se vier vazia, usa hoje)
    dt = datetime.now()
    if data_str:
        # Espera formato DD/MM/AAAA vindo da interface
        try:
            dt = datetime.strptime(data_str, "%d/%m/%Y")
        except:
            dt = datetime.now()

    nova_transacao = Transacao(
        descricao=descricao,
        valor=valor_final,
        categoria_id=categoria.id,
        data=dt # Salva a data correta
    )
    
    session.add(nova_transacao)
    session.commit()
    session.close()

def editar_transacao(id_transacao, nova_desc, novo_valor):
    session = get_session()
    t = session.query(Transacao).filter(Transacao.id == id_transacao).first()
    if t:
        t.descricao = nova_desc
        # Mantém o sinal (negativo/positivo) original, atualiza só o montante
        sinal = -1 if t.valor < 0 else 1
        t.valor = abs(float(novo_valor)) * sinal
        session.commit()
    session.close()

def deletar_transacao(id_transacao):
    session = get_session()
    t = session.query(Transacao).filter(Transacao.id == id_transacao).first()
    if t:
        session.delete(t)
        session.commit()
    session.close()

def get_saldo_total():
    session = get_session()
    transacoes = session.query(Transacao).all()
    saldo = sum(t.valor for t in transacoes)
    session.close()
    return saldo

def get_ultimas_transacoes(limit=50):
    session = get_session()
    
    # MUDANÇA 1: Usamos .outerjoin em vez de .join
    # Isso garante que transações sem categoria ou com IDs quebrados apareçam também
    transacoes = session.query(Transacao).outerjoin(Categoria).order_by(Transacao.data.desc(), Transacao.id.desc()).limit(limit).all()
    
    resultado = []
    for t in transacoes:
        # MUDANÇA 2: Verificamos se t.categoria existe antes de tentar pegar o nome
        nome_categoria = t.categoria.nome if t.categoria else "Sem Categoria"
        
        resultado.append({
            "id": t.id,
            "descricao": t.descricao,
            "valor": t.valor,
            "data": t.data.strftime("%d/%m/%Y") if t.data else "Data desc.",
            "categoria": nome_categoria
        })
        
    session.close()
    return resultado