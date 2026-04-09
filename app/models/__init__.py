"""SQLAlchemy-модели проекта: пользователи, новости, категории и взаимодействия."""

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager


class User(UserMixin, db.Model):
    """Пользователь системы.

    Поддерживает:
    - аутентификацию через Flask-Login;
    - роли (обычный пользователь/администратор);
    - связи с комментариями, лайками и новостями автора.
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')  # Роль пользователя: 'admin' или 'user'
    avatar = db.Column(db.String(256), default='default_avatar.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # lazy='dynamic' возвращает query-объект, что удобно для фильтрации/подсчетов.
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Сохраняет хэш пароля вместо исходной строки."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверяет введенный пароль по сохраненному хэшу."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """Флаг административной роли для проверок доступа."""
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Колбэк Flask-Login: загружает пользователя по id из сессии."""
    return User.query.get(int(user_id))


class Category(db.Model):
    """Категория новостей (например, политика, спорт, технологии)."""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    color = db.Column(db.String(20), default='#3b82f6')
    icon = db.Column(db.String(64), default='fas fa-tag')

    # Одна категория -> много новостей.
    news = db.relationship('News', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


class News(db.Model):
    """Новостная статья."""

    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    slug = db.Column(db.String(256), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(512))
    image = db.Column(db.String(256))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)

    # Автор хранится отдельной связью для удобного доступа в шаблонах.
    author = db.relationship('User', backref='news_posts')
    comments = db.relationship('Comment', backref='news', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='news', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def likes_count(self):
        """Возвращает текущее количество лайков у статьи."""
        return self.likes.count()

    @property
    def comments_count(self):
        """Считает только одобренные комментарии."""
        return self.comments.filter_by(is_approved=True).count()

    def __repr__(self):
        return f'<News {self.title}>'


class Comment(db.Model):
    """Комментарий пользователя к новости."""

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Comment {self.id}>'


class Like(db.Model):
    """Лайк пользователя для новости."""

    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Запрещаем повторный лайк одной и той же новости одним пользователем.
    __table_args__ = (db.UniqueConstraint('news_id', 'user_id', name='_news_user_like'),)

    def __repr__(self):
        return f'<Like news={self.news_id} user={self.user_id}>'
