"""
utils.py — Utilitários de parsing e normalização de valores OCR.
"""

import re


def encontrar_label(words: list[dict], termos: list[str]) -> dict | None:
    """
    Localiza sequência de termos nos words e retorna a posição do primeiro.
    Comparação case-insensitive.
    """
    termos_upper = [t.upper() for t in termos]

    for i in range(len(words) - len(termos_upper) + 1):
        grupo = words[i: i + len(termos_upper)]
        textos = [w.get("texto", "").upper() for w in grupo]
        if textos == termos_upper:
            return grupo[0]

    return None


def eh_valor(texto: str) -> bool:
    """Retorna True se o texto puder ser interpretado como valor numérico."""
    if not texto:
        return False

    texto = texto.strip()
    texto = texto.replace("R$", "").replace("$", "").strip()
    texto = texto.replace(",", ".")

    # Remove unidades comuns (ex: "123 m³", "450kWh")
    texto = re.sub(r'[a-zA-Z³]', '', texto).strip()

    # Rejeita textos muito curtos ou que sejam só zeros
    if len(texto) < 1:
        return False

    try:
        float(texto)
        return True
    except ValueError:
        return False


def normalizar_valor(valor: str | float) -> float:
    """Converte string de valor para float, lidando com vírgula brasileira."""
    if isinstance(valor, (int, float)):
        return float(valor)

    valor = str(valor).strip()
    valor = valor.replace("R$", "").replace("$", "").strip()
    valor = re.sub(r'[a-zA-Z³\s]', '', valor)

    if not valor:
        raise ValueError("Valor vazio após limpeza")

    # Formato brasileiro: 1.234,56
    if "," in valor and "." in valor:
        if valor.index(".") < valor.index(","):
            valor = valor.replace(".", "").replace(",", ".")
        else:
            valor = valor.replace(",", "")
    elif "," in valor:
        valor = valor.replace(",", ".")

    return float(valor)


def safe_normalizar(valor) -> float | None:
    """Versão segura de normalizar_valor, retorna None em caso de erro."""
    try:
        return normalizar_valor(valor)
    except Exception:
        return None