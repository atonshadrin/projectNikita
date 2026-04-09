"""Маршруты публичной части сайта: главная и страницы категорий."""

from flask import Blueprint, render_template, request

from app.models import Category, Comment, News

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Рендерит главную страницу портала.

    На главной выводятся несколько независимых блоков:
    - избранные новости для верхнего слайдера;
    - последние новости по дате публикации;
    - популярные новости по числу просмотров;
    - последние одобренные комментарии;
    - список категорий для меню/сайдбара.
    """
    # Отдельные запросы упрощают управление блоками и позволяют независимо
    # менять лимиты/сортировку каждого раздела.
    featured_news = (
        News.query
        .filter_by(is_published=True, is_featured=True)
        .order_by(News.published_at.desc())
        .limit(5)
        .all()
    )
    latest_news = (
        News.query
        .filter_by(is_published=True)
        .order_by(News.published_at.desc())
        .limit(8)
        .all()
    )
    popular_news = (
        News.query
        .filter_by(is_published=True)
        .order_by(News.views_count.desc())
        .limit(5)
        .all()
    )
    latest_comments = (
        Comment.query
        .filter_by(is_approved=True)
        .order_by(Comment.created_at.desc())
        .limit(5)
        .all()
    )
    categories = Category.query.all()

    return render_template(
        'index.html',
        featured_news=featured_news,
        latest_news=latest_news,
        popular_news=popular_news,
        latest_comments=latest_comments,
        categories=categories,
    )


@main_bp.route('/category/<slug>')
def category(slug):
    """Рендерит страницу конкретной категории с пагинацией."""
    # Если категория не найдена, Flask автоматически вернет 404.
    cat = Category.query.filter_by(slug=slug).first_or_404()

    # Берем номер страницы из query-параметра. По умолчанию это первая страница.
    page = request.args.get('page', 1, type=int)

    # Показываем только опубликованные новости выбранной категории.
    news_list = (
        News.query
        .filter_by(category_id=cat.id, is_published=True)
        .order_by(News.published_at.desc())
        .paginate(page=page, per_page=10)
    )
    categories = Category.query.all()

    return render_template(
        'category.html',
        category=cat,
        news_list=news_list,
        categories=categories,
    )
