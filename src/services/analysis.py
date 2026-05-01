"""
analysis.py — Módulo de análise de consumo e estimativa mensal.

Classifica o nível de consumo do usuário e projeta gastos futuros
com base no histórico de leituras.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, date
import statistics


# ─────────────────────────────────────────────
# BENCHMARKS MÉDIOS BRASILEIROS (ANEEL / SNIS)
# ─────────────────────────────────────────────

# Consumo médio residencial de energia por mês (kWh) — ANEEL 2024
ENERGIA_BENCHMARKS = {
    "muito_baixo": (0, 100),
    "baixo": (100, 200),
    "medio": (200, 350),
    "alto": (350, 600),
    "muito_alto": (600, float("inf")),
}

# Consumo médio residencial de água por mês (m³) — SNIS 2024
# Referência: ~150 L/pessoa/dia → família de 4 pessoas ≈ 18 m³/mês
AGUA_BENCHMARKS = {
    "muito_baixo": (0, 8),
    "baixo": (8, 15),
    "medio": (15, 25),
    "alto": (25, 40),
    "muito_alto": (40, float("inf")),
}

NIVEL_LABELS = {
    "muito_baixo": "Muito Baixo",
    "baixo": "Baixo",
    "medio": "Na Média",
    "alto": "Alto",
    "muito_alto": "Risco — Consumo Crítico",
}

NIVEL_CORES = {
    "muito_baixo": "#60a5fa",   # azul claro
    "baixo": "#34d399",          # verde
    "medio": "#fbbf24",          # amarelo
    "alto": "#f97316",           # laranja
    "muito_alto": "#ef4444",     # vermelho
}


# ─────────────────────────────────────────────
# DATACLASSES
# ─────────────────────────────────────────────

@dataclass
class LeituraFatura:
    mes_referencia: str          # "03/2025"
    consumo: float               # m³ ou kWh
    total: float                 # valor em R$
    tipo: str                    # "agua" ou "energia"
    vencimento: Optional[str] = None


@dataclass
class AnaliseConsumo:
    nivel: str                           # chave interna
    nivel_label: str                     # label para exibição                            # hex color
    consumo_atual: float
    unidade: str
    media_historico: Optional[float]
    variacao_percentual: Optional[float]  # vs. média histórica
    estimativa_proximo_mes: Optional[float]  # projeção de consumo
    estimativa_valor_proximo_mes: Optional[float]  # projeção em R$
    custo_por_unidade: Optional[float]
    recomendacoes: list[str] = field(default_factory=list)
    alerta: Optional[str] = None


# ─────────────────────────────────────────────
# CLASSIFICADOR DE NÍVEL
# ─────────────────────────────────────────────

def classificar_nivel(consumo: float, tipo: str) -> str:
    benchmarks = ENERGIA_BENCHMARKS if tipo == "energia" else AGUA_BENCHMARKS
    for nivel, (minimo, maximo) in benchmarks.items():
        if minimo <= consumo < maximo:
            return nivel
    return "muito_alto"


def calcular_variacao(atual: float, media: float) -> float:
    """Variação percentual do consumo atual vs. média histórica."""
    if media == 0:
        return 0.0
    return round(((atual - media) / media) * 100, 1)


# ─────────────────────────────────────────────
# GERAÇÃO DE RECOMENDAÇÕES
# ─────────────────────────────────────────────

def gerar_recomendacoes(nivel: str, tipo: str, variacao: Optional[float]) -> list[str]:
    recomendacoes = []

    if tipo == "energia":
        if nivel in ("alto", "muito_alto"):
            recomendacoes += [
                "Verifique aparelhos em standby — TVs, carregadores e ar-condicionado consomem mesmo desligados.",
                "Considere substituir lâmpadas por LED se ainda não o fez.",
                "Avalie o uso do chuveiro elétrico — é o maior vilão do consumo.",
                "Cheque se a geladeira está vedando bem e com temperatura adequada (entre 3°C e 7°C).",
            ]
        elif nivel == "medio":
            recomendacoes += [
                "Seu consumo está dentro da média, mas há espaço para redução.",
                "Tente desligar luzes ao sair dos cômodos — pode reduzir até 10% da conta.",
            ]
        else:
            recomendacoes += [
                "Excelente! Seu consumo está abaixo da média nacional.",
                "Mantenha os bons hábitos de uso consciente de energia.",
            ]

    else:  # agua
        if nivel in ("alto", "muito_alto"):
            recomendacoes += [
                "Verifique vazamentos — uma torneira pingando gasta até 46 litros por dia.",
                "Reduza o tempo no banho para menos de 5 minutos.",
                "Considere instalar redutores de vazão nas torneiras.",
                "Reutilize a água do enxágue da máquina de lavar para limpar o quintal.",
            ]
        elif nivel == "medio":
            recomendacoes += [
                "Consumo dentro da faixa esperada para uma família.",
                "Fechar a torneira ao escovar os dentes economiza até 12 litros por vez.",
            ]
        else:
            recomendacoes += [
                "Consumo muito eficiente! Continue com os bons hábitos.",
                "Compartilhe suas práticas de economia de água com vizinhos e familiares.",
            ]

    if variacao is not None and variacao > 20:
        recomendacoes.insert(0, f"⚠️ Seu consumo subiu {variacao:.0f}% em relação à sua média histórica.")

    return recomendacoes


def gerar_alerta(nivel: str, variacao: Optional[float]) -> Optional[str]:
    if nivel == "muito_alto":
        return "🔴 Consumo crítico! Verifique imediatamente possíveis vazamentos ou equipamentos com defeito."
    if nivel == "alto" and variacao is not None and variacao > 30:
        return f"🟠 Consumo alto com aumento de {variacao:.0f}% vs. sua média. Atenção redobrada."
    if variacao is not None and variacao > 50:
        return f"🟡 Aumento atípico de {variacao:.0f}% detectado. Revise o uso neste período."
    return None


# ─────────────────────────────────────────────
# ANÁLISE PRINCIPAL
# ─────────────────────────────────────────────

def analisar_consumo(
    consumo_atual: float,
    total_atual: float,
    tipo: str,                              # "agua" ou "energia"
    historico: Optional[list[LeituraFatura]] = None,
) -> AnaliseConsumo:
    """
    Gera análise completa de consumo com projeções e recomendações.

    Args:
        consumo_atual: consumo do mês atual (m³ ou kWh)
        total_atual: valor da fatura atual em R$
        tipo: "agua" ou "energia"
        historico: lista de faturas anteriores (opcional)

    Returns:
        AnaliseConsumo com todos os dados calculados
    """
    unidade = "m³" if tipo == "agua" else "kWh"

    # Histórico de consumos anteriores
    consumos_hist = []
    valores_hist = []

    if historico:
        consumos_hist = [f.consumo for f in historico if f.consumo is not None and f.tipo == tipo]
        valores_hist = [f.total for f in historico if f.total is not None and f.tipo == tipo]

    media_consumo = statistics.mean(consumos_hist) if consumos_hist else None
    media_valor = statistics.mean(valores_hist) if valores_hist else None

    variacao = calcular_variacao(consumo_atual, media_consumo) if media_consumo else None

    # Projeção simples: média ponderada dando mais peso ao mês atual
    if consumos_hist:
        todos = consumos_hist + [consumo_atual]
        pesos = [1] * len(consumos_hist) + [2]  # mês atual tem peso 2
        estimativa_consumo = sum(c * p for c, p in zip(todos, pesos)) / sum(pesos)
        estimativa_consumo = round(estimativa_consumo, 2)
    else:
        estimativa_consumo = consumo_atual

    # Custo por unidade
    custo_por_unidade = round(total_atual / consumo_atual, 4) if consumo_atual > 0 else None

    # Projeção de valor
    if custo_por_unidade:
        estimativa_valor = round(estimativa_consumo * custo_por_unidade, 2)
    elif media_valor:
        estimativa_valor = round((media_valor + total_atual) / 2, 2)
    else:
        estimativa_valor = total_atual

    nivel = classificar_nivel(consumo_atual, tipo)
    recomendacoes = gerar_recomendacoes(nivel, tipo, variacao)
    alerta = gerar_alerta(nivel, variacao)

    return AnaliseConsumo(
        nivel=nivel,
        nivel_label=NIVEL_LABELS[nivel],
        consumo_atual=consumo_atual,
        unidade=unidade,
        media_historico=round(media_consumo, 2) if media_consumo else None,
        variacao_percentual=variacao,
        estimativa_proximo_mes=estimativa_consumo,
        estimativa_valor_proximo_mes=estimativa_valor,
        custo_por_unidade=custo_por_unidade,
        recomendacoes=recomendacoes,
        alerta=alerta,
    )


def analise_para_dict(analise: AnaliseConsumo) -> dict:
    """Serializa AnaliseConsumo para dict (para resposta da API)."""
    return {
        "nivel": analise.nivel,
        "nivel_label": analise.nivel_label,
        "consumo_atual": analise.consumo_atual,
        "unidade": analise.unidade,
        "media_historico": analise.media_historico,
        "variacao_percentual": analise.variacao_percentual,
        "estimativa_proximo_mes": analise.estimativa_proximo_mes,
        "estimativa_valor_proximo_mes": analise.estimativa_valor_proximo_mes,
        "custo_por_unidade": analise.custo_por_unidade,
        "recomendacoes": analise.recomendacoes,
        "alerta": analise.alerta,
    }