import os
from flask import Flask
from flask_login import LoginManager
from app.models import db, User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'krishisahay-secret-key-12345')
    
    # Locate database in the instance folder
    instance_path = os.path.join(app.root_path, '..', 'instance')
    os.makedirs(instance_path, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(instance_path, 'krishisahay.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure uploads
    upload_path = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_path, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_path
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB limit
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.schemes import schemes_bp
    from app.routes.upload import upload_bp
    from app.routes.admin import admin_bp
    from app.routes.chatbot import chatbot_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(schemes_bp, url_prefix='/schemes')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(chatbot_bp)
    
    return app
