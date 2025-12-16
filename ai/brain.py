import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

def classificar_transacao(descricao, valor):
    if not api_key:
        return "Geral"

    categorias_possiveis = "Alimentação, Transporte, Moradia, Lazer, Saúde, Educação, Investimento, Assinaturas, Outros"

    prompt = f"""
    Aja como um assistente financeiro. Tenho um gasto: "{descricao}" valor R$ {valor}.
    Categorias: [{categorias_possiveis}].
    Responda APENAS o nome da categoria.
    """

    try:
        # Atualizado para o modelo que sua conta detectou
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip().replace("\n", "").replace(".", "")
    except Exception as e:
        print(f"Erro na IA: {e}")
        return "Outros"