from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from .content_detector import ContentFilter
import os

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = '12345678'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/kopo'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['GEMINI_API_KEY'] = 'YOUR_API_KEY'
    
    # 로그 디렉토리 생성
    if not os.path.exists('logs'):
        os.makedirs('logs')
   
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
   
    login_manager.login_view = 'login'
    login_manager.login_message = '이 페이지에 접근하려면 로그인이 필요합니다.'

    # ContentFilter 초기화
    global content_detector
    content_detector = ContentFilter(
        json_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'merged_toxic_data.json'),
        api_key=app.config['GEMINI_API_KEY']
    )
   
    with app.app_context():
        from app import routes
        routes.init_routes(app)
   
    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))