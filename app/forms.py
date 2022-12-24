from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, EqualTo

from app.models import Reader, Author
from app.routes import session


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    role = BooleanField('Я Автор')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    role = BooleanField('Вы автор?')
    submit = SubmitField('Зарегистрироваться')

    def validate_login(self, login):
        if self.role.data:
            user = Author.get_by_login(login.data)
        else:
            user = Reader.get_by_login(login.data)
        print(user)
        if user is not None:
            raise ValidationError('Используйте другое имя')


class BookForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    submit = SubmitField('Создать книгу')


class ChapterForm(FlaskForm):
    book = StringField('Название', validators=[DataRequired()])
    num_ch = IntegerField('Номер главы', validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    submit = SubmitField('Загрузить')
