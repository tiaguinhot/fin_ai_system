import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

# Agora aceitamos a lista de categorias existentes como argumento
def classificar_transacao(descricao, valor, categorias_existentes):
    if not api_key:
        return "Geral"

    # Convertemos a lista em string para o prompt
    lista_cats = ", ".join(categorias_existentes)

    prompt = f"""
    Aja como um especialista em organização financeira.
    Tenho um gasto: "{descricao}" no valor de R$ {valor}.
    
    Minhas categorias atuais são: [{lista_cats}].
    
    Sua missão:
    1. Se o gasto se encaixar PERFEITAMENTE em uma categoria atual, responda com o nome dela.
    2. Se NÃO se encaixar bem, SUGIRA UMA NOVA categoria curta (máximo 2 palavras, ex: "Pets", "Viagem", "Jogos").
    
    Responda APENAS o nome da categoria (sem pontuação final).
    """

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = model.generate_content(prompt)
        return response.text.strip().replace("\n", "").replace(".", "")
    except Exception as e:
        print(f"Erro na IA: {e}")
        return "Outros"
    
def gerar_analise_financeira(resumo_texto):
    if not api_key:
        return "Erro: Chave API não configurada."

    prompt = f"""
    Você é um consultor financeiro pessoal experiente, direto e amigável.
    Analise os dados financeiros abaixo do seu cliente:

    {resumo_texto}

    Sua missão é fornecer um relatório curto (máximo 4 parágrafos) usando formatação Markdown (negrito, tópicos).
    Estruture sua resposta assim:
    
    1. **Análise Rápida**: O saldo está positivo? A saúde financeira está boa?
    2. **O Vilão do Orçamento**: Identifique qual categoria está gastando muito e faça um alerta.
    3. **Dica Prática**: Uma sugestão acionável para economizar no próximo mês baseada nesses dados.

    Se não houver dados suficientes, diga para o usuário lançar mais gastos.
    """


    try:
        # Trocamos para o 1.5 Flash que é extremamente rápido e estável
        model = genai.GenerativeModel('gemini-2.5-flash-lite') 
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Desculpe, não consegui analisar agora. Erro: {e}"