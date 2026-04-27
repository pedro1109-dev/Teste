"""
extract.py — Extratores de campos de faturas (água e energia).
Corrigido + expandido com extratores adicionais para análise mensal.
"""

from src.repositories.utils import normalizar_valor, eh_valor, encontrar_label
import re


    # ─────────────────────────────────────────────
    # HELPERS INTERNOS
    # ─────────────────────────────────────────────

def _texto_completo(words: list[dict]) -> str:
    return " ".join(w.get("texto", "") for w in words)


def _candidatos_proximos(words, ref, tolerancia_y=50, apenas_direita=True):
    """Retorna words na mesma linha (±tolerancia_y) de ref, opcionalmente só à direita."""
    resultado = []
    for w in words:
        if "x" not in w or "y" not in w:
            continue
        dy = abs(w["y"] - ref["y"])
        if dy > tolerancia_y:
            continue
        if apenas_direita and w["x"] <= ref["x"]:
            continue
        resultado.append(w)
    return resultado


# ─────────────────────────────────────────────
# EXTRATORES PRINCIPAIS
# ─────────────────────────────────────────────

def extrair_total_pagar(words: list[dict]):
    texto = _texto_completo(words)

    # Tentativa 1: regex direta no texto completo
    # Cobre variações reais do OCR:
    #   "R $ 69,01"  → OCR separa R$ em dois tokens
    #   "R$69,01"    → colado
    #   "69,01"      → sem símbolo
    #   Quando há dois valores na linha (ex: "67,26 69,01"), pega o ÚLTIMO
    #   pois faturas de energia costumam ter subtotal + total na mesma linha
    padroes = [
        r'TOTAL\s+A\s+PAGAR[\s\S]{0,30}?(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*$',
        r'VALOR\s+A\s+PAGAR[\s\S]{0,30}?(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*$',
        r'TOTAL\s+DA\s+FATURA[\s\S]{0,30}?(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*$',
        r'VALOR\s+TOTAL[\s\S]{0,30}?(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*$',
    ]
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE | re.MULTILINE)
        if match:
            try:
                return normalizar_valor(match.group(1))
            except Exception:
                pass

    # Tentativa 2: captura TODOS os valores após o label e pega o último
    # Motivo: "TOTAL A PAGAR R $ 67,26 69,01" → o último (69,01) é o total real
    padroes_todos = [
        r'TOTAL\s+A\s+PAGAR([\s\S]{0,60})',
        r'VALOR\s+A\s+PAGAR([\s\S]{0,60})',
        r'TOTAL\s+DA\s+FATURA([\s\S]{0,60})',
        r'VALOR\s+TOTAL([\s\S]{0,60})',
    ]
    for padrao in padroes_todos:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            trecho = match.group(1)
            # Extrai todos os valores numéricos do trecho
            valores = re.findall(r'\d{1,3}(?:[.,]\d{3})*[.,]\d{2}', trecho)
            if valores:
                try:
                    # Pega o último valor encontrado (é o total final)
                    return normalizar_valor(valores[-1])
                except Exception:
                    pass

    # Tentativa 3: por posição espacial (fallback quando regex falha)
    for termos in [["TOTAL", "A", "PAGAR"], ["TOTAL", "PAGAR"], ["VALOR", "PAGAR"], ["TOTAL", "FATURA"]]:
        ref = encontrar_label(words, termos)
        if not ref:
            continue

        candidatos = _candidatos_proximos(words, ref, tolerancia_y=45)
        candidatos = [w for w in candidatos if eh_valor(w["texto"])]
        if candidatos:
            # Ordena por posição X e pega o mais à direita (último da linha = total)
            candidatos.sort(key=lambda w: w["x"])
            return normalizar_valor(candidatos[-1]["texto"])

    return None


def extrair_vencimento(words: list[dict]):
    texto = _texto_completo(words)

    # Tentativa 1: regex
    match = re.search(
        r'VENCIMENTO[:\s]*(\d{2}[/\-]\d{2}[/\-]\d{2,4})',
        texto, re.IGNORECASE
    )
    if match:
        return match.group(1)

    # Tentativa 2: posição — procura palavra VENCIMENTO e pega data próxima
    for i, w in enumerate(words):
        if "VENCIMENTO" in w["texto"].upper():
            for j in range(i + 1, min(i + 8, len(words))):
                val = words[j]["texto"]
                if re.match(r'\d{2}[/\-]\d{2}[/\-]\d{2,4}', val):
                    return val

    return None


def extrair_consumo(words: list[dict]):
    texto = _texto_completo(words)

    # Tentativa 1: regex — captura número seguido de m³ ou kWh
    match = re.search(
        r'CONSUMO[^0-9]*(\d+[\.,]?\d*)\s*(m[³3]|kWh|KWH|kwh)?',
        texto, re.IGNORECASE
    )
    if match:
        try:
            return normalizar_valor(match.group(1))
        except Exception:
            pass

    # Tentativa 2: posição espacial
    for termo in [["CONSUMO"], ["Consumo"], ["CONSUMO", "MEDIDO"]]:
        ref = encontrar_label(words, termo)
        if not ref:
            continue

        candidatos = []
        for w in words:
            if "x" not in w or "y" not in w:
                continue
            # Busca abaixo ou na mesma linha com tolerância ampliada
            dy = w["y"] - ref["y"]
            dx = abs(w["x"] - ref["x"])
            if 0 <= dy < 100 and dx < 120:
                if eh_valor(w["texto"]):
                    candidatos.append(w)

        if candidatos:
            candidatos.sort(key=lambda w: w["x"], reverse=True)
            return normalizar_valor(candidatos[0]["texto"])

    return None


def extrair_unidade_consumo(words: list[dict]) -> str:
    """
    Detecta unidade olhando ao redor do valor de consumo,
    não no documento inteiro.
    """
    texto = _texto_completo(words)

    # 1. Tenta pegar junto do consumo (mais confiável)
    match = re.search(
        r'CONSUMO[^0-9]*(\d+[\.,]?\d*)\s*(kwh|KWH|kWh|m[³3])',
        texto,
        re.IGNORECASE
    )
    if match:
        unidade = match.group(2).lower()
        if "kwh" in unidade:
            return "kWh"
        return "m³"

    # 2. fallback: procurar "kWh" explícito
    if "KWH" in texto.upper():
        return "kWh"

    # 3. fallback: água
    if "M³" in texto.upper() or "M3" in texto.upper():
        return "m³"

    return "desconhecido"


def extrair_mes_referencia(words: list[dict]):
    """Extrai o mês/ano de referência da fatura."""
    texto = _texto_completo(words)

    # Ex: "Referência: 03/2025" ou "MÊS DE REFERÊNCIA: MARÇO/2025"
    match = re.search(
        r'REFER[EÊ]NCIA[:\s]*([A-ZÇÃÁa-záãçé]+[/\s]?\d{4}|\d{2}/\d{4})',
        texto, re.IGNORECASE
    )
    if match:
        return match.group(1).strip()

    # Fallback: procura padrão MM/AAAA
    match = re.search(r'\b(0[1-9]|1[0-2])/(\d{4})\b', texto)
    if match:
        return match.group(0)

    return None


def extrair_leitura_anterior(words: list[dict]):
    """Extrai leitura anterior (útil para calcular consumo real)."""
    texto = _texto_completo(words)
    match = re.search(
        r'LEITURA\s+ANTERIOR[:\s]*(\d+)',
        texto, re.IGNORECASE
    )
    if match:
        try:
            return float(match.group(1))
        except Exception:
            pass
    return None


def extrair_leitura_atual(words: list[dict]):
    """Extrai leitura atual."""
    texto = _texto_completo(words)
    match = re.search(
        r'LEITURA\s+ATUAL[:\s]*(\d+)',
        texto, re.IGNORECASE
    )
    if match:
        try:
            return float(match.group(1))
        except Exception:
            pass
    return None


def extrair_todos_campos(words: list[dict]) -> dict:
    """Extrai todos os campos disponíveis de uma fatura."""
    return {
        "total": extrair_total_pagar(words),
        "vencimento": extrair_vencimento(words),
        "consumo": extrair_consumo(words),
        "unidade": extrair_unidade_consumo(words),
        "mes_referencia": extrair_mes_referencia(words),
        "leitura_anterior": extrair_leitura_anterior(words),
        "leitura_atual": extrair_leitura_atual(words),
        "texto_bruto": _texto_completo(words),
    }