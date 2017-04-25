from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import backref, load_only

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(), nullable=True, unique=True)
    password = db.Column(db.String(), nullable=True)
    age = db.Column(db.Integer(), nullable=True)
    gender = db.Column(db.String(), nullable=True)

    recommendation = db.relationship("Recommendations", backref=backref("users", order_by=id))

    def __init__(self, username, password, age, gender):
        self.username = username
        self.set_password(password)
        self.age = age
        self.gender = gender

    def set_password(self, password):
        self.password = generate_password_hash(password)


    def check_password(self, value):
        return check_password_hash(self.password, value)


    @property
    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True


    def is_active(self):
        return True


    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False


    def get_id(self):
        return self.id


    def __repr__(self):
        return '<User %r>' % self.username


class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(), nullable=True)
    release_year = db.Column(db.String(), nullable=True)
    imdb_url = db.Column(db.String(), nullable=True)
    poster = db.Column(db.String(), nullable=True)
    description = db.Column(db.String(), nullable=True)
    genre = db.Column(db.String(), nullable=True)
    rating = db.Column(db.String(), nullable=True)

    def __init__(self, *args, **kwargs):
        super(Movie, self).__init__(*args, **kwargs)

    def get_id(self):
        return self.id

    def get_imdb_url(self):
        return self.imdb_url

    def __repr__(self):
        return '<Movie %r>' % self.title

class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer(), primary_key=True)
    movie_id = db.Column(db.Integer(), db.ForeignKey('movies.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    rating = db.Column(db.Float(), default='0')

    user = db.relationship("User", backref=backref("ratings", order_by=id))
    movie = db.relationship("Movie", backref=backref("ratings", order_by=id))


    def __init__(self, rating, movie_id, user_id):
        self.rating = rating
        self.movie_id = movie_id
        self.user_id = user_id

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<Rating %r>' % self.rating



class Recommendations(db.Model):
    __tablename__ = 'recommendations'
    id = db.Column(db.Integer(), primary_key=True)
    movie_id = db.Column(db.Integer(), db.ForeignKey('movies.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    recommendValue = db.Column(db.Float(), default='0')

    user = db.relationship("User", backref=backref("recommendations", order_by=id))
    movie = db.relationship("Movie", backref=backref("recommendations", order_by=id))

    def __init__(self, *args, **kwargs):
        super(Recommendations, self).__init__(*args, **kwargs)

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<Rating %r>' % self.recommendValue

