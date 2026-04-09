"""Маршруты просмотра новости, комментариев и лайков."""

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app import db
from app.models import Category, Comment, Like, News

news_bp = Blueprint('news', __name__)


def allowed_file(filename):
    """Проверяет, что расширение файла входит в список разрешенных.

    Функция используется как служебная валидация для загрузки изображений.
    """
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    )


@news_bp.route('/<slug>')
def detail(slug):
    """Отображает страницу новости и увеличивает счетчик просмотров."""
    # Неопубликованные материалы не выдаем в публичной части.
    article = News.query.filter_by(slug=slug, is_published=True).first_or_404()

    # Счетчик просмотров фиксируем сразу после успешного открытия новости.
    article.views_count += 1
    db.session.commit()

    # Показываем только одобренные комментарии, в хронологическом порядке.
    comments = (
        Comment.query
        .filter_by(news_id=article.id, is_approved=True)
        .order_by(Comment.created_at.asc())
        .all()
    )

    # Флаг для состояния кнопки лайка в интерфейсе.
    user_liked = False
    if current_user.is_authenticated:
        user_liked = (
            Like.query.filter_by(news_id=article.id, user_id=current_user.id).first()
            is not None
        )

    # Подбираем похожие статьи из той же категории, кроме текущей.
    related = (
        News.query
        .filter_by(category_id=article.category_id, is_published=True)
        .filter(News.id != article.id)
        .order_by(News.published_at.desc())
        .limit(4)
        .all()
    )
    categories = Category.query.all()

    return render_template(
        'news/detail.html',
        article=article,
        comments=comments,
        user_liked=user_liked,
        related=related,
        categories=categories,
    )


@news_bp.route('/<slug>/comment', methods=['POST'])
@login_required
def add_comment(slug):
    """Добавляет комментарий текущего пользователя к новости."""
    article = News.query.filter_by(slug=slug, is_published=True).first_or_404()
    content = request.form.get('content', '').strip()

    if not content:
        flash('Комментарий не может быть пустым.', 'danger')
    else:
        comment = Comment(content=content, news_id=article.id, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен.', 'success')

    # Возвращаем пользователя к блоку комментариев на странице новости.
    return redirect(url_for('news.detail', slug=slug) + '#comments')


@news_bp.route('/<int:news_id>/like', methods=['POST'])
@login_required
def toggle_like(news_id):
    """Ставит или снимает лайк с новости (переключатель)."""
    article = News.query.get_or_404(news_id)

    # Проверяем, есть ли лайк текущего пользователя на эту новость.
    existing = Like.query.filter_by(news_id=news_id, user_id=current_user.id).first()
    if existing:
        db.session.delete(existing)
        liked = False
    else:
        db.session.add(Like(news_id=news_id, user_id=current_user.id))
        liked = True

    db.session.commit()

    # Возвращаем JSON для обновления интерфейса без полной перезагрузки страницы.
    return jsonify({'liked': liked, 'count': article.likes_count})
