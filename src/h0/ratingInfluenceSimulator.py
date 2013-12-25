#!/usr/bin/python -O
#
# Ideas for simulations:
#
# Simple model:
#
# A user's rating is based on
#   a) the displayed movie mean
#   b) the user's true preference, which is a function of the true underlying movie mean
#
# Combine these factors using some kind of weighted average.  How do differences in
# the simulation parameters affect the system?
#
# Make the simulation more realistic, and see how it affects the results you observe.
#
import copy
import random
import string


TRUE_MEANS = {
    'Pulp Fiction' : 4.1,
    'Forrest Gump' : 4.0,
    'Silence of the Lambs' : 4.2,
    'Jurassic Park' : 3.7,
    'The Shawshank Redemption' : 4.5,
    'Star Wars' : 4.2
}

NUM_SIMULATIONS = 1000
NUM_USERS = 100
MAX_RATINGS_PER_USER = 5

def main():
    finalMovieRanks = {}     # list of final ranks per movie
    finalMovieMeans = {}     # list of final means per movie
    for m in TRUE_MEANS.keys():
        finalMovieRanks[m] = []
        finalMovieMeans[m] = []

    # the outer loop runs the entire simulation from scratch NUM_SIMULATIONS times
    for i in xrange(NUM_SIMULATIONS):

        movieRatings = {}
        for m in TRUE_MEANS.keys():
            movieRatings[m] = []

        # simualte a user and update the ratings
        simulateUser(movieRatings)

        # print out the simulation results
        results = []
        for (movie, ratings) in movieRatings.items():
            results.append((mean(ratings), movie))
        results.sort()
        results.reverse()
        for i in xrange(len(results)):
            (movieMean, movie) = results[i]
            finalMovieRanks[movie].append(i+1)
            finalMovieMeans[movie].append(movieMean)

    movieRankPairs = [(mean(ranks), movie) for (movie, ranks) in finalMovieRanks.items()]
    movieRankPairs.sort()

    for (_, m) in movieRankPairs:
        ranks = finalMovieRanks[m]
        means = finalMovieMeans[m]
        print '%s (true mean %.3f)' % (m, TRUE_MEANS[m])
        print '\tavg rank is %.3f (%s)' % (mean(ranks), histogram(ranks))
        print '\tavg mean is %.3f (min=%.3f, max=%.3f)' % (mean(means), min(means), max(means))
        print


# Simulates a single user given a current set of movie ratings.
#
def simulateUser(movieRatings):
    # the first inner loop simulates each user
    for j in xrange(NUM_USERS):

        numRatings = random.randint(1, MAX_RATINGS_PER_USER)
        titles = list(TRUE_MEANS.keys())
        random.shuffle(titles)

        # the second inner loop simulates each rating
        for movie in titles[:numRatings]:
            displayedMean = mean(movieRatings[movie])
            trueMean = TRUE_MEANS[movie]
            rating = simulateUserRating(movie, displayedMean, trueMean)
            movieRatings[movie].append(rating)
            afterDisplayedMean = mean(movieRatings[movie])
            # uncomment to print event log for simulated users
            #print ('user %d rated "%s" a %.4f (mean shifted from %.4f to %.4f)'
            #% (j, movie, rating, displayedMean or 0.0, afterDisplayedMean))


# The random.normalvariate(mean, stdDev) function may be useful to you.
# The displayed mean might be None, indicating that no users have rated the movie.
#
def simulateUserRating(movie, displayedMean, trueMean):
    # userTrueRating = random.normalvariate(trueMean, 1.0)
    # if userTrueRating > 5.0:
    #     userTrueRating = 5.0
    # elif userTrueRating < 1.0:
    #     userTrueRating = 1.0
    values = getAlphaBeta(trueMean, 0.5)
    alpha = values[0]
    beta = values[1]
    userTrueRating = random.betavariate(alpha, beta) * 4 + 1
    destiny = random.random()
    if destiny < 0.2:
        userRating = userTrueRating * 2 - displayedMean if displayedMean != None else userTrueRating
        if userRating > 5:
            userRating = 5
        # print userRating, userTrueRating, displayedMean
        return userRating
    else:
        return (userTrueRating + displayedMean)/2 if displayedMean != None else userTrueRating

def getAlphaBeta(mean, std):
    a = (mean - 1.0) / 4  # normalizedMean
    b = (std / 4.0) ** 2  # normalizedStd
    alpha = (-a**3+a**2-a*b)/b
    beta = (a**3-2*a**2+a*b+a-b)/b
    return alpha, beta


def mean(l):
    if not l:
        return None
    else:
        return 1.0 * sum(l) / len(l)


def histogram(values):
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    keys = counts.keys()
    keys.sort()
    return string.join(
        [('%s=%s' % (k, counts[k])) for k in keys]
    )


if __name__ == '__main__':
    main()