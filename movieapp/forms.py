from wtforms import PasswordField, validators, StringField, IntegerField, SelectField
from flask_wtf import Form

from .models import User

class LoginForm(Form):
    username = StringField(u'username', validators=[validators.required()])
    password =PasswordField(u'password', validators=[validators.required()])

    def validate(self):
        check_validate = super(LoginForm, self).validate()

        if not check_validate:
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append('Invalid username or password')
            return False

        if not user.check_password(self.password.data):
            self.username.errors.append('Invalid Username or PAssword')
            return False
        return True


class RegisterForm(Form):
    username = StringField(u'username', validators=[validators.required()])
    password = PasswordField(u'password', validators=[validators.required()])
    passwordAgain = PasswordField(u'passwordAgain', validators=[validators.required()])
    age = IntegerField(u'age', validators=[validators.required()])
    gender = StringField(u'gender', validators=[validators.required()])


    def validate(self):
        check_validate = super(RegisterForm, self).validate()

        if not check_validate:
            print("HELLO1")
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append('The username already exists')
            print("HELLO2")
            return False

        print(self.password, self.passwordAgain)
        if self.password.data != self.passwordAgain.data :
            self.username.errors.append('Passwords did not match')
            print("HELLO3")
            return False
        return True

class RatingForm(Form):
    ratings = [(1, 1), (1.5, 1.5), (2, 2), (2.5, 2.5), (3, 3), (3.5, 3.5), (4, 4), (4.5, 4.5), (5, 5)]
    rating = SelectField(u'Rate this movie', choices=ratings, validators=[validators.required()], coerce=float)


    def validate(self):
        check_validate = super(RatingForm, self).validate()

        if not check_validate:
            print("HELLO1")
            return False

        return True

class SearchForm(Form):
    search = StringField(u'search', validators=[validators.required()],)


    def validate(self):
        check_validate = super(SearchForm, self).validate()

        if not check_validate:
            print("HELLO1")
            return False

        return True

