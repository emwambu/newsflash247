import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, render_template_string
from models import EmailLog, NewsSubscriber
from app import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_email(to_email, subject, html_content, email_type='general'):
        """Send email using SMTP"""
        try:
            # Create email log entry
            email_log = EmailLog(
                recipient_email=to_email,
                subject=subject,
                email_type=email_type,
                status='pending'
            )
            db.session.add(email_log)
            db.session.commit()
            
            # Check if email credentials are configured
            if not current_app.config.get('MAIL_USERNAME') or not current_app.config.get('MAIL_PASSWORD'):
                email_log.status = 'failed'
                email_log.error_message = 'Email credentials not configured'
                db.session.commit()
                logger.warning(f"Email credentials not configured for {to_email}")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
            msg['To'] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
                server.starttls()
                server.login(
                    current_app.config['MAIL_USERNAME'],
                    current_app.config['MAIL_PASSWORD']
                )
                server.send_message(msg)
            
            # Update log as sent
            email_log.status = 'sent'
            email_log.sent_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            # Update log as failed
            if 'email_log' in locals():
                email_log.status = 'failed'
                email_log.error_message = str(e)
                db.session.commit()
            
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def send_welcome_email(email):
        """Send welcome email to new subscriber"""
        subject = "Welcome to NewsFlash247 Newsletter!"
        
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #0d6efd, #0056b3); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">📰 Welcome to NewsFlash247!</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">Your trusted source for breaking news</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                <h2 style="color: #333; margin-top: 0;">Thank you for subscribing!</h2>
                <p style="color: #666; line-height: 1.6;">
                    We're excited to have you join our community of informed readers. You'll receive:
                </p>
                
                <ul style="color: #666; line-height: 1.8;">
                    <li>📰 Daily news digest with the most important stories</li>
                    <li>⚡ Breaking news alerts for urgent updates</li>
                    <li>📊 Weekly news roundup and analysis</li>
                    <li>🎯 Personalized content based on your interests</li>
                </ul>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #0d6efd;">
                    <h3 style="color: #0d6efd; margin-top: 0;">What's Next?</h3>
                    <p style="color: #666; margin-bottom: 0;">
                        Keep an eye on your inbox for our latest news updates. We promise to deliver only high-quality, 
                        relevant content that keeps you informed about what matters most.
                    </p>
                </div>
                
                <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    Best regards,<br>
                    <strong>The NewsFlash247 Team</strong>
                </p>
                
                <hr style="border: none; border-top: 1px solid #dee2e6; margin: 20px 0;">
                
                <p style="color: #999; font-size: 12px; text-align: center;">
                    If you didn't subscribe to this newsletter, you can safely ignore this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(email, subject, html_content, 'welcome')
    
    @staticmethod
    def generate_subscription_token():
        """Generate a unique subscription token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def subscribe_email(email):
        """Subscribe email to newsletter"""
        try:
            # Check if already subscribed
            existing = NewsSubscriber.query.filter_by(email=email).first()
            if existing:
                if existing.is_active:
                    return False, "Email already subscribed"
                else:
                    # Reactivate subscription
                    existing.is_active = True
                    existing.subscribed_at = datetime.utcnow()
                    db.session.commit()
                    EmailService.send_welcome_email(email)
                    return True, "Subscription reactivated"
            
            # Create new subscription
            token = EmailService.generate_subscription_token()
            subscriber = NewsSubscriber(
                email=email,
                subscription_token=token
            )
            db.session.add(subscriber)
            db.session.commit()
            
            # Send welcome email
            EmailService.send_welcome_email(email)
            
            return True, "Successfully subscribed"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to subscribe {email}: {str(e)}")
            return False, "Failed to subscribe"
    
    @staticmethod
    def send_newsletter(articles, test_email=None):
        """Send newsletter to all active subscribers"""
        if not articles:
            return 0, "No articles to send"
        
        # Get recipients
        if test_email:
            recipients = [test_email]
        else:
            subscribers = NewsSubscriber.query.filter_by(is_active=True).all()
            recipients = [sub.email for sub in subscribers]
        
        if not recipients:
            return 0, "No active subscribers"
        
        # Create newsletter content
        subject = f"NewsFlash247 Daily Digest - {datetime.now().strftime('%B %d, %Y')}"
        
        html_content = EmailService.create_newsletter_html(articles)
        
        # Send emails
        sent_count = 0
        for email in recipients:
            if EmailService.send_email(email, subject, html_content, 'newsletter'):
                sent_count += 1
                
                # Update subscriber stats
                if not test_email:
                    subscriber = NewsSubscriber.query.filter_by(email=email).first()
                    if subscriber:
                        subscriber.last_email_sent = datetime.utcnow()
                        subscriber.email_count += 1
        
        if not test_email:
            db.session.commit()
        
        return sent_count, f"Newsletter sent to {sent_count} recipients"
    
    @staticmethod
    def create_newsletter_html(articles):
        """Create HTML content for newsletter"""
        html_template = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
            <div style="background: linear-gradient(135deg, #0d6efd, #0056b3); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">📰 NewsFlash247</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">Daily News Digest - {{ date }}</p>
            </div>
            
            <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px;">
                <h2 style="color: #333; margin-top: 0; border-bottom: 2px solid #0d6efd; padding-bottom: 10px;">
                    Today's Top Stories
                </h2>
                
                {% for article in articles %}
                <div style="margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #dee2e6;">
                    {% if article.is_breaking %}
                    <div style="background: #dc3545; color: white; padding: 5px 10px; border-radius: 15px; display: inline-block; font-size: 12px; font-weight: bold; margin-bottom: 10px;">
                        🚨 BREAKING NEWS
                    </div>
                    {% endif %}
                    
                    <h3 style="color: #0d6efd; margin: 10px 0; font-size: 18px; line-height: 1.4;">
                        {{ article.title }}
                    </h3>
                    
                    <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #0d6efd; margin: 15px 0;">
                        <p style="color: #666; margin: 0; line-height: 1.6;">
                            {{ article.summary or article.content[:200] + '...' }}
                        </p>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px;">
                        <small style="color: #999;">
                            📂 {{ article.category }} | 👁️ {{ article.views_count }} views | ⏱️ {{ article.reading_time }} min read
                        </small>
                        <small style="color: #999;">
                            {{ article.created_at.strftime('%B %d, %Y at %I:%M %p') }}
                        </small>
                    </div>
                </div>
                {% endfor %}
                
                <div style="background: #0d6efd; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-top: 30px;">
                    <h3 style="margin: 0 0 10px 0;">Stay Connected</h3>
                    <p style="margin: 0; font-size: 14px;">
                        Visit NewsFlash247 for more breaking news and updates throughout the day.
                    </p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px; text-align: center;">
                    You're receiving this email because you subscribed to NewsFlash247 newsletter.<br>
                    © 2025 NewsFlash247. All rights reserved.
                </p>
            </div>
        </body>
        </html>
        """
        
        from jinja2 import Template
        template = Template(html_template)
        return template.render(
            articles=articles,
            date=datetime.now().strftime('%B %d, %Y')
        )