# senhaSchemas.py - Esquemas para recuperação de senha
# Define modelos para solicitação de reset e redefinição de senha.

from pydantic import BaseModel, EmailStr

class EmailRequest(BaseModel):
    # Esquema para solicitar reset de senha
    email: EmailStr  # Email válido

class ResetRequest(BaseModel):
    # Esquema para redefinir senha com token
    token: str  # Token de reset
    nova_senha: str  # Nova senha