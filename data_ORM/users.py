import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin

'''Кроме того, наша модель для пользователей должна содержать ряд методов для корректной работы flask-login
, но мы не будем создавать их руками, а воспользуемся множественным наследованием. 
И помимо SqlAlchemyBase унаследуем User от UserMixin из модуля flask-login, 
то есть заголовок класса модели пользователей будет выглядеть так: UPD'''


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    # Создаём талблицу с именем users 

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    # Cоздаём столбики и передаём в них значения 
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    passwords = orm.relationship("Password", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
