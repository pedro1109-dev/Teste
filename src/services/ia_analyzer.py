"""
ai_analyzer.py — Análise inteligente de faturas via Google Gemini API (GRATUITO).

COMO A IA É UTILIZADA:
───────────────────────────────────────────────────────────────────────
O Google Vision OCR extrai o texto bruto da imagem com coordenadas (x,y).
Porém, faturas de diferentes concessionárias têm layouts completamente
distintos — o que faz os extratores baseados em regex/posição falharem.

Para resolver isso, usamos o Gemini 1.5 Flash (100% gratuito, 1.500 req/dia)
como camada de interpretação semântica:

  1. O texto bruto do OCR é enviado ao Gemini com um prompt especializado.
  2. O Gemini entende o contexto da fatura e devolve JSON estruturado.
  3. O resultado é fundido com o que os extratores regex já encontraram.
     Regex tem prioridade (mais preciso localmente); Gemini preenche lacunas.
───────────────────────────────────────────────────────────────────────
"""

import json
import re
import httpx

def extrair_json_seguro(texto: str):
    try:
        # remove blocos ```json ```
        texto = re.sub(r"```json|```", "", texto).strip()

        # tenta encontrar JSON dentro do texto
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            return json.loads(match.group())

        return {"erro_ia": "Nenhum JSON encontrado", "raw": texto}

    except Exception as e:
        return {"erro_ia": f"Falha ao parsear JSON: {str(e)}", "raw": texto}

GEMINI_MODEL = "gemini-2.5-flash"

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

_SYSTEM = """Você é um assistente especializado em leitura de faturas brasileiras de água e energia elétrica.
Dado o texto bruto extraído via OCR de uma fatura, identifique os campos abaixo.
Retorne APENAS um JSON válido, sem markdown, sem explicações, sem texto adicional.
Se um campo não for encontrado, use null."""

_PROMPT = """Analise este texto de fatura brasileira e extraia os campos:

- total_pagar: valor total a pagar (float em reais, ex: 87.43)
- vencimento: data de vencimento no formato DD/MM/AAAA
- consumo: quantidade consumida (float — m³ para água, kWh para energia)
- unidade: "m³" para água ou "kWh" para energia
- mes_referencia: mês e ano de referência da fatura (ex: "03/2025")
- tipo_fatura: "agua" ou "energia"
- leitura_anterior: leitura anterior do medidor (float ou null)
- leitura_atual: leitura atual do medidor (float ou null)
- concessionaria: nome da empresa (string ou null)

Texto da fatura:
{texto}


NÃO use markdown.
NÃO use ```json```.
NÃO escreva texto fora do JSON"""


async def analisar_fatura_com_gemini(texto_bruto: str, api_key: str) -> dict:
    """
    Envia o texto OCR ao Gemini 2.5 Flash e retorna os campos como dict.
    Gratuito até 1.500 req/dia | 15 req/min — sem cartão de crédito.
    """
    if not api_key:
        return {"erro_ia": "GEMINI_API_KEY não configurada no .env"}

    url = f"{GEMINI_API_URL}?key={api_key}"

    payload = {
        "system_instruction": {
            "parts": [{"text": _SYSTEM}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": _PROMPT.format(texto=texto_bruto[:1500])}],
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1024,
            "responseMimeType": "application/json",
        },
    }

    raw_text = ""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
            resp.raise_for_status()
            data = resp.json()
        print("RESPOSTA COMPLETA GEMINI:", data)

        finish_reason = data.get("candidates", [{}])[0].get("finishReason")

        raw_text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )

        if finish_reason == "MAX_TOKENS":
            return {
                "erro_ia": "Resposta cortada (MAX_TOKENS)",
                "raw": raw_text
                }
        print("RAW TEXT:", raw_text)
        if not raw_text:
            return {"erro_ia": "Gemini retornou resposta vazia"}
        resultado = extrair_json_seguro(raw_text)

        if "erro_ia" not in resultado:
            return resultado

        # Se deu erro, retorna com mais contexto
        return {
            "erro_ia": "Falha ao interpretar resposta da IA",
            "raw": raw_text
        }

    except json.JSONDecodeError:
        return {"erro_ia": "Resposta da IA não é JSON válido", "raw": raw_text}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            return {"erro_ia": "Limite gratuito Gemini atingido — aguarde 1 minuto e tente novamente."}
        return {"erro_ia": f"HTTP {e.response.status_code}: {e.response.text[:300]}"}
    except Exception as e:
        return {"erro_ia": str(e)}


def fundir_resultados(extraido_ocr: dict, extraido_ia: dict) -> dict:
    """
    Funde OCR regex com resultado do Gemini.
    OCR tem prioridade; Gemini preenche os campos que o regex não encontrou.

    Regra especial para tipo_fatura: a unidade detectada pelo OCR
    é a fonte da verdade — nunca deixamos a IA sobrescrever esse campo,
    pois o Gemini ocasionalmente retorna 'm³' para faturas de energia.
    """
    mapa = [
        ("total",            "total_pagar"),
        ("vencimento",       "vencimento"),
        ("consumo",          "consumo"),
        ("unidade",          "unidade"),
        ("mes_referencia",   "mes_referencia"),
        ("leitura_anterior", "leitura_anterior"),
        ("leitura_atual",    "leitura_atual"),
    ]

    resultado = dict(extraido_ocr)

    for campo_ocr, campo_ia in mapa:
        if (resultado.get(campo_ocr) is None or resultado.get(campo_ocr) == ""):
            valor_ia = extraido_ia.get(campo_ia)
            if valor_ia is not None:
                resultado[campo_ocr] = valor_ia

    # tipo_fatura: OCR tem prioridade absoluta (derivado da unidade, que é mais confiável).
    # A IA só preenche se o OCR realmente não detectou a unidade.
    tipo_ocr = resultado.get("tipo_fatura")
    if not tipo_ocr or tipo_ocr == "desconhecido":
        resultado["tipo_fatura"] = extraido_ia.get("tipo_fatura")

    # Campos exclusivos da IA
    resultado["concessionaria"] = extraido_ia.get("concessionaria")

    return resultado