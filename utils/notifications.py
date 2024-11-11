import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailNotifier:
    def __init__(self):
        self.smtp_username = os.environ.get('SMTP_USERNAME')
        self.smtp_password = os.environ.get('SMTP_PASSWORD')
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_notification(self, recipients, subject, message):
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'html'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            logger.info(f"Email notification sent successfully to {recipients}")
            return True
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False

    def format_contract_notification(self, contracts):
        """Format contract information for email"""
        html = """
        <html>
            <head>
                <style>
                    table { border-collapse: collapse; width: 100%; }
                    th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
                    th { background-color: #f2f2f2; }
                </style>
            </head>
            <body>
                <h2>Nuevos Contratos de Transporte</h2>
                <p>Se han detectado los siguientes contratos nuevos:</p>
                <table>
                    <tr>
                        <th>Entidad</th>
                        <th>Tipo de Contrato</th>
                        <th>Valor</th>
                        <th>Fecha</th>
                    </tr>
        """
        
        for contract in contracts:
            html += f"""
                <tr>
                    <td>{contract.get('nombre_entidad', 'N/A')}</td>
                    <td>{contract.get('tipo_de_contrato', 'N/A')}</td>
                    <td>${contract.get('valor_del_contrato', 0):,.2f}</td>
                    <td>{contract.get('fecha_de_firma', 'N/A')}</td>
                </tr>
            """
            
        html += """
                </table>
                <p>Para más detalles, ingrese al sistema de gestión de contratos.</p>
            </body>
        </html>
        """
        return html

def notify_new_contracts(contracts, recipients):
    """Send notification for new contracts"""
    notifier = EmailNotifier()
    subject = f"Nuevos Contratos de Transporte - {datetime.now().strftime('%Y-%m-%d')}"
    message = notifier.format_contract_notification(contracts)
    return notifier.send_notification(recipients, subject, message)
