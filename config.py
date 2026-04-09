import os


class Config:
    # В продакшене секреты должны задаваться через переменные окружения.
    # Если переменная не задана, используется dev-значение по умолчанию.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    # По умолчанию используется локальная SQLite-база для быстрого старта.
    # При деплое можно подменить на Postgres/MySQL через DATABASE_URL.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///news.db')
    # Отключаем трекинг изменений объектов SQLAlchemy ради экономии памяти.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Папка для изображений, загружаемых через админку.
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'img', 'uploads')
    # Ограничение размера запроса при загрузке файлов.
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 МБ
    # Разрешенные расширения изображений.
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    # Размер страницы в списках новостей (можно использовать в пагинации).
    NEWS_PER_PAGE = 10
