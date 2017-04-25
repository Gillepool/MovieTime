from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask import session as flask_session

from movieapp.extensions import cache
from movieapp.models import User, db, Rating
from movieapp.forms import LoginForm, RegisterForm, RatingForm, SearchForm
from movieapp.util import *
import pickle
from movieapp.recommendation import *
from sqlalchemy.sql.expression import func, select
main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
@main.route('/home/page/<int:page>')
@cache.cached(timeout=10000)
def home(page=1):
    #movielist = db.session.query(Movie).order_by(Movie.rating.desc()).limit(9).all()
    movielist = Movie.query.order_by(Movie.rating.desc()).paginate(page, 9)
    return render_template('index.html', movies=movielist)

@main.route('/movie/<int:id>', methods=["GET", "POST"])
@login_required
def movie(id):
    movie = db.session.query(Movie).filter_by(id=id).one()
    print(movie)
    rated = db.session.query(Rating).filter_by(movie_id=id, user_id=current_user.id).first()
    #similarMovies = pickle.load(open("movies.p", "rb" ))
    #tes = transformPrefs(similarMovies)
    #top = top_matches(tes, movie.title, n=6)
    #similarMovies = []
    #print(top)
    #for movie1 in top:
     #   movie1 = db.session.query(Movie).filter_by(title=movie1[1]).first()
     #   similarMovies.append(movie1)
    #similarMovies = top_matches(similarMovies, id, n=5)
    #print(similarMovies)
    form = RatingForm()
    if form.validate_on_submit():
        if not rated:
            rating = Rating(form.rating.data, id, current_user.id)
            db.session.add(rating)
            flash("Added a rating")
            db.session.commit()
        else:
            rated.rating = form.rating.data
            flash("Rating updated")
            db.session.commit()

        return redirect(request.args.get("next") or url_for(".movie", id=id))
    return render_template('movie.html', movie=movie, form=form, rated=rated)

@main.route('/recommendedmovies/')
@login_required
def recommendedMovies():
    p = np.load("recs.npy")
    # print("MY ID", current_user.id)
    try:
        my_predictions = p[:, current_user.id - 1] + get_Ymean().flatten()
    except:
        flash("You don't have any recommendations yet, check back at a later time. In the meantime rate some movies")
        return redirect(url_for(".home", page=1))

    ix = my_predictions.argsort(axis=0)[::-1]
    movies = db.session.query(Movie).all()
    alreadyRecommended = db.session.query(Rating).filter_by(user_id=current_user.id).all()
    ids = []
    for movie in alreadyRecommended:
        ids.append(movie.movie_id)
    showMovies = []
    show = []
    for i in range(100):
        j = ix[i]
        showMovies.append(movies[j])
        print("Predicting rating %.1f for movie " % (my_predictions[j] / 2))
    for movie in showMovies:
        if movie.id not in ids:
            show.append(movie)
        else:
            print("NOT " , movie.title)
    return render_template('recommendedmovies.html', movies=show[0:10])

@main.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()
        login_user(user)
        flash("Logged in successfully")
        return redirect(request.args.get("next") or url_for(".home"))
    return render_template("login.html", form=form)

@main.route("/search", methods=["GET", "POST"])
def search():

    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for(".search_results", query=form.search.data))
    return render_template("search.html", form=form)

@main.route("/random_movie/")
def random_movie():
    rowId = Movie.query.order_by(func.random()).first().id

    row = Movie.query.get(rowId)
    print(row)
    return render_template('random_movie.html', movie=row)

@main.route('/search_results/<query>')
def search_results(query):
    print(query)
    result = Movie.query.filter(Movie.title.like(query + "%")).all()

    print(result)
    return render_template('search_results.html',
                           query=query,
                           results=result)

@main.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    password=form.password.data,
                    age=form.age.data,
                    gender=form.gender.data)
        db.session.add(user)
        db.session.commit()
        rating  = Rating(user_id=user.id, movie_id=1, rating=0)
        db.session.add(rating)
        db.session.commit()
        flash("Successfully registered a user")
        return redirect(request.args.get("next") or url_for(".login"))
    return render_template("register.html", form=form)


@main.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out")

    return redirect(url_for(".home"))


@main.route("/rec")
@login_required
def recs():
    prefs = pickle.load(open("prefs.p",'rb'))
    show = getRecommendations(prefs, current_user.id)
    similarMovies = []
    for movie1 in show[0:10]:
        print(movie1)
        similarMovies.append(db.session.query(Movie).filter_by(title=movie1[1]).first())

    return render_template('recommendedmovies.html', movies=similarMovies)