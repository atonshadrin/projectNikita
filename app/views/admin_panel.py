"""Маршруты административной панели: управление контентом и пользователями."""

import os
import uuid
from functools import wraps

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Category, Comment, News, User

admin_bp = Blueprint('admin_panel', __name__)


def admin_required(f):
    """Декоратор, ограничивающий доступ только администраторам.

    Используется совместно с @login_required:
    - @login_required проверяет, что пользователь вошел в систему;
    - @admin_required проверяет роль пользователя.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Доступ запрещён.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)

    return decorated


def save_image(file):
    """Сохраняет загруженное изображение и возвращает имя файла.

    Почему генерируем UUID-имя:
    - исключаем конфликт одинаковых имен;
    - не зависим от исходного имени файла пользователя.
    """
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)

    file.save(os.path.join(upload_folder, filename))
    return filename


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Главная страница админки со сводной статистикой."""
    news_count = News.query.count()
    users_count = User.query.count()
    comments_count = Comment.query.count()
    categories_count = Category.query.count()

    # Последние новости показываем для быстрого перехода к редактированию.
    latest_news = News.query.order_by(News.published_at.desc()).limit(10).all()

    return render_template(
        'admin/dashboard.html',
        news_count=news_count,
        users_count=users_count,
        comments_count=comments_count,
        categories_count=categories_count,
        latest_news=latest_news,
    )


@admin_bp.route('/news')
@login_required
@admin_required
def news_list():
    """Список новостей в админке с пагинацией."""
    page = request.args.get('page', 1, type=int)
    news = News.query.order_by(News.published_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/news_list.html', news=news)


@admin_bp.route('/news/create', methods=['GET', 'POST'])
@login_required
@admin_required
def news_create():
    """Создает новую новость через форму админки."""
    categories = Category.query.all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        summary = request.form.get('summary', '').strip()
        category_id = request.form.get('category_id', type=int)
        is_published = request.form.get('is_published') == 'on'
        is_featured = request.form.get('is_featured') == 'on'

        # Минимальная серверная валидация обязательных полей.
        if not title or not content or not category_id:
            flash('Заполните обязательные поля.', 'danger')
            return render_template('admin/news_form.html', categories=categories)

        # Генерируем человекочитаемый и уникальный slug для URL.
        slug = generate_slug(title)

        image_filename = None
        if 'image' in request.files and request.files['image'].filename:
            image_filename = save_image(request.files['image'])

        article = News(
            title=title,
            slug=slug,
            content=content,
            summary=summary,
            category_id=category_id,
            author_id=current_user.id,
            is_published=is_published,
            is_featured=is_featured,
            image=image_filename,
        )
        db.session.add(article)
        db.session.commit()

        flash('Новость создана.', 'success')
        return redirect(url_for('admin_panel.news_list'))

    return render_template('admin/news_form.html', categories=categories, article=None)


@admin_bp.route('/news/<int:news_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def news_edit(news_id):
    """Редактирует существующую новость."""
    article = News.query.get_or_404(news_id)
    categories = Category.query.all()

    if request.method == 'POST':
        article.title = request.form.get('title', '').strip()
        article.content = request.form.get('content', '').strip()
        article.summary = request.form.get('summary', '').strip()
        article.category_id = request.form.get('category_id', type=int)
        article.is_published = request.form.get('is_published') == 'on'
        article.is_featured = request.form.get('is_featured') == 'on'

        if 'image' in request.files and request.files['image'].filename:
            article.image = save_image(request.files['image'])

        db.session.commit()
        flash('Новость обновлена.', 'success')
        return redirect(url_for('admin_panel.news_list'))

    return render_template('admin/news_form.html', categories=categories, article=article)


@admin_bp.route('/news/<int:news_id>/delete', methods=['POST'])
@login_required
@admin_required
def news_delete(news_id):
    """Удаляет новость по идентификатору."""
    article = News.query.get_or_404(news_id)
    db.session.delete(article)
    db.session.commit()
    flash('Новость удалена.', 'success')
    return redirect(url_for('admin_panel.news_list'))


@admin_bp.route('/categories')
@login_required
@admin_required
def categories_list():
    """Список категорий."""
    cats = Category.query.all()
    return render_template('admin/categories.html', categories=cats)


@admin_bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
@admin_required
def category_create():
    """Создает новую категорию."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        color = request.form.get('color', '#3b82f6')
        icon = request.form.get('icon', 'fas fa-tag')

        if not name:
            flash('Введите название.', 'danger')
        else:
            cat = Category(name=name, slug=generate_slug(name), color=color, icon=icon)
            db.session.add(cat)
            db.session.commit()
            flash('Категория создана.', 'success')
            return redirect(url_for('admin_panel.categories_list'))

    return render_template('admin/category_form.html', category=None)


@admin_bp.route('/categories/<int:cat_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def category_edit(cat_id):
    """Редактирует существующую категорию."""
    cat = Category.query.get_or_404(cat_id)

    if request.method == 'POST':
        cat.name = request.form.get('name', '').strip()
        cat.color = request.form.get('color', '#3b82f6')
        cat.icon = request.form.get('icon', 'fas fa-tag')
        db.session.commit()

        flash('Категория обновлена.', 'success')
        return redirect(url_for('admin_panel.categories_list'))

    return render_template('admin/category_form.html', category=cat)


@admin_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
@login_required
@admin_required
def category_delete(cat_id):
    """Удаляет категорию."""
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Категория удалена.', 'success')
    return redirect(url_for('admin_panel.categories_list'))


@admin_bp.route('/comments')
@login_required
@admin_required
def comments_list():
    """Список комментариев для модерации."""
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.order_by(Comment.created_at.desc()).paginate(page=page, per_page=30)
    return render_template('admin/comments.html', comments=comments)


@admin_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
@admin_required
def comment_delete(comment_id):
    """Удаляет комментарий."""
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Комментарий удалён.', 'success')
    return redirect(url_for('admin_panel.comments_list'))


@admin_bp.route('/users')
@login_required
@admin_required
def users_list():
    """Список пользователей для управления аккаунтами."""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-role', methods=['POST'])
@login_required
@admin_required
def user_toggle_role(user_id):
    """Переключает роль пользователя между user и admin."""
    user = User.query.get_or_404(user_id)

    # Защита от случайного лишения админ-прав самого себя.
    if user.id == current_user.id:
        flash('Нельзя изменить собственную роль.', 'warning')
    else:
        user.role = 'user' if user.role == 'admin' else 'admin'
        db.session.commit()
        flash(f'Роль {user.username} изменена.', 'success')

    return redirect(url_for('admin_panel.users_list'))


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def user_toggle_active(user_id):
    """Активирует/деактивирует пользователя."""
    user = User.query.get_or_404(user_id)

    # Нельзя деактивировать самого себя, чтобы не потерять доступ к админке.
    if user.id == current_user.id:
        flash('Нельзя деактивировать собственный аккаунт.', 'warning')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        flash(f'Статус {user.username} изменён.', 'success')

    return redirect(url_for('admin_panel.users_list'))


def generate_slug(text):
    """Преобразует произвольный текст в уникальный URL-slug.

    Алгоритм:
    1. Пытаемся транслитерировать кириллицу в латиницу.
    2. Удаляем служебные символы.
    3. Заменяем пробелы/подчеркивания на дефисы.
    4. При конфликте добавляем суффикс -1, -2, ...
    """
    import re
    from transliterate import translit

    try:
        text = translit(text, 'ru', reversed=True)
    except Exception:
        # Если транслитерация недоступна, используем исходный текст.
        pass

    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')

    base_slug = slug
    counter = 1

    # Проверяем уникальность slug сразу для двух сущностей: News и Category.
    while News.query.filter_by(slug=slug).first() or Category.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug
