# ocr.py - Repositório para extração de texto via OCR
# Usa Google Vision para detectar texto em imagens e Gemini para análise inteligente.

"""
ocr.py — Extração de texto via Google Vision + enriquecimento com Gemini (gratuito).
"""

import os
from google.cloud import vision
from src.repositories.extract import extrair_todos_campos  # Função de extração
from src.services.ia_analyzer import analisar_fatura_com_gemini, fundir_resultados  # Análise IA
from src.config.settings import GOOGLE_CREDENTIALS_PATH, GEMINI_API_KEY

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDENTIALS_PATH  # Configura credenciais Google

def extrair_com_posicao(caminho_imagem: str) -> list[dict]:
    # Extrai palavras com posições (x, y) da imagem
    client = vision.ImageAnnotatorClient()

    with open(caminho_imagem, "rb") as f:
        content = f.read()

    image    = vision.Image(content=content)
    response = client.text_detection(image=image)

    if response.error.message:
        raise RuntimeError(f"Google Vision erro: {response.error.message}")

    words = []
    for item in response.text_annotations[1:]:  # Ignora o bloco completo
        vertices = item.bounding_poly.vertices
        words.append({
            "texto": item.description,
            "x":     vertices[0].x,
            "y":     vertices[0].y,
        })

    return words

def _inferir_tipo_por_unidade(unidade: str) -> str:
    # Infere tipo da fatura pela unidade (kWh = energia, m³ = água)
    if unidade and unidade.lower() == "kwh":
        return "energia"
    if unidade and unidade.lower() in ("m³", "m3"):
        return "agua"
    return "desconhecido"


async def extrair_total_avancado(words: list[dict]) -> dict:
    """
    Pipeline de extração em três etapas:
      1. Extratores regex/posição (rápidos, sem custo)
      2. Gemini 1.5 Flash para preencher o que o regex não encontrou
      3. Pós-processamento: garante tipo_fatura consistente com a unidade do OCR

    Retorna dict unificado com todos os campos da fatura.
    """
    # Etapa 1: extratores tradicionais
    dados_ocr = extrair_todos_campos(words)

    # Deriva tipo_fatura a partir da unidade já detectada pelo OCR.
    # Isso serve de âncora: mesmo que a IA retorne tipo errado, corrigimos abaixo.
    tipo_por_unidade = _inferir_tipo_por_unidade(dados_ocr.get("unidade", ""))
    if tipo_por_unidade != "desconhecido":
        dados_ocr["tipo_fatura"] = tipo_por_unidade

    # Etapa 2: Gemini como fallback semântico
    texto_bruto = dados_ocr.get("texto_bruto", "")
    dados_ia = {}
    aviso_ia = None

    if GEMINI_API_KEY and texto_bruto:
        dados_ia = await analisar_fatura_com_gemini(texto_bruto, GEMINI_API_KEY)

    if dados_ia and "erro_ia" in dados_ia:
        aviso_ia = dados_ia["erro_ia"]

    # Etapa 3: fusão — OCR tem prioridade, Gemini preenche lacunas
    if dados_ia and "erro_ia" not in dados_ia:
        resultado = fundir_resultados(dados_ocr, dados_ia)
    else:
        resultado = dados_ocr

    # Pós-processamento: a unidade detectada pelo OCR é fonte da verdade
    # para tipo_fatura. Sobrescreve qualquer valor divergente vindo da IA.
    if tipo_por_unidade != "desconhecido":
        resultado["tipo_fatura"] = tipo_por_unidade

    # Propaga aviso_ia para o resultado final (era perdido antes)
    if aviso_ia:
        resultado["aviso_ia"] = aviso_ia

    return resultado