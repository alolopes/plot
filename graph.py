import sys
import os
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END

from agentes.gerar_estrutura import gerar_estrutura
from agentes.gerar_capitulo_base import gerar_capitulo_base, normalizar_capitulo
from agentes.expandir_capitulo import expandir_capitulo
from utils import criar_pasta_livro, extrair_nome_livro, log_inicio, log_fim

class LivroState(TypedDict):
    conteudo_ideia: str
    titulo: str
    numero_capitulo: int
    ato_index: int
    cap_index: int
    tentativas: int
    valido: bool
    dados_capitulo: Dict[str, Any]
    nome_ato: str
    texto_base: str
    texto_expandido: str
    estrutura: Dict[str, Any]

def etapa_estrutura(state: LivroState):
    log_inicio("Gerando estrutura do Livro")
    estrutura = gerar_estrutura(state["titulo"], state["conteudo_ideia"])
    log_fim("Estrutura gerada")
    return {"estrutura": estrutura}

def selecionar_capitulo(state: LivroState):
    ato = state["estrutura"]["atos"][state["ato_index"]]
    cap = normalizar_capitulo(ato["capitulos"][state["cap_index"]])
    return {"dados_capitulo": cap, "nome_ato": ato.get("nome", "Ato Sem Nome")}

def escrever_base(state: LivroState):
    # Passando os 3 argumentos necessários: título, dados do cap e nome do ato
    texto = gerar_capitulo_base(state["titulo"], state["dados_capitulo"], state["nome_ato"])
    return {"texto_base": texto}

def expandir(state: LivroState):
    log_inicio(f"Expandindo Capítulo {state['numero_capitulo']}")
    texto_rico = expandir_capitulo(state["texto_base"])
    return {"texto_expandido": texto_rico, "tentativas": state["tentativas"] + 1}

def validar(state: LivroState):
    # Validação simples por contagem de palavras
    palavras = len(state["texto_expandido"].split())
    valido = palavras >= 400 
    return {"valido": valido}

def salvar(state: LivroState):
    # Lógica de incremento e salvamento
    print(f"💾 Salvando Capítulo {state['numero_capitulo']}...")
    
    proximo_cap = state["cap_index"] + 1
    proximo_ato = state["ato_index"]
    
    ato_atual = state["estrutura"]["atos"][state["ato_index"]]
    if proximo_cap >= len(ato_atual["capitulos"]):
        proximo_ato += 1
        proximo_cap = 0
        
    return {
        "numero_capitulo": state["numero_capitulo"] + 1,
        "cap_index": proximo_cap,
        "ato_index": proximo_ato,
        "tentativas": 0
    }

# Configuração do Grafo
builder = StateGraph(LivroState)
builder.add_node("estrutura", etapa_estrutura)
builder.add_node("selecionar", selecionar_capitulo)
builder.add_node("escrever", escrever_base)
builder.add_node("expandir", expandir)
builder.add_node("validar", validar)
builder.add_node("salvar", salvar)

builder.set_entry_point("estrutura")
builder.add_edge("estrutura", "selecionar")
builder.add_edge("selecionar", "escrever")
builder.add_edge("escrever", "expandir")
builder.add_edge("expandir", "validar")

builder.add_conditional_edges("validar", lambda x: "salvar" if x["valido"] or x["tentativas"] >= 3 else "expandir")
builder.add_conditional_edges("salvar", lambda x: END if x["ato_index"] >= len(x["estrutura"]["atos"]) else "selecionar")

graph = builder.compile()

if __name__ == "__main__":
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        ideia = f.read()
    
    # Extrai o título curto (ex: "A Velatura")
    titulo = extrair_nome_livro(ideia)
    criar_pasta_livro(titulo)
    
    graph.invoke({
        "conteudo_ideia": ideia, 
        "titulo": titulo,
        "numero_capitulo": 1, 
        "ato_index": 0, 
        "cap_index": 0, 
        "tentativas": 0
    })