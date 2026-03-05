from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3:8b-instruct-q4_K_M")

def expandir_capitulo(texto_base, **kwargs):
    prompt = f"""
    Expanda o rascunho abaixo adicionando diálogos, ambientação e profundidade psicológica.
    Contexto: Capítulo {kwargs.get('numero')} - {kwargs.get('titulo')}
    Meta: Aproximadamente {kwargs.get('palavras', 700)} palavras.

    Rascunho:
    {texto_base}
    """
    return llm.invoke(prompt)