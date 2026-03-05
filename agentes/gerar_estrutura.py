import json
from langchain_ollama import OllamaLLM # Garantindo que está usando o novo pacote
from langchain_core.output_parsers import JsonOutputParser

llm = OllamaLLM(model="llama3:8b-instruct-q4_K_M", format="json")

def gerar_estrutura(titulo, ideia): # Adicionado o parâmetro 'titulo'
    prompt = f"""
    Você é um arquiteto literário. Crie a estrutura do livro "{titulo}".
    Ideia central: {ideia}

    Retorne APENAS um JSON no formato:
    {{
        "atos": [
            {{
                "nome": "Ato 1",
                "capitulos": [
                    {{ "numero": 1, "titulo": "Título", "descricao": "Resumo" }}
                ]
            }}
        ]
    }}
    """
    resposta = llm.invoke(prompt)
    try:
        parser = JsonOutputParser()
        return parser.parse(resposta)
    except Exception as e:
        print(f"Erro ao converter JSON: {e}")
        return {"atos": []}