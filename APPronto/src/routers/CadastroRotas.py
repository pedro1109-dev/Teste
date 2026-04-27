# CadastroRotas.py - Router para operações de usuário (cadastro, atualização, listagem)
# Define as rotas relacionadas ao gerenciamento de usuários no sistema EcoControl.

from src.main import app  # Importa a app (não usado diretamente aqui)
from src.schemas.usuarioSchemas import UsuarioCreate, UsuarioUpdate, SenhaUpdate  # Esquemas para validação
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter
from src.config.settings import get_db  # Função para obter sessão do banco
from src.models.usuarioModel import Usuario  # Modelo do usuário
from src.middlewares.auth import hash_password, verify_password  # Funções de hash e verificação de senha

user_router = APIRouter(tags=["Usuário"])  # Cria o router com tag para documentação

@user_router.post("/registrar")
def Register (usuario: UsuarioCreate, db : Session = Depends(get_db)):
    # Rota para registrar um novo usuário
    usuario_existente = db.query(Usuario).filter(
        Usuario.email == usuario.email
    ).first()
    if usuario_existente :
        raise HTTPException(status_code=400, detail="Email já está cadastrado!!")

    novo_usuario = Usuario(
        nome = usuario.nome,
        email= usuario.email,
        senha = hash_password(usuario.senha)  # Hashea a senha antes de salvar
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return{
        "mensgem" : "Usuário criado com sucesso!!",
        "id": novo_usuario.id
    }

@user_router.put("/update/{usuario_id}")
def update_usuario(usuario_id: int, usuario: UsuarioUpdate, db: Session = Depends(get_db)):
    # Rota para atualizar dados de um usuário existente
    usuario_existente = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    usuario_existente.nome = usuario.nome
    usuario_existente.email = usuario.email
    db.commit()
    db.refresh(usuario_existente)
    
    return {"mensagem": "Usuário atualizado com sucesso"}

@user_router.get("/lista_usuario")
def Listar(id_usuario: int,db:Session = Depends(get_db)):
    # Rota para listar usuários (parece incompleta, filtra por id mas retorna lista)
    listar_usuario = db.query(Usuario).filter(Usuario.id == id_usuario).all()
    return listar_usuario

@user_router.put("/update-senha/{usuario_id}")
def update_senha(usuario_id: int, senha_data: SenhaUpdate, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if not verify_password(senha_data.senha_atual, usuario_existente.senha):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    
    usuario_existente.senha = hash_password(senha_data.nova_senha)
    db.commit()
    
    return {"mensagem": "Senha atualizada com sucesso"}

@user_router.delete("/delet/{usuario_id}") # Use .delete para rotas de remoção
def deletar(usuario_id: int, db: Session = Depends(get_db)):
    # 1. BUSCA o objeto primeiro
    usuario_existente = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    # 2. VERIFICA se ele realmente existe
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Consumo não existe")
    
    # 3. DELETA o objeto que você encontrou
    db.delete(usuario_existente)
    
    # 4. COMMIT para salvar a alteração no banco
    db.commit()

    return {"mensagem": f"Usuario {usuario_id} apagado com sucesso!"}

