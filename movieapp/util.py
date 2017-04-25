from movieapp.models import db, Movie, Rating, User
import os, requests
import time
import functools
import omdb
from math import sqrt





def timeit(func):
    @functools.wraps(func)
    def newfunc(*args, **kwargs):
        startTime = time.time()
        func(*args, **kwargs)
        elapsedTime = time.time() - startTime
        print('function [{}] finished in {} ms'.format(
            func.__name__, int(elapsedTime * 1000)))
    return newfunc


def get_omdb(id):
    movie = omdb.imdbid("tt"+str(id))
    return movie


#Pearson correlation Score algoritm
def sim_pearson(data, p1, p2):


    #En dict med gemensamma betygsatta items(filmer)
    si = {}
    for item in data[p1]:
        if item in data[p2]:
            si[item]=1

    #
    n = len(si)

    #Inga betygsättningar i gemenskap
    if n == 0:
        return 0

    #Summerar alla preferenser
    sum1=sum([data[p1][it] for it in si])
    sum2 = sum([data[p2][it] for it in si])

    #Samma emen upphöjt
    sum1Sq = sum([pow(data[p1][it],2) for it in si])
    sum2Sq = sum([pow(data[p2][it],2) for it in si])

    #summera produktena
    pSum = sum([data[p1][it]*data[p2][it] for it in si])

    #Beräknar pearson-score för algoritmen
    num=pSum-(sum1*sum2/n)
    den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den == 0:
        return 0

    r = num/den

    return r

#Distans mellan tvp personers smak typ algoritm
def sim_distance(data, person1, person2):


    si={}
    for item in data[person1]:
        if item in data[person2]:
            si[item]=1

    #Om man inte har någon rating gemensamt
    if len(si) == 0:
        return 0

    # Summerar skillnaden mellan personerna upphöjt i 2
    sum_of_squares=sum([pow(data[person1][item]-data[person2][item],2)
                        for item in data[person1] if item in data[person2]])



    return 1/(1+sum_of_squares)


#Jämför items med varandra istället för personer, är bättre vid en större data
def calculateSimilarItems(data, n):
    # Create a dict of items showing which other items they are most similar to
    #skapar en dict med items(filmer) som andra items(filmer) som dem har mest gemensamt med
    result = {}

    #Inverterar preferens matricen
    itemData = transformPrefs(data)
    C=0
    for item in itemData:
        #Status update för stora datasets
        C+=1
        if C%100==0:
            print("%d / %d" % (C, len(itemData)))
            #Hitta den som har mest gemensamt med en viss item med sim_distance algoritmen
        scores = top_matches(itemData, item, n=n,similarity=sim_pearson)
        result[item] = scores
    return result

def transformPrefs(data):
    result={}
    for person in data:
        for item in data[person]:
            result.setdefault(item, {})

            #Flippar personen och items
            result[item][person]=data[person][item]
    return result

# Rankar kritikerna(personerna)
def top_matches(data, person, n, similarity=sim_pearson):
    scores = [(similarity(data, person, other), other) for other in data if other !=person]

    scores.sort()
    scores.reverse()
    return scores[:n]

def getRecommendedItem(data, itemMatch, user):
    userRating=data[user]
    scores={}
    totalSim={}
    #Loop over items betygsatt av användaren
    for (item, rating) in userRating.items():
        #loop over items liknande denna
        for (similatiry, item2) in itemMatch[item]:
            #Ignorera om den redan betygsatt
            if item2 in userRating:continue

            #Weighted summering av betygsättnigarna och gemenskapen
            scores.setdefault(item2, 0)
            scores[item2]+=similatiry*rating

            #summerin av alla gemenskaper
            totalSim.setdefault(item2, 0)
            totalSim[item2]+=similatiry
    #rankings=[(score/totalSim[item], item) for item, score in scores.items()]
    rankings = []
    for item, score, in scores.items():
        if totalSim[item] == 0:
            totalSim[item] = 0.01
        rankings.append((score/totalSim[item], item))

    rankings.sort()
    rankings.reverse()
    return rankings

# Gets recommendations for a person by using a weighted average
#  of every other user's rankings
def getRecommendations(prefs,person,similarity=sim_pearson):
    totals={}
    simSums={}
    for other in prefs:
        if other==person:
            continue
        sim=similarity(prefs,person,other)
        if sim<=0: continue
        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item]==0:
                totals.setdefault(item,0)
                totals[item]+=prefs[other][item]*sim

                simSums.setdefault(item,0)
                simSums[item]+=sim
    rankings=[(total/simSums[item],item) for item,total in totals.items()]
    rankings.sort()
    rankings.reverse()
    return rankings

def prepare_data_sim():
    data = Movie.query.all()
    movies = {}
    for movie in data:
        (id, title) = movie.id, movie.title
        movies[id] = title
    dataw = Rating.query.all()
    ratings = {}
    for rating in dataw:
        (userid, movieid, rating) = rating.user_id, rating.movie_id, rating.rating
        ratings.setdefault(userid, {})
        ratings[userid][movies[movieid]]=float(rating)


    return ratings