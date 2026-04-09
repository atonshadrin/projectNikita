"""Маршруты аутентификации: вход, регистрация и выход."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Обрабатывает авторизацию пользователя по email и паролю."""
    # Если пользователь уже вошел в систему, повторный вход не нужен.
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # Нормализуем ввод: убираем пробелы у email, пароль оставляем как есть.
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        # Ищем пользователя по email и проверяем пароль/активность аккаунта.
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)

            # Если пользователь пришел на защищенную страницу, Flask-Login
            # передает ее адрес в параметре next.
            next_page = request.args.get('next')
            flash('Добро пожаловать!', 'success')
            return redirect(next_page or url_for('main.index'))

        flash('Неверный email или пароль.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Создает нового пользователя и сразу авторизует его."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')

        # Базовая валидация формы регистрации.
        if not username or not email or not password:
            flash('Все поля обязательны.', 'danger')
        elif password != password2:
            flash('Пароли не совпадают.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Имя пользователя занято.', 'danger')
        else:
            user = User(username=username, email=email)

            # В модели пароль сохраняется в виде хэша, а не в открытом виде.
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            # После успешной регистрации сразу выполняем вход.
            login_user(user)
            flash('Регистрация прошла успешно!', 'success')
            return redirect(url_for('main.index'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Завершает пользовательскую сессию."""
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('main.index'))
