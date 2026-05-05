# OcrRota.py - Router para processamento de OCR em faturas
# Permite upload de imagens de faturas, extração de dados via OCR e análise de consumo.

"""
OcrRota.py — Rotas FastAPI para upload de faturas e análise de consumo.

Endpoints:
  POST /ocr                    — envia imagem + id_usuario, extrai e salva
  GET  /analise/{id}           — análise detalhada de uma leitura
  GET  /historico/{id_usuario} — histórico do usuário com estimativas
  GET  /resumo/{id_usuario}    — visão consolidada do consumo do usuário
"""

import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.services.ocr import extrair_com_posicao, extrair_total_avancado  # Funções de OCR
from src.services.analysis import (
    analisar_consumo,
    analise_para_dict,
    LeituraFatura,
    classificar_nivel,
    NIVEL_LABELS,
)  # Funções de análise
from src.config.settings import get_db
from src.models.ocrModel import Ocr
from src.models.consumoModel import Consumo  # Modelo OCR

ocr_route = APIRouter(tags=["OCR"])  # Router para OCR

TEMP_DIR = "/tmp/ocr_uploads"  # Diretório temporário para uploads
os.makedirs(TEMP_DIR, exist_ok=True)

def _ocr_para_leitura(ocr: Ocr) -> LeituraFatura | None:
    # Converte modelo OCR para objeto LeituraFatura
    if ocr.consumo is None or ocr.total is None:
        return None
    return LeituraFatura(
        mes_referencia=ocr.mes_referencia or "",
        consumo=ocr.consumo,
        total=ocr.total,
        tipo=ocr.tipo_fatura or "desconhecido",
        vencimento=ocr.vencimento,
    )

# POST /ocr - Recebe imagem + id_usuario via multipart form

@ocr_route.post("/ocr", summary="Upload de fatura vinculada ao usuário")
async def upload_fatura(
    file:       UploadFile = File(...),
    id_usuario: int        = Form(...),   # ID do usuário logado
    db:         Session    = Depends(get_db),
):
    ext       = os.path.splitext(file.filename or "fatura.jpg")[1] or ".jpg"
    temp_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}{ext}")

    try:
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())

        # 1. OCR + Gemini
        words = extrair_com_posicao(temp_path)
        dados = await extrair_total_avancado(words)

        # 2. Histórico do usuário específico para análise comparativa
        tipo = dados.get("tipo_fatura") or "desconhecido"
        historico_db = (
            db.query(Ocr)
            .filter(Ocr.id_usuario == id_usuario, Ocr.tipo_fatura == tipo)
            .order_by(desc(Ocr.criado_em))
            .limit(12)
            .all()
        )
        historico = [h for h in (_ocr_para_leitura(r) for r in historico_db) if h]

        # 3. Análise de consumo
        analise      = None
        analise_dict = {}
        tipo_valido  = tipo if tipo in ("agua", "energia") else "agua"

        if dados.get("consumo") and dados.get("total"):
            analise = analisar_consumo(
                consumo_atual=float(dados["consumo"]),
                total_atual=float(dados["total"]),
                tipo=tipo_valido,
                historico=historico,
            )
            analise_dict = analise_para_dict(analise)

        # 4. Salva no banco vinculado ao usuário
        leitura = Ocr(
            id_usuario              = id_usuario,
            total                   = dados.get("total"),
            vencimento              = dados.get("vencimento"),
            consumo                 = dados.get("consumo"),
            unidade                 = dados.get("unidade"),
            mes_referencia          = dados.get("mes_referencia"),
            tipo_fatura             = dados.get("tipo_fatura"),
            concessionaria = dados.get("concessionaria") or "Desconhecida",
            nivel_consumo           = analise.nivel if analise else None,
            estimativa_proximo_mes  = analise.estimativa_proximo_mes if analise else None,
            estimativa_valor_proximo= analise.estimativa_valor_proximo_mes if analise else None,
        )

        db.add(leitura)
        db.commit()
        db.refresh(leitura)

        return {
            "id_leitura":     leitura.id_leitura,
            "dados_extraidos": dados,
            "analise":        analise_dict,
            "aviso_ia":       dados.get("aviso_ia"),
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ─────────────────────────────────────────────
# GET /analise/{id_leitura}
# ─────────────────────────────────────────────

@ocr_route.get("/analise/{id_leitura}", summary="Análise detalhada de uma fatura")
def get_analise(id_leitura: int, db: Session = Depends(get_db)):
    leitura = db.query(Ocr).filter(Ocr.id_leitura == id_leitura).first()
    if not leitura:
        raise HTTPException(status_code=404, detail="Leitura não encontrada")

    tipo = leitura.tipo_fatura or "agua"
    historico_db = (
        db.query(Ocr)
        .filter(
            Ocr.id_usuario == leitura.id_usuario,
            Ocr.tipo_fatura == tipo,
            Ocr.id_leitura != id_leitura,
        )
        .order_by(desc(Ocr.criado_em))
        .limit(12)
        .all()
    )
    historico = [h for h in (_ocr_para_leitura(r) for r in historico_db) if h]

    if not leitura.consumo or not leitura.total:
        raise HTTPException(status_code=422, detail="Dados insuficientes para análise")

    analise = analisar_consumo(
        consumo_atual=leitura.consumo,
        total_atual=leitura.total,
        tipo=tipo if tipo in ("agua", "energia") else "agua",
        historico=historico,
    )

    return {
        "id_leitura": id_leitura,
        "fatura": {
            "total":          leitura.total,
            "consumo":        leitura.consumo,
            "unidade":        leitura.unidade,
            "vencimento":     leitura.vencimento,
            "mes_referencia": leitura.mes_referencia,
            "tipo_fatura":    leitura.tipo_fatura,
            "concessionaria": leitura.concessionaria,
        },
        "analise": analise_para_dict(analise),
    }




# ─────────────────────────────────────────────
# GET /resumo/{id_usuario}
# ─────────────────────────────────────────────

@ocr_route.get("/resumo/{id_usuario}", summary="Resumo geral do consumo do usuário")
def get_resumo(id_usuario: int, db: Session = Depends(get_db)):
    resultado = {}

    for tipo in ("agua", "energia"):
        leituras = (
            db.query(Ocr)
            .filter(
                Ocr.id_usuario == id_usuario,
                Ocr.tipo_fatura == tipo,
                Ocr.consumo.isnot(None),
            )
            .order_by(desc(Ocr.criado_em))
            .limit(12)
            .all()
        )

        if not leituras:
            resultado[tipo] = {"mensagem": "Nenhuma leitura disponível"}
            continue

        consumos = [r.consumo for r in leituras if r.consumo]
        valores  = [r.total   for r in leituras if r.total]
        unidade  = leituras[0].unidade or ("kWh" if tipo == "energia" else "m³")

        media_consumo = sum(consumos) / len(consumos) if consumos else 0
        media_valor   = sum(valores)  / len(valores)  if valores  else 0

        tendencia = None
        if len(consumos) >= 2:
            delta     = consumos[0] - consumos[1]
            tendencia = "subindo" if delta > 0 else "caindo" if delta < 0 else "estável"

        nivel_atual = classificar_nivel(consumos[0], tipo) if consumos else None

        resultado[tipo] = {
            "total_faturas":            len(leituras),
            "media_consumo":            round(media_consumo, 2),
            "media_valor":              round(media_valor, 2),
            "unidade":                  unidade,
            "tendencia":                tendencia,
            "nivel_atual":              nivel_atual,
            "nivel_label":              NIVEL_LABELS.get(nivel_atual) if nivel_atual else None,
            "estimativa_proximo_mes":   leituras[0].estimativa_proximo_mes,
            "estimativa_valor_proximo": leituras[0].estimativa_valor_proximo,
            "ultima_fatura": {
                "mes_referencia": leituras[0].mes_referencia,
                "consumo":        leituras[0].consumo,
                "total":          leituras[0].total,
            },
        }

    return resultado

@ocr_route.post("/converter/{id_leitura}")
def converter_para_consumo(id_leitura: int, db: Session = Depends(get_db)):
    
    leitura = db.query(Ocr).filter(Ocr.id_leitura == id_leitura).first()

    if not leitura:
        raise HTTPException(status_code=404, detail="Leitura não encontrada")

    # validação mínima
    if not leitura.consumo or not leitura.total:
        raise HTTPException(status_code=400, detail="Dados incompletos para conversão")
    
    existe = db.query(Consumo).filter(
        Consumo.id_usuario == leitura.id_usuario,
        Consumo.tipo == leitura.tipo_fatura,
        Consumo.mes_referencia == leitura.mes_referencia,
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail=f"Consumo de '{leitura.tipo_fatura}' já registrado para {leitura.mes_referencia or 'esse mês'}",
        )

    novo_consumo = Consumo(
        id_usuario=leitura.id_usuario,
        consumo=leitura.consumo,
        valor=leitura.total,
        unidade=leitura.unidade,
        tipo=leitura.tipo_fatura,
        mes_referencia=leitura.mes_referencia,
        vencimento=leitura.vencimento,
        origem="ocr"
    )
    

    db.add(novo_consumo)
    db.commit()
    db.refresh(novo_consumo)

    return {
        "mensagem": "Convertido com sucesso",
        "consumo": {
            "id": novo_consumo.id_consumos,
            "consumo": novo_consumo.consumo,
            "total": novo_consumo.total
        }
    }