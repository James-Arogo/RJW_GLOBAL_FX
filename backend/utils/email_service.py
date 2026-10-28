import os
import secrets
from datetime import datetime, timedelta
from flask import current_app, url_for
from flask_mail import Message, Mail
import jwt


class EmailService:
    """Email service for user verification and password reset."""
    
    def __init__(self, app=None):
        self.mail = Mail()
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize email service with Flask app."""
        self.mail.init_app(app)
    
    def generate_verification_token(self, user_id):
        """Generate email verification token."""
        payload = {
            'user_id': user_id,
            'type': 'email_verification',
            'exp': datetime.utcnow() + timedelta(hours=current_app.config['EMAIL_VERIFICATION_EXPIRE_HOURS'])
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    def generate_password_reset_token(self, user_id):
        """Generate password reset token."""
        payload = {
            'user_id': user_id,
            'type': 'password_reset',
            'exp': datetime.utcnow() + timedelta(hours=current_app.config['PASSWORD_RESET_EXPIRE_HOURS'])
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    def verify_token(self, token, token_type):
        """Verify and decode token."""
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            
            if payload.get('type') != token_type:
                return None
            
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                return None
            
            return payload['user_id']
        except jwt.InvalidTokenError:
            return None
    
    def send_verification_email(self, user_email, verification_token):
        """Send email verification email."""
        try:
            verification_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={verification_token}"
            
            msg = Message(
                subject='Verify Your RJW GLOBAL FX Account',
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[user_email]
            )
            
            msg.body = f"""
            Hello,
            
            Thank you for registering with RJW GLOBAL FX!
            
            Please click the link below to verify your email address:
            {verification_url}
            
            This link will expire in {current_app.config['EMAIL_VERIFICATION_EXPIRE_HOURS']} hours.
            
            If you did not create an account, please ignore this email.
            
            Best regards,
            RJW GLOBAL FX Team
            """
            
            msg.html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2c3e50;">Verify Your RJW GLOBAL FX Account</h2>
                <p>Hello,</p>
                <p>Thank you for registering with RJW GLOBAL FX!</p>
                <p>Please click the button below to verify your email address:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background-color: #3498db; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Verify Email Address
                    </a>
                </div>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #7f8c8d;">{verification_url}</p>
                <p><strong>Note:</strong> This link will expire in {current_app.config['EMAIL_VERIFICATION_EXPIRE_HOURS']} hours.</p>
                <p>If you did not create an account, please ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
                <p style="color: #7f8c8d; font-size: 12px;">
                    Best regards,<br>
                    RJW GLOBAL FX Team
                </p>
            </div>
            """
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send verification email: {str(e)}")
            return False
    
    def send_password_reset_email(self, user_email, reset_token):
        """Send password reset email."""
        try:
            reset_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
            
            msg = Message(
                subject='Reset Your RJW GLOBAL FX Password',
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[user_email]
            )
            
            msg.body = f"""
            Hello,
            
            We received a request to reset your password for your RJW GLOBAL FX account.
            
            Please click the link below to reset your password:
            {reset_url}
            
            This link will expire in {current_app.config['PASSWORD_RESET_EXPIRE_HOURS']} hour(s).
            
            If you did not request a password reset, please ignore this email.
            
            Best regards,
            RJW GLOBAL FX Team
            """
            
            msg.html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #e74c3c;">Reset Your RJW GLOBAL FX Password</h2>
                <p>Hello,</p>
                <p>We received a request to reset your password for your RJW GLOBAL FX account.</p>
                <p>Please click the button below to reset your password:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #e74c3c; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #7f8c8d;">{reset_url}</p>
                <p><strong>Note:</strong> This link will expire in {current_app.config['PASSWORD_RESET_EXPIRE_HOURS']} hour(s).</p>
                <p>If you did not request a password reset, please ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
                <p style="color: #7f8c8d; font-size: 12px;">
                    Best regards,<br>
                    RJW GLOBAL FX Team
                </p>
            </div>
            """
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send password reset email: {str(e)}")
            return False
    
    def send_welcome_email(self, user_email, username):
        """Send welcome email after successful registration."""
        try:
            msg = Message(
                subject='Welcome to RJW GLOBAL FX!',
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[user_email]
            )
            
            msg.body = f"""
            Hello {username},
            
            Welcome to RJW GLOBAL FX! Your account has been successfully created.
            
            You can now:
            - Access live forex market prices
            - Execute simulated trades
            - Track your portfolio performance
            - Use advanced trading features
            
            Log in to your account at: {current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/login
            
            If you have any questions, please don't hesitate to contact our support team.
            
            Best regards,
            RJW GLOBAL FX Team
            """
            
            msg.html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #27ae60;">Welcome to RJW GLOBAL FX!</h2>
                <p>Hello {username},</p>
                <p>Welcome to RJW GLOBAL FX! Your account has been successfully created.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #2c3e50; margin-top: 0;">What you can do now:</h3>
                    <ul style="color: #34495e;">
                        <li>Access live forex market prices</li>
                        <li>Execute simulated trades</li>
                        <li>Track your portfolio performance</li>
                        <li>Use advanced trading features</li>
                        <li>Set up limit orders and stop-loss</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/login" 
                       style="background-color: #27ae60; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Log In to Your Account
                    </a>
                </div>
                
                <p>If you have any questions, please don't hesitate to contact our support team.</p>
                
                <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
                <p style="color: #7f8c8d; font-size: 12px;">
                    Best regards,<br>
                    RJW GLOBAL FX Team
                </p>
            </div>
            """
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send welcome email: {str(e)}")
            return False
    
    def send_trade_notification(self, user_email, trade_details):
        """Send trade execution notification."""
        try:
            msg = Message(
                subject=f'Trade Executed: {trade_details["pair"]}',
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[user_email]
            )
            
            result_color = '#27ae60' if trade_details['result'] == 'win' else '#e74c3c'
            
            msg.html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: {result_color};">Trade Executed Successfully</h2>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Currency Pair:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{trade_details['pair']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Amount:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">${trade_details['amount']:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Result:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6; color: {result_color}; text-transform: capitalize;">{trade_details['result']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Profit/Loss:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6; color: {result_color};">${trade_details['profit_loss']:,.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px;"><strong>New Balance:</strong></td>
                            <td style="padding: 8px;">${trade_details['balance']:,.2f}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/dashboard" 
                       style="background-color: #3498db; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Your Dashboard
                    </a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 30px 0;">
                <p style="color: #7f8c8d; font-size: 12px;">
                    This is an automated notification from RJW GLOBAL FX.<br>
                    You can disable email notifications in your account settings.
                </p>
            </div>
            """
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send trade notification: {str(e)}")
            return False


# Global email service instance
email_service = EmailService()
