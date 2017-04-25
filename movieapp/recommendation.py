import scipy.io
import numpy as np
import scipy.optimize as op
import pandas as pd
from movieapp.models import db, Movie, Rating, User, Recommendations
from flask_login import current_user


def cofiCostFunc(params, Y, R, num_users, num_movies, num_features, Lamnda):

    X = params[0:num_movies*num_features].reshape(num_movies, num_features)
    Theta = params[num_movies*num_features:].reshape(num_users, num_features)

    J = 0
    X_grad = np.zeros((np.shape(X)))
    Theta_grad = np.zeros((np.shape(Theta)))

    J_temporary = (X.dot(Theta.T) - Y)**2
    J = np.sum(np.sum(J_temporary[R == 1]))/2 + Lamnda/2 * np.sum(np.sum(Theta**2)) + Lamnda/2 * np.sum(np.sum(X**2))

    X_grad = ((X.dot(Theta.T) - Y ) *R ).dot(Theta) + Lamnda*X
    Theta_grad = ((X.dot(Theta.T) - Y) * R).T.dot(X) + Lamnda*Theta

    grad = np.append(X_grad.flatten(), Theta_grad.flatten())

    return J, grad

def computeNumericalGradient(J, theta):
    numgrad = np.zeros((np.shape(theta)))
    perturb = np.zeros((np.shape(theta)))
    e = 1e-4

    for p in range(len(theta.flatten())):
        perturb[p] = e
        loss1, grad1 = J(theta - perturb)
        loss2, grad2 = J(theta + perturb)

        numgrad[p] = (loss2 - loss1)/(2*e)
        perturb[p] = 0
    return numgrad

def checkCostFunction(Lambda = None):
    if Lambda == None:
        Lambda = 0
    X_t = np.random.rand(4,3)
    theta_t = np.random.rand(5,3)

    Y = X_t.dot(theta_t.T)
    Y[np.random.rand(np.shape(Y)[0]) > 0.5] = 0
    R = np.zeros((np.shape(Y)))
    R[Y != 0] = 1

    m, n = np.shape(X_t)
    X = np.random.randn(m,n)
    a, b = np.shape(theta_t)
    theta = np.random.randn(a,b)
    num_users = np.shape(Y)[1]
    num_movies = np.shape(Y)[0]
    num_features = np.shape(theta_t)[1]
    def J(t):
        return cofiCostFunc(t, Y, R, num_users, num_movies, \
                                num_features, Lambda)

    numgrad = computeNumericalGradient(J, \
            np.append(X.flatten(), theta.flatten()))
    cost, grad = cofiCostFunc(np.append(X.flatten(), \
            theta.flatten()), Y, R, num_users, \
                          num_movies, num_features, Lambda)
    print( numgrad, grad)
    print ('The above two columns you get should be very similar.')
    print ('(Left-Your Numerical Gradient, Right-Analytical Gradient)')
    diff = np.linalg.norm(numgrad-grad)/np.linalg.norm(numgrad+grad)
    print ('If your backpropagation implementation is correct, then \
           #the relative difference will be small (less than 1e-9).\
           #Relative Difference: ', diff)



def LoadMovieList():
    counter = 0
    movielist = {}
    with open('data/movie_ids.txt', 'r') as fid:
        lines = fid.readlines()
        for line in lines:
            movielist[counter] = line.split(' ', 1)[1]
            counter += 1
    return movielist

def normalizeRatings(Y, R):
    m, n = np.shape(Y)
    Ymean = np.zeros((m, 1))
    YNorm = np.zeros((m,n))
    for i in range(m):
        idx = np.where(R[i, :] == 1)
        Ymean[i] = np.mean(Y[i, idx])
        YNorm[i, idx] = Y[i, idx] - Ymean[i]
    return [YNorm, Ymean]


def get_Ymean():
    ratings = pd.read_sql(db.session.query(Rating).statement, db.session.bind)
    movies = pd.read_sql(db.session.query(Movie).statement, db.session.bind)
    print(len(movies))
    # movis = pd.DataFrame(movielist, columns=['title,' 'release_year', 'imdb_url', 'poster',' description', 'genre', 'rating'])
    Y = ratings.pivot(index='movie_id', columns='user_id', values='rating').fillna(0)
    R = Y.copy()
    R[R > 0] = 1
    R = R.as_matrix()
    Y = Y.as_matrix()
    # Normalize ratings
    [Ynorm, Ymean] = normalizeRatings(Y, R)
    return Ymean

def prepare_data():
    users = pd.read_sql(db.session.query(User).statement, db.session.bind)
    ratings = pd.read_sql(db.session.query(Rating).statement, db.session.bind)
    movies = pd.read_sql(db.session.query(Movie).statement, db.session.bind)
    print(len(users))
    print(len(movies))
    #movis = pd.DataFrame(movielist, columns=['title,' 'release_year', 'imdb_url', 'poster',' description', 'genre', 'rating'])
    Y = ratings.pivot(index='movie_id', columns='user_id', values='rating').fillna(0)
    print(Y)
    R = Y.copy()
    R[R > 0] = 1
    R = R.as_matrix()
    Y = Y.as_matrix()
    # Normalize ratings
    [Ynorm, Ymean] = normalizeRatings(Y, R)

    # Useful values
    num_users = np.shape(Y)[1]
    num_movies = np.shape(Y)[0]
    num_features = 12  # number of "unknown" categories(features)

    # set init params (Theta, X)
    X = np.random.randn(num_movies, num_features)
    Theta = np.random.randn(num_users, num_features)

    initital_parameters = np.append(X.flatten(), Theta.flatten())

    Lambda = 10

    cost = lambda params: cofiCostFunc(params, Y, R, num_users, num_movies, num_features, Lambda)[0]
    grad = lambda params: cofiCostFunc(params, Y, R, num_users, num_movies, num_features, Lambda)[1]

    theta = op.minimize(cost, np.append(X.flatten(), Theta.flatten()), method='CG', jac=grad,
                        options={'disp': True, 'maxiter': 300})

    theta = theta.x
    print(theta)
    # Unfold the theta
    X = theta[:num_movies * num_features].reshape(num_movies, num_features)
    Theta = theta[num_movies * num_features:].reshape(num_users, num_features)

    p = X.dot(Theta.T)
    np.save("recs.npy", p)
    movieId = 1
    print(num_movies)
    print(num_users)

    '''
    for user in range(num_users):
        print(user, "out of", num_users)
        my_predictions = p[:, user] + Ymean.flatten()
        for rating in my_predictions:

        #ix = my_predictions.argsort(axis=0)[::-1]
            ratings = Recommendations(user_id=user+1, movie_id=movieId, recommendValue=rating)
            db.session.add(ratings)
            try:
                db.session.commit()
            except:
                db.session.rollback()
            movieId+=1
            print("movie, ", movieId, " out of", num_movies)
            print("user: ", user, " out of ", num_users)
    print("DONE")
    '''
    #for i in range(10):
       # j = ix[i]
       # print("Predicting rating %.1f for movie %s" % (my_predictions[j] / 2, movies['title'][j]))
