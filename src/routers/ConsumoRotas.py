# ConsumoRotas.py - Router para operações de consumo (registro, atualização, listagem)
# Gerencia o registro e controle de consumo de energia/água dos usuários.

from src.main import app  # Importa a app (não usado)
from src.schemas.consumoSchemas import ConsumoCreate, ConsumoUpdate  # Esquemas para consumo
from datetime import datetime
from src.models.consumoModel import Consumo  # Modelo de consumo
from src.config.settings import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter

consumo_router = APIRouter(tags=["Consumo"])  # Router para rotas de consumo


    

@consumo_router.post("/consumo")
def registro_consumo(consumo: ConsumoCreate, db :Session = Depends(get_db)):
    # Rota para registrar um novo consumo
    novo_consumo = Consumo(
        tipo = consumo.tipo or "desconhecido",
        valor = consumo.valor,
        unidade = consumo.unidade,
        data = datetime.now(),  # Define a data atual
        id_usuario = consumo.id_usuario,
        id_meta = consumo.id_meta if consumo.id_meta not in (0, None) else None  # Trata meta opcional
        )
    db.add(novo_consumo)
    db.commit()
    db.refresh(novo_consumo)

    return{
        "mensagem":"Consumo registrado com sucesso!!",
        "id" : novo_consumo.id_consumos
    }

@consumo_router.put("/update_consumo/{usuario_id}")
def consumo_update(consumo_id: int, consumo:ConsumoUpdate ,db: Session = Depends(get_db)):
    # Rota para atualizar um consumo existente (nota: parâmetro usuario_id não usado)
    consumo_existente = db.query(Consumo).filter(Consumo.id_consumos == consumo_id).first()
    if not consumo_existente:
        raise HTTPException(status_code=404, detail="Consumo não encontrado")
    
    consumo_existente.tipo = consumo.tipo
    consumo_existente.valor = consumo.valor  # Erro de digitação: deveria ser valor
    consumo_existente.id_meta = consumo.id_meta if consumo.id_meta not in (0, None) else None
    db.commit()
    db.refresh(consumo_existente)
    
    return {"mensagem": "Consumo atualizado com sucesso"}

@consumo_router.get("/lista_consumo")
def Listar(id_usuario: int,db:Session = Depends(get_db)):
    # Rota para listar consumos de um usuário (incompleta, só declara a função)
    listar_consumo = db.query(Consumo).filter(Consumo.id_usuario == id_usuario).all()
    return listar_consumo




@consumo_router.delete("/delet/{consumo_id}") # Use .delete para rotas de remoção
def deletar(consumo_id: int, db: Session = Depends(get_db)):
    # 1. BUSCA o objeto primeiro
    consumo_existente = db.query(Consumo).filter(Consumo.id_consumos == consumo_id).first()

    # 2. VERIFICA se ele realmente existe
    if not consumo_existente:
        raise HTTPException(status_code=404, detail="Consumo não existe")
    
    # 3. DELETA o objeto que você encontrou
    db.delete(consumo_existente)
    
    # 4. COMMIT para salvar a alteração no banco
    db.commit()

    return {"mensagem": f"Consumo {consumo_id} removido com sucesso!"}

