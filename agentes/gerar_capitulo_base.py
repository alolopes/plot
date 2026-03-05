from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3:8b-instruct-q4_K_M")

def gerar_capitulo_base(titulo_livro, capitulo, nome_ato):
    prompt = f"""
    Você é um escritor profissional trabalhando na obra: "{titulo_livro}".
    Contexto do Ato: {nome_ato}

    Escreva a versão base (rascunho) do capítulo abaixo:
    Capítulo {capitulo['numero']}: {capitulo['titulo']}
    Objetivo: {capitulo['descricao']}

    Vá direto à história, sem introduções.
    """
    return llm.invoke(prompt)

def normalizar_capitulo(cap):
    """Garante que o dicionário do capítulo tenha todas as chaves necessárias"""
    cap.setdefault('numero', 0)
    cap.setdefault('titulo', 'Sem Título')
    cap.setdefault('descricao', 'Sem Descrição')
    return cap