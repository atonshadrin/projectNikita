from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Глобальные расширения объявляются здесь, а инициализируются внутри create_app().
# Такой подход удобен для тестов и разных конфигураций запуска.
db = SQLAlchemy()
login_manager = LoginManager()

# Настройки поведения Flask-Login для неавторизованных пользователей.
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
login_manager.login_message_category = 'warning'


def create_app(config=None):
    """Создает и настраивает экземпляр Flask-приложения.

    Последовательность инициализации:
    1. Создаем объект Flask.
    2. Загружаем конфигурацию.
    3. Подключаем расширения (SQLAlchemy, Flask-Login).
    4. Регистрируем blueprints для маршрутов.
    """
    app = Flask(__name__)

    if config is None:
        # Базовый сценарий: используем конфигурацию проекта из config.py.
        from config import Config
        app.config.from_object(Config)
    else:
        # Кастомная конфигурация (например, тестовая) передается извне.
        app.config.from_object(config)

    # Привязка расширений к текущему экземпляру приложения.
    db.init_app(app)
    login_manager.init_app(app)

    # Маршруты разбиты на функциональные области для удобства поддержки.
    from app.views.admin_panel import admin_bp
    from app.views.auth import auth_bp
    from app.views.main import main_bp
    from app.views.news import news_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(news_bp, url_prefix='/news')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
