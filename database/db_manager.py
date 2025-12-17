import calendar
from sqlalchemy.orm import Session
from database.models import engine, Transacao, Conta, Categoria, Base
from datetime import datetime

Base.metadata.create_all(engine)

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime(year, month, day)

def get_session():
    return Session(engine)

def adicionar_transacao(descricao, valor, tipo="despesa", categoria_nome="Outros", conta_nome=None, data_str=None, num_parcelas=1):
    session = get_session()
    
    # 1. Busca Conta e Categoria
    categoria = session.query(Categoria).filter(Categoria.nome == categoria_nome).first()
    if not categoria:
        nova_cat = Categoria(nome=categoria_nome, is_despesa=(tipo == "despesa"))
        session.add(nova_cat)
        session.commit()
        categoria = nova_cat
    
    conta = None
    if conta_nome:
        conta = session.query(Conta).filter(Conta.nome == conta_nome).first()

    # 2. Prepara a Data Base
    dt_base = datetime.now()
    if data_str:
        try:
            dt_base = datetime.strptime(data_str, "%d/%m/%Y")
        except:
            pass

    # 3. Lógica do Cartão de Crédito (Fechamento)
    # Se comprou DEPOIS que fechou, a 1ª parcela só cai no mês seguinte
    meses_offset = 0
    if conta and conta.tipo == "Crédito" and conta.dia_fechamento:
        if dt_base.day >= conta.dia_fechamento:
            meses_offset = 1 # Pula 1 mês para começar

    # 4. Cálculo do Valor da Parcela
    valor_float = float(valor)
    valor_parcela = valor_float / int(num_parcelas)
    # Define sinal
    valor_final = -abs(valor_parcela) if tipo == "despesa" else abs(valor_parcela)

    # 5. Loop para criar as N transações
    for i in range(int(num_parcelas)):
        # Calcula a data desta parcela específica
        data_parcela = add_months(dt_base, i + meses_offset)
        
        # Se for parcelado, adiciona (1/10), (2/10) na descrição
        desc_final = descricao
        if int(num_parcelas) > 1:
            desc_final = f"{descricao} ({i+1}/{num_parcelas})"

        nova_transacao = Transacao(
            descricao=desc_final,
            valor=valor_final,
            categoria_id=categoria.id,
            conta_id=conta.id if conta else None,
            data=data_parcela
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
    
    # 1. Soma todo o histórico de transações (Receitas - Despesas)
    transacoes = session.query(Transacao).all()
    total_transacoes = sum(t.valor for t in transacoes)
    
    # 2. Soma o saldo inicial de todas as contas cadastradas
    contas = session.query(Conta).all()
    total_inicial = sum(c.saldo_inicial for c in contas)
    
    session.close()
    
    # O saldo real é a soma dos dois
    return total_transacoes + total_inicial

def get_ultimas_transacoes(limit=50):
    session = get_session()
    
    # Agora fazemos outerjoin com Categoria E com Conta
    transacoes = session.query(Transacao)\
        .outerjoin(Categoria)\
        .outerjoin(Conta)\
        .order_by(Transacao.data.desc(), Transacao.id.desc())\
        .limit(limit).all()
    
    resultado = []
    for t in transacoes:
        nome_categoria = t.categoria.nome if t.categoria else "Sem Categoria"
        # Verificamos se tem conta vinculada
        nome_conta = t.conta.nome if t.conta else "---"
        
        resultado.append({
            "id": t.id,
            "descricao": t.descricao,
            "valor": t.valor,
            "data": t.data.strftime("%d/%m/%Y") if t.data else "Data desc.",
            "categoria": nome_categoria,
            "conta": nome_conta # Adicionamos esse campo novo
        })
        
    session.close()
    return resultado


# --- GERENCIAMENTO DE CONTAS ---

def adicionar_conta(nome, tipo, saldo_inicial=0.0, dia_fechamento=None, dia_vencimento=None):
    session = get_session()

    saldo_float = float(saldo_inicial) if saldo_inicial else 0.0

    # Se não for crédito, garantimos que os dias sejam None
    if tipo != "crédito":
        dia_fechamento = None
        dia_vencimento = None
    else:
        # Garante que são inteiros se forem fornecidos
        dia_fechamento = int(dia_fechamento) if dia_fechamento else None
        dia_vencimento = int(dia_vencimento) if dia_vencimento else None

    nova_conta = Conta(
        nome=nome, 
        tipo=tipo, 
        saldo_inicial=saldo_float,
        dia_fechamento=dia_fechamento,
        dia_vencimento=dia_vencimento
    )
    session.add(nova_conta)
    session.commit()
    session.close()

def get_contas():
    session = get_session()
    contas = session.query(Conta).all()
    resultado = []
    for c in contas:
        resultado.append({
            "id": c.id,
            "nome": c.nome,
            "tipo": c.tipo,
            "saldo_inicial": c.saldo_inicial,
            # Retorna também os dias
            "dia_fechamento": c.dia_fechamento,
            "dia_vencimento": c.dia_vencimento
        })
    session.close()
    return resultado


def deletar_conta(id_conta):
    session = get_session()
    c = session.query(Conta).filter(Conta.id == id_conta).first()
    if c:
        session.delete(c)
        session.commit()
    session.close()

def get_todas_categorias():
    session = get_session()
    # Pega apenas os nomes das categorias
    categorias = session.query(Categoria.nome).all()
    session.close()
    # Retorna uma lista limpa: ['Alimentação', 'Transporte', ...]
    return [c[0] for c in categorias]

def get_resumo_financeiro():
    """
    Gera um texto resumido para a IA ler.
    Ex: "Gastos: Alimentação: R$ 500, Transporte: R$ 200..."
    """
    session = get_session()
    
    # 1. Totais Gerais
    transacoes = session.query(Transacao).all()
    total_receitas = sum(t.valor for t in transacoes if t.valor > 0)
    total_despesas = sum(t.valor for t in transacoes if t.valor < 0)
    
    # 2. Gastos por Categoria (Agrupamento via Python simples)
    gastos_por_cat = {}
    for t in transacoes:
        if t.valor < 0: # Só analisa despesas
            cat_nome = t.categoria.nome if t.categoria else "Sem Categoria"
            if cat_nome not in gastos_por_cat:
                gastos_por_cat[cat_nome] = 0
            gastos_por_cat[cat_nome] += abs(t.valor)
    
    session.close()

    # Formata o texto para a IA
    texto = f"Resumo Financeiro Atual:\n"
    texto += f"- Total Receitas: R$ {total_receitas:.2f}\n"
    texto += f"- Total Despesas: R$ {abs(total_despesas):.2f}\n"
    texto += f"- Saldo Líquido: R$ {(total_receitas + total_despesas):.2f}\n\n"
    texto += "Despesas por Categoria:\n"
    
    for cat, valor in gastos_por_cat.items():
        texto += f"- {cat}: R$ {valor:.2f}\n"
        
    return texto

def get_gastos_por_categoria():
    session = get_session()
    transacoes = session.query(Transacao).filter(Transacao.valor < 0).all() # Só despesas
    
    dados = {}
    for t in transacoes:
        cat_nome = t.categoria.nome if t.categoria else "Outros"
        if cat_nome not in dados:
            dados[cat_nome] = 0.0
        dados[cat_nome] += abs(t.valor)
        
    session.close()
    return dados