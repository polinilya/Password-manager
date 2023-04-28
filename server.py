from flask import Flask, url_for, render_template, redirect, make_response, request, session, abort, send_file
from data_ORM import db_session
from data_ORM.users import User
from data_ORM.passwords import Password
import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms_ORM.user2 import LoginForm
from forms_ORM.user import RegisterForm
from forms_ORM.passwords import PasswordForm
import csv
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

'''Для верной работы flask-login у нас должна быть функция
 для получения пользователя, украшенная декоратором login_manager.user_loader.
  Добавим ее:'''


def main():
    db_session.global_init("db_ORM/password_db.db")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


'''Теперь добавим обработчик адреса /logout. 
Для него нам не понадобится отдельный шаблон, 
поскольку это не отдельная страница, а действие.'''


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login_ORM.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login_ORM.html', title='Авторизация', form=form)


'''Давайте добавим небольшое изменение в главную страницу нашего 
приложения, чтобы для авторизованного пользователя 
отображались и его личные записи.'''


@app.route("/")
def index():
    db_sess = db_session.create_session()
    # news = db_sess.query(News).filter(News.is_private != False)
    # if current_user.is_authenticated:
    # news = db_sess.query(News).filter(
    # (News.user == current_user) | (News.is_private != True))
    # else:
    # news = db_sess.query(News).filter(News.is_private != True)
    if current_user.is_authenticated:
        news = db_sess.query(Password).filter(Password.user == current_user)
    else:
        news = db_sess.query(Password).filter(Password.is_private == False)
    return render_template("index_ORM.html", news=news)


'''Добавим обработчик для добавление нововсти'''


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = PasswordForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = Password()
        news.email = form.email.data
        news.site_url = form.site_url.data
        news.site_password = form.site_password.data
        current_user.passwords.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


'''А теперь напишем обработчик для редакции новостей. Будем создавать, уже
написанный news.py и news.html'''


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = PasswordForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(Password).filter(Password.id == id,
                                              Password.user == current_user
                                              ).first()
        if news:
            form.email.data = news.email
            form.site_url.data = news.site_url
            form.site_password.data = news.site_password
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(Password).filter(Password.id == id,
                                              Password.user == current_user
                                              ).first()
        if news:
            news.email = form.email.data
            news.site_url = form.site_url.data
            news.site_password = form.site_password.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование пароля',
                           form=form
                           )


'''Если мы запросили страницу записи, ищем ее в базе по id, 
причем автор новости должен совпадать с текущим пользователем. 
Если что-то нашли, предзаполняем форму, иначе показываем пользователю страницу 404. 
Такую же проверку на всякий случай делаем перед изменением новости.

Добавим кнопки «Изменить» и «Удалить» к каждой новости в списке новостей, 
но только для тех записей, автором которых является current_user. 
Немного изменим шаблон index.html.'''


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(Password).filter(Password.id == id,
                                          Password.user == current_user
                                          ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


'''Добавим еще обработчик удаления записи. Он сверху'''


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_ORM.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register_ORM.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register_ORM.html', title='Регистрация', form=form)


@app.route('/export')
def export_data():
    db_sess = db_session.create_session()
    with open('save.csv', 'w') as f:
        out = csv.writer(f)
        out.writerow(['id', 'email', 'site_url', 'site_password'])
        for item in db_sess.query(Password).filter(Password.user == current_user):
            out.writerow([item.id, item.email, item.site_url, item.site_password])
    return send_file('save.csv',
                     mimetype='text/csv',
                     download_name=f"Экспортированный_Пароль_{datetime.datetime.now()}.csv",
                     as_attachment=True)


if __name__ == '__main__':
    main()
    app.run(port=8080, host='127.0.0.1')
