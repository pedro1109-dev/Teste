# password.py - Serviços para recuperação de senha
# Contém funções para gerar tokens, definir expiração e enviar emails de reset.

import secrets
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# Gera token seguro para recuperação de senha
def gerar_token():
    return secrets.token_urlsafe(32)

# Define tempo de expiração do token (15 minutos)
def gerar_expiracao():
    return datetime.utcnow() + timedelta(minutes=15)

# Envia email de recuperação com link
def enviar_email(destinatario: str, link: str):
    remetente = "pedro11souza09@gmail.com"
    senha = "xitx eobz qhku nndd"  # Senha do email (deve ser segura em produção)

    assunto = "Recuperação de senha"
    corpo = f"""
    <!DOCTYPE html>

<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
</head>
<body style="margin:0; padding:0; font-family: Arial, sans-serif; background-color:#eef2f3;">

  <table width="100%" cellpadding="0" cellspacing="0" style="padding: 20px;">
    <tr>
      <td align="center">

```
    <table width="520" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.08);">

      <!-- HEADER COM IMAGEM -->
      <tr>
        <td>
          <img src="https://images.unsplash.com/photo-1466611653911-95081537e5b7" 
               alt="Sustentabilidade" 
               width="100%" 
               style="display:block;">
        </td>
      </tr>

      <!-- LOGO / NOME -->
      <tr>
        <td align="center" style="padding:20px;">
          <h2 style="margin:0; color:#2e7d32;">🌱 EcoControl</h2>
          <p style="margin:5px 0 0; color:#7f8c8d; font-size:14px;">
            Tecnologia a favor da sustentabilidade
          </p>
        </td>
      </tr>

      <!-- CONTEÚDO -->
      <tr>
        <td style="padding: 0 30px 10px 30px; color:#333; font-size:16px; line-height:1.6;">
          
          <p>Prezado(a) usuário(a),</p>

          <p>
            Recebemos uma solicitação para redefinição de senha vinculada à sua conta na <strong>EcoControl</strong>.
          </p>

          <p>
            Para garantir a segurança das suas informações, disponibilizamos um link exclusivo para a criação de uma nova senha.
          </p>

        </td>
      </tr>

      <!-- BOTÃO -->
      <tr>
        <td align="center" style="padding:20px;">
          <a href="{{LINK_AQUI}}" 
             style="background-color:#2e7d32; color:#ffffff; padding:14px 30px; text-decoration:none; border-radius:6px; font-weight:bold; display:inline-block;">
            Redefinir minha senha
          </a>
        </td>
      </tr>

      <!-- IMAGEM SECUNDÁRIA -->
      <tr>
        <td align="center" style="padding: 10px 20px;">
          <img src="https://images.unsplash.com/photo-1501004318641-b39e6451bec6" 
               alt="Natureza" 
               width="100%" 
               style="border-radius:8px;">
        </td>
      </tr>

      <!-- TEXTO FINAL -->
      <tr>
        <td style="padding: 20px 30px; color:#555; font-size:14px; line-height:1.5;">
          
          <p>
            Por motivos de segurança, este link possui validade limitada e poderá expirar em breve.
          </p>

          <p>
            Caso você não tenha solicitado esta redefinição, recomendamos ignorar este e-mail. Nenhuma alteração será realizada sem sua confirmação.
          </p>

          <p>
            A EcoControl reforça seu compromisso com a segurança digital e com práticas sustentáveis.
          </p>

        </td>
      </tr>

      <!-- RODAPÉ -->
      <tr>
        <td style="background:#f4f6f7; padding:20px; text-align:center; font-size:12px; color:#95a5a6;">
          
          <p style="margin:0;">
            Este é um e-mail automático. Por favor, não responda.
          </p>

          <p style="margin:5px 0 0;">
            © 2026 EcoControl — Soluções Inteligentes e Sustentáveis 🌍
          </p>

        </td>
      </tr>

    </table>

  </td>
</tr>
```

  </table>

</body>
</html>


    
    """

    msg = MIMEText(corpo, "html")
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario

    with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
        servidor.starttls()
        servidor.login(remetente, senha)
        servidor.send_message(msg)