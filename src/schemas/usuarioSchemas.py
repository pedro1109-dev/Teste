# usuarioSchemas.py - Esquemas Pydantic para validação de dados de usuário
# Define modelos para criação, atualização e login de usuários.

from pydantic import BaseModel

class UsuarioCreate(BaseModel):
    # Esquema para criar novo usuário
    nome: str
    email: str
    senha: str

class UsuarioUpdate(BaseModel):
    # Esquema para atualizar dados do usuário
    nome: str
    email: str

class SenhaUpdate(BaseModel):
    # Esquema para atualizar senha
    senha_atual: str
    nova_senha: str

class LoginCreate(BaseModel):
    # Esquema para dados de login
    email: str
    senha: str