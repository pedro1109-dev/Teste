# MetasRotas.py - Router para operações de metas de consumo
# Permite criar, atualizar, listar e deletar metas de consumo sustentável.

from fastapi import APIRouter, Depends, HTTPException
from src.schemas.metasSchemas import MetasCreate, MetasUpdate  # Esquemas para metas
from src.models.metaModel import Meta  # Modelo de meta
from sqlalchemy.orm import Session
from src.config.settings import get_db

metas_router = APIRouter(tags=["Metas"])  # Router para metas

@metas_router.post("/meta")
def metas(metas : MetasCreate, db : Session = Depends(get_db)):
    # Rota para criar uma nova meta
    nova_meta = Meta(
        objetivo = metas.objetivo,
        valor_limit = metas.valor_limit,
        data_meta = metas.data_meta,
        id_usuario = metas.id_usuario
        )
    db.add(nova_meta)
    db.commit()
    db.refresh(nova_meta)

    return{
        "mensagem":"Meta registrada com sucesso!!",
        "id" : nova_meta.id_metas
    }

@metas_router.put("/update_metas/{usuario_id}")
def consumo_update(metas_id: int, metas:MetasUpdate ,db: Session = Depends(get_db)):
    # Rota para atualizar uma meta existente (parâmetro usuario_id não usado)
    meta_existente = db.query(Meta).filter(Meta.id_metas == metas_id).first()
    if not meta_existente:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    
    meta_existente.objetivo = metas.objetivo
    meta_existente.valor_limit = metas.valor_limit
    meta_existente.data_meta = metas.data_meta
    db.commit()
    db.refresh(meta_existente)
    
    return {"mensagem": "Meta atualizada com sucesso"}

@metas_router.get("/lista_metas")
def Listar_Metas(id_usuario: int,db:Session = Depends(get_db)):
    # Rota para listar metas de um usuário
    listar_metas = db.query(Meta).filter(Meta.id_usuario == id_usuario).all()
    return listar_metas

@metas_router.delete("/delete/{metas_id}")
def deletar_metas(metas_id: int, db: Session = Depends(get_db)):
    # Rota para deletar uma meta
    meta_existente = db.query(Meta).filter(Meta.id_metas == metas_id).first()

    # 2. VERIFICA se ele realmente existe
    if not meta_existente:
        raise HTTPException(status_code=404, detail="Meta não existe")
    
    # 3. DELETA o objeto que você encontrou
    db.delete(meta_existente)
    
    # 4. COMMIT para salvar a alteração no banco
    db.commit()

    return {"mensagem": f"Meta {metas_id} removido com sucesso!"}