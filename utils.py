import os
from pathlib import Path
from datetime import datetime

def criar_pasta_livro(titulo: str) -> Path:
    """Cria a estrutura de pastas para um livro"""
    nome_limpo = "".join([c if c.isalnum() or c in " _-" else "" for c in titulo]).strip()
    base = Path("livros") / nome_limpo.replace(" ", "_")
    
    pasta_memoria = base / "memoria"
    pasta_kindle = pasta_memoria / "kindle_book" / "OEBPS"
    pasta_chapters = pasta_kindle / "chapters"
    
    for p in [base, pasta_memoria, pasta_kindle, pasta_chapters]:
        p.mkdir(parents=True, exist_ok=True)
    
    print(f"Estrutura de pastas criada em: {base.resolve()}")
    return base

def extrair_nome_livro(conteudo: str) -> str:
    """Pega apenas o início da primeira linha como nome do livro"""
    linhas = conteudo.splitlines()
    if not linhas:
        return "Livro_Sem_Nome"
    primeira_linha = linhas[0].strip()
    if len(primeira_linha) > 30:
        palavras = primeira_linha.split()
        return " ".join(palavras[:3])  # aumentei para 3 palavras
    return primeira_linha or "Livro_Sem_Nome"

def hora_atual() -> str:
    return datetime.now().strftime("%H:%M:%S")

def log_inicio(etapa: str):
    print(f"\n🚀 INÍCIO → {etapa} | 🕒 {hora_atual()}")

def log_fim(etapa: str):
    print(f"✅ FIM → {etapa} | 🕒 {hora_atual()}\n")