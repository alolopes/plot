import sys
import os
import json
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from datetime import datetime

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
    
    # Mostra onde a pasta raiz do livro foi criada
    pasta_raiz = criar_pasta_livro(state["titulo"])
    print(f"📂 Pasta raiz do livro criada em:\n   → {pasta_raiz.resolve()}")
    
    # Mostra a estrutura gerada de forma legível
    print("\nEstrutura gerada (JSON formatado):")
    print(json.dumps(estrutura, indent=2, ensure_ascii=False))
    
    log_fim("Estrutura gerada")
    return {"estrutura": estrutura}

def selecionar_capitulo(state: LivroState):
    ato = state["estrutura"]["atos"][state["ato_index"]]
    cap = normalizar_capitulo(ato["capitulos"][state["cap_index"]])
    return {
        "dados_capitulo": cap,
        "nome_ato": ato.get("nome", "Ato Sem Nome")
    }

def escrever_base(state: LivroState):
    texto = gerar_capitulo_base(
        state["titulo"],
        state["dados_capitulo"],
        state["nome_ato"]
    )
    return {"texto_base": texto}

def expandir(state: LivroState):
    log_inicio(f"Expandindo Capítulo {state['numero_capitulo']}")
    texto_rico = expandir_capitulo(
        state["texto_base"],
        numero=state["numero_capitulo"],
        titulo=state["dados_capitulo"].get("titulo", "Sem título"),
        palavras=700
    )
    print(f"   Texto expandido gerado ({len(texto_rico)} caracteres / ~{len(texto_rico.split())} palavras):")
    print("   " + texto_rico[:180].replace("\n", " ") + "..." if texto_rico else "   [VAZIO OU NULO]")
    return {"texto_expandido": texto_rico, "tentativas": state["tentativas"] + 1}

def validar(state: LivroState):
    if not state.get("texto_expandido"):
        print("   ⚠️  ALERTA: texto_expandido está vazio ou None!")
    palavras = len(state["texto_expandido"].split()) if state["texto_expandido"] else 0
    valido = palavras >= 400
    status = "VÁLIDO → vai salvar" if valido else f"INVÁLIDO ({palavras} palavras) → tenta expandir novamente"
    print(f"   Validação Capítulo {state['numero_capitulo']}: {palavras} palavras | tentativas={state['tentativas']} → {status}")
    return {"valido": valido}

def salvar(state: LivroState):
    print(f"\n💾 Iniciando salvamento do Capítulo {state['numero_capitulo']}...")

    pasta_base = criar_pasta_livro(state["titulo"])
    pasta_chapters = pasta_base / "memoria" / "kindle_book" / "OEBPS" / "chapters"
    pasta_chapters.mkdir(parents=True, exist_ok=True)
    
    print(f"   Pasta de capítulos (onde os arquivos .md serão salvos):\n      → {pasta_chapters.resolve()}")

    numero = f"{state['numero_capitulo']:02d}"
    titulo_cap = state["dados_capitulo"].get("titulo", "Sem_Titulo")
    proibidos = r'<>:"/\\|?*'
    titulo_limpo = "".join("_" if c in proibidos else c for c in titulo_cap.strip())
    titulo_limpo = titulo_limpo.rstrip(" .")

    nome_arquivo = f"Capítulo {numero} - {titulo_limpo}.md"
    caminho_completo = pasta_chapters / nome_arquivo

    conteudo = f"""---
numero: {state['numero_capitulo']}
titulo: {state['dados_capitulo']['titulo']}
ato: {state['nome_ato']}
palavras: {len(state["texto_expandido"].split())}
gerado_em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
---

# {state['dados_capitulo']['titulo']}

**Capítulo {state['numero_capitulo']} – {state['nome_ato']}**

{state["texto_expandido"].strip()}
"""

    with caminho_completo.open("w", encoding="utf-8") as f:
        f.write(conteudo)

    print(f"   ARQUIVO SALVO COM SUCESSO:\n      → {caminho_completo.resolve()}")
    print(f"      (tamanho: {len(conteudo)} caracteres)\n")

    # Próximo capítulo/ato
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

builder.add_conditional_edges(
    "validar",
    lambda x: "salvar" if x["valido"] or x["tentativas"] >= 3 else "expandir"
)

builder.add_conditional_edges(
    "salvar",
    lambda x: END if x["ato_index"] >= len(x["estrutura"]["atos"]) else "selecionar"
)

graph = builder.compile()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python graph.py caminho_do_arquivo_ideia.txt")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        ideia = f.read()

    titulo = extrair_nome_livro(ideia)
    print(f"Iniciando geração do livro: {titulo}")
    print(f"Arquivo de ideia: {os.path.abspath(sys.argv[1])}")
    
    initial_state = {
        "conteudo_ideia": ideia,
        "titulo": titulo,
        "numero_capitulo": 1,
        "ato_index": 0,
        "cap_index": 0,
        "tentativas": 0
    }

    graph.invoke(initial_state)
    print("\nGeração concluída! Verifique os caminhos impressos acima.")