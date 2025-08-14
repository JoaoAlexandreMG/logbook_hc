# app/email.py
import threading

from flask import current_app
from flask_mail import Message

from app import mail


def send_async_email(app, msg):
    """Envia email de forma assíncrona"""
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body=None):
    """Função para enviar emails"""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    if html_body:
        msg.html = html_body

    # Envia o email em uma thread separada para não bloquear a aplicação
    thread = threading.Thread(
        target=send_async_email, args=(current_app._get_current_object(), msg)
    )
    thread.start()


def send_procedimento_avaliado_email(residente, procedimento, status):
    """Envia email quando um procedimento é avaliado"""
    if status == "Validado":
        subject = f"✅ Procedimento Aprovado - {procedimento.nome_procedimento}"
        template_text = f"""
Olá {residente.nome},

Seu procedimento foi APROVADO!

Detalhes do Procedimento:
- Nome: {procedimento.nome_procedimento}
- Data de Realização: {procedimento.data_realizacao.strftime('%d/%m/%Y')}
- Preceptor: {procedimento.preceptor.nome}

{f"Observações do Preceptor: {procedimento.observacao_preceptor}" if procedimento.observacao_preceptor else ""}

Parabéns pelo seu progresso!

Atenciosamente,
Sistema de Logbook do Residente
        """

        template_html = f"""
<html>
<body>
    <h2 style="color: #28a745;">✅ Procedimento Aprovado</h2>
    <p>Olá <strong>{residente.nome}</strong>,</p>
    
    <p>Seu procedimento foi <strong style="color: #28a745;">APROVADO</strong>!</p>
    
    <div style="border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 5px;">
        <h3>Detalhes do Procedimento:</h3>
        <ul>
            <li><strong>Nome:</strong> {procedimento.nome_procedimento}</li>
            <li><strong>Data de Realização:</strong> {procedimento.data_realizacao.strftime('%d/%m/%Y')}</li>
            <li><strong>Preceptor:</strong> {procedimento.preceptor.nome}</li>
        </ul>
        
        {f"<p><strong>Observações do Preceptor:</strong><br>{procedimento.observacao_preceptor}</p>" if procedimento.observacao_preceptor else ""}
    </div>
    
    <p style="color: #28a745;"><strong>Parabéns pelo seu progresso!</strong></p>
    
    <hr>
    <p><em>Sistema de Logbook do Residente</em></p>
</body>
</html>
        """

    else:  # Rejeitado
        subject = f"❌ Procedimento Rejeitado - {procedimento.nome_procedimento}"
        template_text = f"""
Olá {residente.nome},

Seu procedimento foi REJEITADO e precisa ser revisado.

Detalhes do Procedimento:
- Nome: {procedimento.nome_procedimento}
- Data de Realização: {procedimento.data_realizacao.strftime('%d/%m/%Y')}
- Preceptor: {procedimento.preceptor.nome}

{f"Observações do Preceptor: {procedimento.observacao_preceptor}" if procedimento.observacao_preceptor else ""}

Por favor, revise as informações e reenvie o procedimento se necessário.

Atenciosamente,
Sistema de Logbook do Residente
        """

        template_html = f"""
<html>
<body>
    <h2 style="color: #dc3545;">❌ Procedimento Rejeitado</h2>
    <p>Olá <strong>{residente.nome}</strong>,</p>
    
    <p>Seu procedimento foi <strong style="color: #dc3545;">REJEITADO</strong> e precisa ser revisado.</p>
    
    <div style="border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 5px;">
        <h3>Detalhes do Procedimento:</h3>
        <ul>
            <li><strong>Nome:</strong> {procedimento.nome_procedimento}</li>
            <li><strong>Data de Realização:</strong> {procedimento.data_realizacao.strftime('%d/%m/%Y')}</li>
            <li><strong>Preceptor:</strong> {procedimento.preceptor.nome}</li>
        </ul>
        
        {f"<p><strong>Observações do Preceptor:</strong><br>{procedimento.observacao_preceptor}</p>" if procedimento.observacao_preceptor else ""}
    </div>
    
    <p style="color: #ffc107;">Por favor, revise as informações e reenvie o procedimento se necessário.</p>
    
    <hr>
    <p><em>Sistema de Logbook do Residente</em></p>
</body>
</html>
        """

    send_email(
        subject=subject,
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[residente.email],
        text_body=template_text,
        html_body=template_html,
    )
