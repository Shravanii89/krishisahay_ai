from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    full_name = db.Column(db.String(128), nullable=False)
    farmer_id = db.Column(db.String(64), unique=True, nullable=True)
    age = db.Column(db.Integer, nullable=False)
    mobile_number = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=True)
    state = db.Column(db.String(64), nullable=False)
    district = db.Column(db.String(64), nullable=False)
    village = db.Column(db.String(64), nullable=False)
    land_size = db.Column(db.Float, nullable=False) # in hectares
    crop_type = db.Column(db.String(256), nullable=False) # comma-separated list of crops grown
    annual_income = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(64), nullable=False, default="General") # General, SC, ST, OBC
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to document uploads
    uploads = db.relationship('DocumentUpload', backref='farmer', lazy=True)
    # Relationship to chat history
    chat_history = db.relationship('ChatHistory', backref='farmer', lazy=True, order_by='ChatHistory.timestamp')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_crops_list(self):
        if not self.crop_type:
            return []
        return [c.strip() for c in self.crop_type.split(',') if c.strip()]

    def __repr__(self):
        return f'<User {self.username}>'


class Scheme(db.Model):
    __tablename__ = 'schemes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(64), nullable=False) # Financial, Insurance, Irrigation, Equipment, etc.
    state_specific = db.Column(db.String(64), nullable=True) # "All" or State Name
    
    # Eligibility requirements
    target_category = db.Column(db.String(64), nullable=True) # e.g. "SC/ST", "Women", "Small/Marginal", "All"
    min_age = db.Column(db.Integer, default=0)
    max_land_size = db.Column(db.Float, nullable=True) # in hectares
    max_income = db.Column(db.Float, nullable=True) # in Rupees
    required_crops = db.Column(db.String(256), nullable=True) # comma-separated, optional
    
    # Scheme details
    benefits = db.Column(db.Text, nullable=False) # description of benefits
    required_documents = db.Column(db.Text, nullable=False) # newline/comma-separated documents needed
    application_steps = db.Column(db.Text, nullable=False) # step by step guide
    official_link = db.Column(db.String(256), nullable=True)
    
    def get_crops_list(self):
        if not self.required_crops:
            return []
        return [c.strip().lower() for c in self.required_crops.split(',') if c.strip()]

    def get_documents_list(self):
        if not self.required_documents:
            return []
        return [d.strip() for d in self.required_documents.split('\n') if d.strip()]

    def get_steps_list(self):
        if not self.application_steps:
            return []
        return [s.strip() for s in self.application_steps.split('\n') if s.strip()]

    def __repr__(self):
        return f'<Scheme {self.name}>'


class DocumentUpload(db.Model):
    __tablename__ = 'document_uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(256), nullable=False)
    file_type = db.Column(db.String(32), nullable=False) # "image", "audio", "video", "text"
    ai_status = db.Column(db.String(32), default="Pending") # "Pending", "Completed", "Failed"
    ai_result = db.Column(db.Text, nullable=True) # Mock JSON response of Gemini output
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DocumentUpload {self.file_path}>'


class ChatHistory(db.Model):
    __tablename__ = 'chat_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_bot = db.Column(db.Boolean, default=False)  # False = user, True = bot
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        sender = 'Bot' if self.is_bot else 'User'
        return f'<ChatHistory [{sender}] {self.message[:40]}>'
