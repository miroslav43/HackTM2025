"""
Comprehensive email notification service with templates and delivery management.
Handles email notifications for various system events and user actions.
"""

import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import aiosmtplib
from jinja2 import Environment, FileSystemLoader, BaseLoader
import logging

from ..core.config import settings


class EmailTemplates:
    """
    Email template management with Jinja2
    """
    
    def __init__(self):
        # Default email templates
        self.templates = {
            'welcome': {
                'subject': 'Bun venit pe Platforma Administratiei Publice Romane',
                'html': '''
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
                        <h1 style="color: #0d6efd;">Bun venit!</h1>
                    </div>
                    <div style="padding: 20px;">
                        <p>Salut <strong>{{ user_name }}</strong>,</p>
                        <p>Contul tau a fost creat cu succes pe Platforma Administratiei Publice Romane.</p>
                        <p><strong>Detalii cont:</strong></p>
                        <ul>
                            <li>Email: {{ user_email }}</li>
                            <li>Rol: {{ user_role }}</li>
                            <li>Data inregistrarii: {{ registration_date }}</li>
                        </ul>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{ login_url }}" style="background-color: #0d6efd; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">Acceseaza Platforma</a>
                        </div>
                        <p>Daca ai intrebari, nu ezita sa ne contactezi.</p>
                        <p>Cu respect,<br>Echipa Administratiei Publice</p>
                    </div>
                </body>
                </html>
                ''',
                'text': '''
                Bun venit pe Platforma Administratiei Publice Romane!
                
                Salut {{ user_name }},
                
                Contul tau a fost creat cu succes.
                
                Detalii cont:
                - Email: {{ user_email }}
                - Rol: {{ user_role }}
                - Data inregistrarii: {{ registration_date }}
                
                Acceseaza platforma la: {{ login_url }}
                
                Daca ai intrebari, nu ezita sa ne contactezi.
                
                Cu respect,
                Echipa Administratiei Publice
                '''
            },
            
            'document_verified': {
                'subject': 'Document verificat - {{ document_name }}',
                'html': '''
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #d1e7dd; padding: 20px; text-align: center;">
                        <h1 style="color: #0f5132;">Document Verificat</h1>
                    </div>
                    <div style="padding: 20px;">
                        <p>Salut <strong>{{ user_name }}</strong>,</p>
                        <p>Documentul tau <strong>"{{ document_name }}"</strong> a fost verificat si aprobat.</p>
                        <p><strong>Detalii:</strong></p>
                        <ul>
                            <li>Nume document: {{ document_name }}</li>
                            <li>Status: <span style="color: #0f5132; font-weight: bold;">Verificat</span></li>
                            <li>Data verificarii: {{ verification_date }}</li>
                            <li>Verificat de: {{ verified_by }}</li>
                        </ul>
                        {% if verification_notes %}
                        <p><strong>Note de verificare:</strong></p>
                        <p style="background-color: #f8f9fa; padding: 10px; border-left: 4px solid #0d6efd;">{{ verification_notes }}</p>
                        {% endif %}
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{ document_url }}" style="background-color: #0d6efd; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">Vezi Document</a>
                        </div>
                        <p>Cu respect,<br>Echipa Administratiei Publice</p>
                    </div>
                </body>
                </html>
                ''',
                'text': '''
                Document Verificat
                
                Salut {{ user_name }},
                
                Documentul tau "{{ document_name }}" a fost verificat si aprobat.
                
                Detalii:
                - Nume document: {{ document_name }}
                - Status: Verificat
                - Data verificarii: {{ verification_date }}
                - Verificat de: {{ verified_by }}
                
                {% if verification_notes %}
                Note de verificare: {{ verification_notes }}
                {% endif %}
                
                Vezi documentul la: {{ document_url }}
                
                Cu respect,
                Echipa Administratiei Publice
                '''
            },
            
            'document_rejected': {
                'subject': 'Document respins - {{ document_name }}',
                'html': '''
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #f8d7da; padding: 20px; text-align: center;">
                        <h1 style="color: #842029;">Document Respins</h1>
                    </div>
                    <div style="padding: 20px;">
                        <p>Salut <strong>{{ user_name }}</strong>,</p>
                        <p>Din pacate, documentul tau <strong>"{{ document_name }}"</strong> a fost respins.</p>
                        <p><strong>Detalii:</strong></p>
                        <ul>
                            <li>Nume document: {{ document_name }}</li>
                            <li>Status: <span style="color: #842029; font-weight: bold;">Respins</span></li>
                            <li>Data respingerii: {{ rejection_date }}</li>
                            <li>Respins de: {{ rejected_by }}</li>
                        </ul>
                        <p><strong>Motiv respingere:</strong></p>
                        <p style="background-color: #f8d7da; padding: 10px; border-left: 4px solid #dc3545;">{{ rejection_reason }}</p>
                        <p>Te rugam sa corectezi problemele mentionate si sa incarci din nou documentul.</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{ upload_url }}" style="background-color: #dc3545; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">Incarca Din Nou</a>
                        </div>
                        <p>Cu respect,<br>Echipa Administratiei Publice</p>
                    </div>
                </body>
                </html>
                ''',
                'text': '''
                Document Respins
                
                Salut {{ user_name }},
                
                Din pacate, documentul tau "{{ document_name }}" a fost respins.
                
                Detalii:
                - Nume document: {{ document_name }}
                - Status: Respins
                - Data respingerii: {{ rejection_date }}
                - Respins de: {{ rejected_by }}
                
                Motiv respingere: {{ rejection_reason }}
                
                Te rugam sa corectezi problemele mentionate si sa incarci din nou documentul.
                
                Incarca din nou la: {{ upload_url }}
                
                Cu respect,
                Echipa Administratiei Publice
                '''
            },
            
            'password_reset': {
                'subject': 'Resetare parola - Platforma Administratiei Publice',
                'html': '''
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #fff3cd; padding: 20px; text-align: center;">
                        <h1 style="color: #856404;">Resetare Parola</h1>
                    </div>
                    <div style="padding: 20px;">
                        <p>Salut <strong>{{ user_name }}</strong>,</p>
                        <p>Ai solicitat resetarea parolei pentru contul tau pe Platforma Administratiei Publice.</p>
                        <p>Pentru a reseta parola, te rugam sa accesezi linkul de mai jos:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{ reset_url }}" style="background-color: #ffc107; color: black; padding: 12px 24px; text-decoration: none; border-radius: 5px;">Reseteaza Parola</a>
                        </div>
                        <p><strong>Linkul este valabil {{ expiry_hours }} ore.</strong></p>
                        <p>Daca nu ai solicitat aceasta resetare, poti ignora acest email.</p>
                        <p>Cu respect,<br>Echipa Administratiei Publice</p>
                    </div>
                </body>
                </html>
                ''',
                'text': '''
                Resetare Parola
                
                Salut {{ user_name }},
                
                Ai solicitat resetarea parolei pentru contul tau pe Platforma Administratiei Publice.
                
                Pentru a reseta parola, acceseaza: {{ reset_url }}
                
                Linkul este valabil {{ expiry_hours }} ore.
                
                Daca nu ai solicitat aceasta resetare, poti ignora acest email.
                
                Cu respect,
                Echipa Administratiei Publice
                '''
            },
            
            'system_notification': {
                'subject': '{{ notification_title }}',
                'html': '''
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #e7f3ff; padding: 20px; text-align: center;">
                        <h1 style="color: #004085;">{{ notification_title }}</h1>
                    </div>
                    <div style="padding: 20px;">
                        <p>Salut <strong>{{ user_name }}</strong>,</p>
                        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #0d6efd;">
                            {{ notification_content | safe }}
                        </div>
                        {% if action_url %}
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{ action_url }}" style="background-color: #0d6efd; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">{{ action_text | default("Vezi Detalii") }}</a>
                        </div>
                        {% endif %}
                        <p>Cu respect,<br>Echipa Administratiei Publice</p>
                    </div>
                </body>
                </html>
                ''',
                'text': '''
                {{ notification_title }}
                
                Salut {{ user_name }},
                
                {{ notification_content }}
                
                {% if action_url %}
                Vezi detalii la: {{ action_url }}
                {% endif %}
                
                Cu respect,
                Echipa Administratiei Publice
                '''
            }
        }
        
        # Initialize Jinja2 environment
        self.env = Environment(loader=BaseLoader())
    
    def render_template(self, template_name: str, format_type: str, **kwargs) -> str:
        """Render email template with provided data"""
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} not found")
        
        template = self.templates[template_name]
        content = template.get(format_type, '')
        
        # Simple template rendering (replace {{ var }} with values)
        for key, value in kwargs.items():
            content = content.replace(f'{{{{ {key} }}}}', str(value))
        
        return content


class EmailService:
    """
    Advanced email service with queue management and delivery tracking
    """
    
    def __init__(self):
        self.templates = EmailTemplates()
        
        # Email configuration
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'localhost')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.smtp_use_tls = getattr(settings, 'SMTP_USE_TLS', True)
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@admin.gov.ro')
        self.from_name = getattr(settings, 'FROM_NAME', 'Platforma Administratiei Publice')
        
        # Email queue (in production, use Redis or similar)
        self.email_queue = []
        self.failed_emails = []
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send email with HTML and text content
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Prepare recipient list
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            # Send email
            await self._send_smtp_email(msg, recipients)
            
            self.logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            
            # Add to failed queue for retry
            self.failed_emails.append({
                'to_email': to_email,
                'subject': subject,
                'html_content': html_content,
                'text_content': text_content,
                'error': str(e),
                'timestamp': datetime.utcnow(),
                'retry_count': 0
            })
            
            return False
    
    async def _send_smtp_email(self, msg: MIMEMultipart, recipients: List[str]):
        """Send email via SMTP"""
        if self.smtp_server == 'localhost' or not self.smtp_username:
            # Development mode - just log
            self.logger.info(f"[DEV MODE] Email would be sent to: {recipients}")
            self.logger.info(f"Subject: {msg['Subject']}")
            return
        
        # Production SMTP sending
        async with aiosmtplib.SMTP(
            hostname=self.smtp_server,
            port=self.smtp_port,
            use_tls=self.smtp_use_tls
        ) as server:
            if self.smtp_username and self.smtp_password:
                await server.login(self.smtp_username, self.smtp_password)
            
            await server.send_message(msg, recipients=recipients)
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message"""
        try:
            with open(attachment['path'], 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment.get("filename", "attachment")}'
            )
            msg.attach(part)
            
        except Exception as e:
            self.logger.error(f"Failed to add attachment {attachment.get('path')}: {str(e)}")
    
    async def send_template_email(
        self,
        to_email: str,
        template_name: str,
        template_data: Dict[str, Any],
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Send email using predefined template
        """
        try:
            # Render subject
            subject = self.templates.render_template(template_name, 'subject', **template_data)
            
            # Render HTML content
            html_content = self.templates.render_template(template_name, 'html', **template_data)
            
            # Render text content
            text_content = self.templates.render_template(template_name, 'text', **template_data)
            
            return await self.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                attachments=attachments
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send template email '{template_name}' to {to_email}: {str(e)}")
            return False
    
    # Convenience methods for common notifications
    
    async def send_welcome_email(self, user_email: str, user_name: str, user_role: str) -> bool:
        """Send welcome email to new user"""
        template_data = {
            'user_name': user_name,
            'user_email': user_email,
            'user_role': user_role,
            'registration_date': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'login_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/login"
        }
        
        return await self.send_template_email(user_email, 'welcome', template_data)
    
    async def send_document_verification_email(
        self,
        user_email: str,
        user_name: str,
        document_name: str,
        verified_by: str,
        verification_notes: Optional[str] = None
    ) -> bool:
        """Send document verification notification"""
        template_data = {
            'user_name': user_name,
            'document_name': document_name,
            'verification_date': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'verified_by': verified_by,
            'verification_notes': verification_notes,
            'document_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/documents"
        }
        
        return await self.send_template_email(user_email, 'document_verified', template_data)
    
    async def send_document_rejection_email(
        self,
        user_email: str,
        user_name: str,
        document_name: str,
        rejected_by: str,
        rejection_reason: str
    ) -> bool:
        """Send document rejection notification"""
        template_data = {
            'user_name': user_name,
            'document_name': document_name,
            'rejection_date': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'rejected_by': rejected_by,
            'rejection_reason': rejection_reason,
            'upload_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/documents/upload"
        }
        
        return await self.send_template_email(user_email, 'document_rejected', template_data)
    
    async def send_password_reset_email(
        self,
        user_email: str,
        user_name: str,
        reset_token: str,
        expiry_hours: int = 24
    ) -> bool:
        """Send password reset email"""
        template_data = {
            'user_name': user_name,
            'reset_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}",
            'expiry_hours': expiry_hours
        }
        
        return await self.send_template_email(user_email, 'password_reset', template_data)
    
    async def send_system_notification_email(
        self,
        user_email: str,
        user_name: str,
        title: str,
        content: str,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None
    ) -> bool:
        """Send system notification email"""
        template_data = {
            'user_name': user_name,
            'notification_title': title,
            'notification_content': content,
            'action_url': action_url,
            'action_text': action_text
        }
        
        return await self.send_template_email(user_email, 'system_notification', template_data)
    
    async def send_bulk_emails(self, email_list: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Send bulk emails with rate limiting
        """
        results = {'sent': 0, 'failed': 0}
        
        for email_data in email_list:
            try:
                if 'template_name' in email_data:
                    success = await self.send_template_email(
                        to_email=email_data['to_email'],
                        template_name=email_data['template_name'],
                        template_data=email_data.get('template_data', {}),
                        attachments=email_data.get('attachments')
                    )
                else:
                    success = await self.send_email(
                        to_email=email_data['to_email'],
                        subject=email_data['subject'],
                        html_content=email_data['html_content'],
                        text_content=email_data.get('text_content'),
                        attachments=email_data.get('attachments')
                    )
                
                if success:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                
                # Rate limiting - sleep between emails
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Bulk email failed: {str(e)}")
                results['failed'] += 1
        
        return results
    
    async def retry_failed_emails(self, max_retries: int = 3) -> int:
        """
        Retry failed emails
        """
        retried_count = 0
        
        for failed_email in self.failed_emails[:]:  # Copy list for safe iteration
            if failed_email['retry_count'] >= max_retries:
                continue
            
            # Increment retry count
            failed_email['retry_count'] += 1
            
            # Retry sending
            success = await self.send_email(
                to_email=failed_email['to_email'],
                subject=failed_email['subject'],
                html_content=failed_email['html_content'],
                text_content=failed_email['text_content']
            )
            
            if success:
                self.failed_emails.remove(failed_email)
                retried_count += 1
        
        return retried_count
    
    def get_email_stats(self) -> Dict[str, int]:
        """Get email delivery statistics"""
        return {
            'queued': len(self.email_queue),
            'failed': len(self.failed_emails),
            'failed_retryable': len([e for e in self.failed_emails if e['retry_count'] < 3])
        }


# Global email service instance
email_service = EmailService() 