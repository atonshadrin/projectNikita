from app import create_app, db
from app.models import User, Category, News, Comment


def seed():
    """
    Первичная инициализация базы данных демонстрационными данными.

    Скрипт можно запускать повторно: он не создает дубли пользователей и категорий.
    """
    app = create_app()
    with app.app_context():
        # Создаем таблицы, если они еще отсутствуют.
        db.create_all()

        # Администратор
        if not User.query.filter_by(email='admin@news.ru').first():
            admin = User(username='admin', email='admin@news.ru', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.flush()
        else:
            admin = User.query.filter_by(email='admin@news.ru').first()

        # Обычный пользователь
        if not User.query.filter_by(email='user@news.ru').first():
            user = User(username='user', email='user@news.ru', role='user')
            user.set_password('user123')
            db.session.add(user)
            db.session.flush()
        else:
            user = User.query.filter_by(email='user@news.ru').first()

        # Категории
        cats_data = [
            ('Политика', 'politika', '#ef4444', 'fas fa-landmark'),
            ('Экономика', 'ekonomika', '#f59e0b', 'fas fa-chart-line'),
            ('Технологии', 'tekhnologii', '#3b82f6', 'fas fa-microchip'),
            ('Спорт', 'sport', '#22c55e', 'fas fa-football-ball'),
            ('Культура', 'kultura', '#8b5cf6', 'fas fa-theater-masks'),
            ('Наука', 'nauka', '#06b6d4', 'fas fa-flask'),
        ]
        categories = {}
        for name, slug, color, icon in cats_data:
            cat = Category.query.filter_by(slug=slug).first()
            if not cat:
                cat = Category(name=name, slug=slug, color=color, icon=icon)
                db.session.add(cat)
                db.session.flush()
            # Сохраняем объект категории по slug для дальнейшей привязки новостей.
            categories[slug] = cat

        db.session.commit()

        # Пример новостей
        if News.query.count() == 0:
            sample_news = [
                {
                    'title': 'Новые технологии меняют мировую экономику в 2026 году',
                    'slug': 'novye-tekhnologii-menyayut-mirovuyu-ekonomiku-2026',
                    'summary': 'Искусственный интеллект и автоматизация коренным образом трансформируют рынок труда.',
                    'content': '<p>Технологические инновации 2026 года продолжают менять облик мировой экономики. Искусственный интеллект внедряется во все сферы производства и услуг.</p><p>Эксперты отмечают, что страны, вложившие средства в цифровую инфраструктуру, демонстрируют значительный рост ВВП.</p>',
                    'category': 'tekhnologii', 'is_featured': True
                },
                {
                    'title': 'Чемпионат мира по футболу: итоги отборочного этапа',
                    'slug': 'chempionat-mira-futbol-itogi-otbora',
                    'summary': 'Определились все участники финального турнира. Главные сенсации и разочарования.',
                    'content': '<p>Отборочный этап чемпионата мира завершился громкими сенсациями. Ряд фаворитов не смог пробиться в финальную стадию.</p><p>Среди участников — сборные, впервые в истории вышедшие на мировой финал.</p>',
                    'category': 'sport', 'is_featured': True
                },
                {
                    'title': 'Прорыв в квантовых вычислениях: новый рекорд',
                    'slug': 'proryv-kvantovye-vychisleniya-rekord',
                    'summary': 'Учёные установили новый рекорд скорости квантового процессора.',
                    'content': '<p>Международная команда исследователей достигла нового рекорда в области квантовых вычислений, создав процессор из 1000 кубитов.</p>',
                    'category': 'nauka', 'is_featured': True
                },
                {
                    'title': 'Мировые лидеры встретились на саммите по климату',
                    'slug': 'mirovye-lidery-sammit-klimat',
                    'summary': 'На климатическом саммите принято новое соглашение по сокращению выбросов.',
                    'content': '<p>На международном климатическом саммите в Женеве лидеры 120 стран подписали новое соглашение об ускоренном переходе к возобновляемым источникам энергии.</p>',
                    'category': 'politika', 'is_featured': False
                },
                {
                    'title': 'Инфляция в еврозоне достигла минимума за пять лет',
                    'slug': 'inflyaciya-evrozona-minimum-5-let',
                    'summary': 'Европейский центробанк зафиксировал замедление роста цен.',
                    'content': '<p>Инфляция в странах еврозоны снизилась до 1,8% — минимального уровня за последние пять лет, сообщил Европейский центральный банк.</p>',
                    'category': 'ekonomika', 'is_featured': False
                },
                {
                    'title': 'Новый фестиваль кино в Москве собрал рекордную аудиторию',
                    'slug': 'novyy-festival-kino-moskva-rekord',
                    'summary': 'Более 300 тысяч зрителей посетили международный кинофестиваль.',
                    'content': '<p>Московский международный кинофестиваль 2026 года стал самым посещаемым в истории — его программу посмотрели более 300 тысяч зрителей.</p>',
                    'category': 'kultura', 'is_featured': False
                },
            ]
            import random
            for i, data in enumerate(sample_news):
                # Находим категорию по slug и используем ее id в новости.
                cat = categories[data['category']]
                article = News(
                    title=data['title'],
                    slug=data['slug'],
                    summary=data['summary'],
                    content=data['content'],
                    category_id=cat.id,
                    author_id=admin.id,
                    is_published=True,
                    is_featured=data['is_featured'],
                    views_count=random.randint(50, 2000)
                )
                db.session.add(article)
                db.session.flush()

                # Пример комментария
                comment = Comment(
                    content=f'Очень интересная статья! Спасибо за актуальную информацию.',
                    news_id=article.id,
                    user_id=user.id
                )
                db.session.add(comment)

            db.session.commit()

        print('✅ База данных инициализирована!')
        print('👤 Администратор: admin@news.ru / admin123')
        print('👤 Пользователь: user@news.ru / user123')
        print('🌐 Запустите сервер: python run.py')


if __name__ == '__main__':
    seed()
