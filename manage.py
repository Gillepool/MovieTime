import os

from flask_script import Manager, Server
from flask_script.commands import ShowUrls, Clean
from movieapp import create_app
from movieapp.models import db, User, Movie, Rating
from movieapp.util import *
import pickle
from movieapp.recommendation import prepare_data
from random import randint
import pandas as pd
#Default to dev-config
env = os.environ.get('MOVIEAPP_ENV', 'dev')
app = create_app('movieapp.settings.%sConfig' % env.capitalize())

manager = Manager(app)
manager.add_command("server", Server())
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())

@manager.shell
def make_shell_context():
    '''
    Creates a ptyhon REPL with several default
    imports in the context of the app
    :return:
    '''
    return dict(app=app, db=db, User=User, Movie=Movie, Rating=Rating)


@manager.command
def createdb():
    '''
    Creates a database with all of the tables defined in SQLalchemy models
    :return:
    '''
    db.create_all()

@manager.command
def seed_db_users():
    try:
        db.session.query(User).delete()
        db.session.commit()
    except:
        db.session.rollback()
    import random
    f = open('movieapp/data/u.user', 'r')
    lines = f.readlines()
    string = "abcdefghijklmnopqrstuvwxyz"
    for i in range(671):
        rand_str = lambda n: ''.join([random.choice(string) for i in range(n)])
        # Now to generate a random string of length 10
        s = rand_str(10)
        p = rand_str(10)
        user = User(username=s, password=p, age=randint(10,65), gender="M")
        db.session.add(user)

    f.close()
    try:
        db.session.commit()
    except:
        db.session.rollback()

@manager.command
def seed_db_movies():
    try:
        db.session.query(Movie).delete()
        db.session.commit()
    except:
        db.session.rollback()

    f= open('movieapp/data/links.csv', 'r')
    next(f)
    lines = f.readlines()
    i = 0
    for line in lines:
        try:
             data = line.split(',')
             movie = get_omdb(data[1])
             movie = Movie(id = data[0], title=movie.title, release_year=movie.released, imdb_url=movie.imdb_id,
                            poster=movie.poster, description=movie.plot, genre=movie.genre, rating=movie.imdb_rating)
             db.session.add(movie)
             i+=1
             try:
                 db.session.commit()
                 print(movie.title, "was added, id:", i, data[0])
             except:
                 db.session.rollback()
                 print(movie.title, "Error adding movie", i, data[0])

        except Exception as e:
            print("ERROR", str(e))
    f.close()



@manager.command
def seed_db_ratings():
    try:
        db.session.query(Rating).delete()
        db.session.commit()
    except:
        db.session.rollback()
    f = open('movieapp/data/ratings.csv', 'r')
    next(f)
    lines = f.readlines()

    for line in lines:
        fields = line.split(',')
        print(fields)
        rating = Rating(user_id=fields[0],
                        movie_id=fields[1],
                        rating=fields[2])
        db.session.add(rating)
    f.close()
    try:
        db.session.commit()
    except:
        db.session.rollback()

@manager.command
def recommend():
    prefs = prepare_data_sim()
    #itemSim = calculateSimilarItems(prefs, n=50)
    pickle.dump(prefs, open("prefs.p", "wb"))
    #pickle.dump(itemSim, open("itemSim.p", "wb"))


@manager.command
def similarmovies():
    movies = prepare_data_sim()
    print(movies)
    pickle.dump(movies, open("movies.p", "wb"))

@manager.command
def updaterecommendations():
    prepare_data()



if __name__ == "__main__":
    manager.run()