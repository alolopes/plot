import os
from pathlib import Path
from datetime import datetime

def criar_pasta_livro(titulo: str) -> Path:
    """Cria a estrutura de pastas para um livro"""
    # Garante que o nome da pasta não tenha caracteres inválidos
    nome_limpo = "".join([c if c.isalnum() or c in " _-" else "" for c in titulo]).strip()
    base = Path("livros") / nome_limpo.replace(" ", "_")
    
    pasta_memoria = base / "memoria"
    pasta_kindle = pasta_memoria / "kindle_book" / "OEBPS"
    pasta_chapters = pasta_kindle / "chapters"
    
    for p in [base, pasta_memoria, pasta_kindle, pasta_chapters]:
        p.mkdir(parents=True, exist_ok=True)
    return base

def extrair_nome_livro(conteudo: str) -> str:
    """Pega apenas o início da primeira linha como nome do livro"""
    primeira_linha = conteudo.splitlines()[0].strip()
    # Se a primeira linha for muito longa (descrição), pegamos apenas as 2 primeiras palavras
    if len(primeira_linha) > 30:
        palavras = primeira_linha.split()
        return " ".join(palavras[:2])
    return primeira_linha

def hora_atual() -> str:
    return datetime.now().strftime("%H:%M:%S")

def log_inicio(etapa: str):
    print(f"\n🚀 INÍCIO → {etapa} | 🕒 {hora_atual()}")

def log_fim(etapa: str):
    print(f"✅ FIM → {etapa} | 🕒 {hora_atual()}\n")