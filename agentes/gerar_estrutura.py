import json
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field, ValidationError
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import JsonOutputParser


# =====================================================
# 🔹 SCHEMAS
# =====================================================

class Capitulo(BaseModel):
    numero: int = Field(..., ge=1)
    titulo: str = Field(..., min_length=3)
    descricao: str = Field(..., min_length=10)


class Ato(BaseModel):
    nome: str = Field(..., min_length=3)
    descricao: str = Field(..., min_length=10)
    capitulos: List[Capitulo]


class EstruturaLivro(BaseModel):
    atos: List[Ato]

    def validar_minimo(self):
        if len(self.atos) != 4:
            raise ValueError("A estrutura deve conter exatamente 4 atos.")

        for ato in self.atos:
            if len(ato.capitulos) != 4:
                raise ValueError(
                    f"O ato '{ato.nome}' deve conter exatamente 4 capítulos."
                )


# =====================================================
# 🔹 CONFIGURAÇÃO LLM (MODELO RÁPIDO E ESTÁVEL)
# =====================================================

llm = OllamaLLM(
    model="mistral:7b-instruct",
    format="json",
    temperature=0.2  # mais determinístico = menos erro
)

parser = JsonOutputParser()


# =====================================================
# 🔹 CACHE
# =====================================================

def carregar_cache(caminho: Path) -> dict | None:
    if not caminho.exists():
        return None

    try:
        with caminho.open("r", encoding="utf-8") as f:
            dados = json.load(f)

        estrutura = EstruturaLivro.model_validate(dados)
        estrutura.validar_minimo()

        print("📦 Estrutura carregada do cache.")
        return estrutura.model_dump()

    except Exception as e:
        print("⚠ Cache inválido. Será regenerado.", e)
        return None


def salvar_cache(caminho: Path, estrutura: dict):
    with caminho.open("w", encoding="utf-8") as f:
        json.dump(estrutura, f, ensure_ascii=False, indent=4)

    print(f"💾 Estrutura salva em cache: {caminho}")


# =====================================================
# 🔹 FUNÇÃO PRINCIPAL (1 CHAMADA + 1 RETRY)
# =====================================================

def gerar_estrutura(
    titulo: str,
    ideia: str,
    force: bool = False
) -> dict:

    pasta_base = Path("livros") / titulo.replace(" ", "_")
    caminho_cache = pasta_base / "estrutura.json"

    # 🔹 Verifica cache
    if not force:
        estrutura_cache = carregar_cache(caminho_cache)
        if estrutura_cache:
            return estrutura_cache

    print("🧠 Gerando nova estrutura (modo rápido)...")

    prompt = f"""
    Crie a estrutura completa do livro "{titulo}".

    Ideia:
    {ideia}

    Gere EXATAMENTE:
    - 4 atos
    - Cada ato com 4 capítulos numerados de 1 a 4

    Retorne APENAS JSON no formato:

    {{
        "atos": [
            {{
                "nome": "Nome do Ato",
                "descricao": "Função narrativa do ato",
                "capitulos": [
                    {{
                        "numero": 1,
                        "titulo": "Título do Capítulo",
                        "descricao": "Resumo do capítulo"
                    }}
                ]
            }}
        ]
    }}

    Apenas JSON válido.
    """

    for tentativa in range(2):  # no máximo 1 retry
        try:
            resposta = llm.invoke(prompt)
            dados = parser.parse(resposta)

            estrutura_validada = EstruturaLivro.model_validate(dados)
            estrutura_validada.validar_minimo()

            estrutura_final = estrutura_validada.model_dump()

            pasta_base.mkdir(parents=True, exist_ok=True)
            salvar_cache(caminho_cache, estrutura_final)

            return estrutura_final

        except ValidationError as ve:
            print(f"⚠ Tentativa {tentativa+1}: erro de validação.", ve)

        except Exception as e:
            print(f"⚠ Tentativa {tentativa+1} falhou:", e)

    raise ValueError("❌ Falha ao gerar estrutura válida após retry.")