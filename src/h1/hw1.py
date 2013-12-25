"""
Author: Yu Zhao, Yulun Li

Read in the movie ids and their associated titles.
Returns a hashtable containing the association.
Note that the ids are strings.

Overall mean: 3.51
Distribution: (0.5, 94988), (1.0, 384180), (1.5, 118278), (2.0, 790306), (2.5, 370178), (3.0, 2356676),
    (3.5, 879764), (4.0, 2875850), (4.5, 585022), (5.0, 1544812)

Star Wars 5: 0.989467264935 (because Star Wars fans very possibly have watched and enjoyed all Star Wars movies)
Notting Hill: 0.943972631726
Time complexity: O(u)

Similarity score: 0.989: 1196::Star Wars: Episode V - The Empire Strikes Back (1980)::Action|Adventure|Sci-Fi
Similarity score: 0.986: 1210::Star Wars: Episode VI - Return of the Jedi (1983)::Action|Adventure|Sci-Fi
Similarity score: 0.982: 1198::Raiders of the Lost Ark (Indiana Jones and the Raiders of the Lost Ark) (1981)
    ::Action|Adventure

Extra credit 1:
Tags that "have been" used by Star Wars:
    'saturn award (best makeup)', 'highly quotable', 'far future', 'great soundtrack', 'series', 'adventure', 'divx1',
    'george lucas', 'fantasy', 'gfei own it', 'spielberg/lucas', 'james earl jones', 'darth vader',
    'saturn award (best special effects)', 'star wars', 'noise in space', 'usa', 'space', 'tv', 'classic',
    'harrison ford', 'desert', 'luke skywalker', 'space-opera', 'futuristmovies.com', "eric's dvds", 'war',
    'han solo', 'galactic', 'sci-fi', 'myth', 'luke', 'sequel', 'space opera', 'robots', 'imdb top 250',
    'oscar (best art direction - set decoration)', 'saturn award (best science fiction film)', 'franchise',
    'rating very dependent on version', 'seen more than once', 'saturn award (best actor)', 'lucas',
    'oscar (best sound)', 'dvd', '70mm', 'oscar (best music - original score)', 'vhs', "tumey's dvds",
    'seen at the cinema', 'saturn award (best costumes)', 'nerdy', 'action', 'saturn award (best director)',
    'carrie fisher', 'mark hamill'
Tags that "have not" been used:
    'oscar (best effects - sound effects editing)', 'best of the originals', 'just great', 'i am your father',
    'father-son relationship', 'family drama', 'violent', 'crappy fight choreography', 'sequel better than original',
    'could carry on but i might end up spoilin it for you', 'sci fi', 'death of darth vader', 'superhero', 'father',
    'snow', 'bespin', 'jedi', 'music', 'scifi', 'best of star wars', 'clv', 'betamax', 'hoth', 'good',
    'strong director', 'better than original', 'carbonite', 'scope', 'space battle', 'richard marquand',
    'billy dee williams', 'father son relationship', 'parenthood', 'crappy sequel', 'theater', 'redemption',
    'science fiction', 'bad', 'victory', 'irvin kershner', 'plot holes', 'bah'

Extra credit 2:
We added method normalize(scoreDict) and got lower similarity scores.
1196: 0.982
1210: 0.973
1198: 0.969
Possible reasons for lower scores:
    1. We deleted users that gave all movies the same ratings.
    2. For each user, the ratings always range from 0.0-1.0, although before normalizing, the range can be
        a proportion of the full range. This increases the variance of scores.

Extra Credit 3:
The Pearson correlation yields the same top three most similar movies:
1196: 0.703
1210: 0.643
1198: 0.441
Item with the most negative score: -0.0634, 1483::Crash (1996)::Drama|Thriller
Our filter only considers movies rated 1000+ times.

Extra Credit 4:
We found the users that have rated the target movie, and collected all the ratings they have given to other movies.
We found the movie with the most number of co-ratings, and discount every original correlation score by
numberOfRatings/maxNumberOfRatings.
The top three movies remain unchanged but their order:
1210: 0.7035990766754288
1196: 0.6726934638984933
1198: 0.5769378445789745
"""
__author__ = 'Yu Zhao', 'Yulun Li'


from collections import defaultdict
import math
import time


class Ratings():
    def __init__(self, ratingsData, moviesData, tagsData, logPath):
        self.ratingsDir = ratingsData
        self.movief = open(moviesData, 'r')
        self.tagsDir = tagsData
        self.logPath = logPath

    # def readMovies(self):
    #     """
    #     Copied from problem set.
    #     """
    #     movies = {}
    #     for line in self.movief:
    #         tokens = line.split('::')
    #         if len(tokens) >= 2:
    #             (movieId, title) = tokens[:2]
    #             movies[movieId] = title
    #     self.movief.close()
    #     return movies

    def readRatings(self, kth, n):
        """
        Source: http://stackoverflow.com/a/1985733/2469192
        Set up as an Iterable so that the generator can be reused.
        Yield the kth user for every n users.
        Not using a log because 1. the dataset is well formatted 2. can't write a log file in parallel
        """

        class Iterable(object):
            ratingsDir = self.ratingsDir

            def __iter__(self):
                # initiate variable to keep track of current user
                currentUser = None
                # dictionary that maps movie ID to rating of all movie ratings by ONE user
                movieRatings = {}
                userCount = 0
                with open(self.ratingsDir, 'r') as f:
                    for line in f:
                        try:
                            tokens = line.split('::')
                            if currentUser == tokens[0] or currentUser is None:
                                if currentUser is None:
                                    currentUser = tokens[0]
                                if userCount % n == kth:
                                    movieRatings[tokens[1]] = float(tokens[2])
                            elif userCount % n == kth:
                                yield currentUser, movieRatings
                                userCount += 1
                                # Reset currentuser and its movieRatings dict
                                currentUser = tokens[0]
                                movieRatings = dict()
                                # update new movieRating dictionary
                                movieRatings[tokens[1]] = float(tokens[2])
                            else:
                                currentUser = tokens[0]
                                userCount += 1
                        except ValueError:
                            print("error reading: " + line + " \n")
                            # !!CRUCIAL!! yield last user's information
                    if userCount % n == kth:
                        yield currentUser, movieRatings

        return Iterable()

    def ratingStats(self):
        """
        Count number of users, ratings and its mean
        """
        numUsers, numRatings, meanRatings = 0, 0, 0
        ratingsByUser = {}
        distribution = defaultdict(int)
        for userRatings in self.readRatings(0, 1):
            numUsers += 1
            numRatings += len(userRatings[1])
            ratingsByUser[userRatings[0]] = userRatings[1]
            # meanRatings = (meanRatings + sum(userRatings[1].values())) / (len(userRatings[1]) + 1)
            meanRatings += sum(userRatings[1].values())
            for rating in userRatings[1].values():
                distribution[rating] += 1
        return numUsers, numRatings, meanRatings / numRatings, distribution

    def singleCorrelation(self, movieId, movieId1):
        """
        Return similarity score of movieId and movie Id1
        """
        xDotX, xDotY, yDotY = 0, 0, 0
        for userRatings in self.readRatings(0, 1):
            if movieId in userRatings[1] and movieId1 in userRatings[1]:
                x, y = userRatings[1][movieId], userRatings[1][movieId1]
                xDotX += x * x
                xDotY += x * y
                yDotY += y * y
        return xDotY / math.sqrt(xDotX * yDotY)

    def allCorrelations(self, movieId, ifSmooth):
        """
        Return a sorted list of tuples that are the 20 most similar movies to movieId (cosine similarity)
        If ifSmooth is true, the result uses the discounted scores rather than the truncated.
        """
        # t1 = time.time()
        relatedRatings = defaultdict(lambda: [[], [], []])
        for userRatings in self.readRatings(0, 1):
            if movieId in userRatings[1]:
                if self.normalize(userRatings[1]):
                    x = userRatings[1][movieId]
                    for key, value in userRatings[1].iteritems():
                        y = value
                        relatedRatings[key][0].append(x * x)
                        relatedRatings[key][1].append(x * y)
                        relatedRatings[key][2].append(y * y)
        unsortedResult = {}
        # t2 = time.time()
        # print(str(t2 - t1))
        while relatedRatings:
        # Do this if only the related Ratings dict is not empty
            discounter = max(len(relatedRatings[relatedRating][0]) for relatedRating in relatedRatings)
            for key, value in relatedRatings.iteritems():
                xDotX, xDotY, yDotY = sum(value[0]), sum(value[1]), sum(value[2])
                if ifSmooth:
                    unsortedResult[key] = xDotY * len(value[0]) / (discounter * math.sqrt(xDotX * yDotY)) \
                        if xDotX * yDotY != 0 else 0.0
                else:
                    if len(value[0]) >= 1000:
                        unsortedResult[key] = xDotY / math.sqrt(xDotX * yDotY)
            unsortedResult.pop(movieId)
            # t3 = time.time()
            # print(str(t3-t2))
            return sorted(unsortedResult.iteritems(), key=lambda result: result[1], reverse=True)[:20]
        # t3 = time.time()
        # print(str(t3 - t2))

    def allCorrelationsPearson(self, movieId):
        """
        Return a sorted list of tuples that are the 20 most similar movies to movieId (Pearson similarity)
        """
        relatedRatings = defaultdict(lambda: [[], []])
        for userRatings in self.readRatings(0, 1):
            if movieId in userRatings[1]:
                if self.normalize(userRatings[1]):
                    for key, value in userRatings[1].iteritems():
                        relatedRatings[key][0].append(userRatings[1][movieId])
                        relatedRatings[key][1].append(value)
        unsortedResult = {}
        while relatedRatings:
            # Do this if only the related Ratings dict is not empty
            for key, value in relatedRatings.iteritems():
                if len(value[0]) >= 1000:
                    simScore = self.pearson_correlation(value[0], value[1])
                    unsortedResult[key] = simScore
            unsortedResult.pop(movieId)
            return sorted(unsortedResult.iteritems(), key=lambda result: result[1], reverse=True)[:20]

    def analyzeTags(self, targetMovieId):
        """
        Return the haveBeen and notHaveBeen tags of the targetMovieId
        """
        movieIdList = [movie[0] for movie in self.allCorrelations(targetMovieId, False)[1:3]]
        movieTags = set()
        movieListTags = set()
        with open(self.tagsDir, 'r') as f:
            for line in f:
                tokens = line.split('::')
                if len(tokens) >= 3:
                    (movieId, tag) = tokens[1:3]
                    tag = tag.lower()
                    if movieId in movieIdList:
                        movieListTags.add(tag)
                    elif movieId == targetMovieId:
                        movieTags.add(tag)
        return movieTags.intersection(movieListTags), movieListTags.difference(movieTags)

    def normalize(self, scoreDict):
        """
        Normalize a scoreDict to score range of 0.0-1.0
        """
        minScore, maxScore = min(scoreDict.values()), max(scoreDict.values())
        if maxScore - minScore == 0:
            scoreDict.clear()
            return False
        else:
            for key in scoreDict:
                scoreDict[key] = (scoreDict[key] - minScore) / (maxScore - minScore)
            return True

    def pearson_correlation(self, object1, object2):
        """
        Return a Pearson similarity score of two objects
        Source found online:
        http://mines.humanoriented.com/classes/2010/fall/csci568/portfolio_exports/sphilip/pear.html
        """
        values = range(len(object1))

        # Summation over all attributes for both objects
        sum_object1 = sum([float(object1[i]) for i in values])
        sum_object2 = sum([float(object2[i]) for i in values])

        # Sum the squares
        square_sum1 = sum([pow(object1[i], 2) for i in values])
        square_sum2 = sum([pow(object2[i], 2) for i in values])

        # Add up the products
        product = sum([object1[i] * object2[i] for i in values])

        #Calculate Pearson Correlation score
        numerator = product - (sum_object1 * sum_object2 / len(object1))
        denominator = ((square_sum1 - pow(sum_object1, 2) / len(object1)) * (square_sum2 -
                                                                             pow(sum_object2, 2) / len(object1))) ** 0.5

        # Can"t have division by 0
        if denominator == 0:
            return 0

        result = numerator / denominator
        return result

    def main(self):
        # t1 = time.time()
        ratingStats = self.ratingStats()
        print("numUsers: " + str(ratingStats[0]) + "\nnumRatings: " + str(ratingStats[1]) +
              "\nmeanRatings: " + str(ratingStats[2]) + "\ndistribution: " + str(ratingStats[3].items()))
        # t2 = time.time()
        # print(str(t2 - t1))
        print(self.singleCorrelation('260', '1196'))  # Star Wars 5
        print(self.singleCorrelation('260', '2671'))  # Notting Hill
        # t3 = time.time()
        # print(str(t3 - t2))
        result = self.analyzeTags('260')
        print(result[0])
        print(result[1])
        print(self.allCorrelations('260', True))
        # print(str(time.time() - t3))
        # return None


if __name__ == "__main__":
    baseDir = "C:\\Users\\Yu\\Downloads\\ml-10M100K\\"
    baseDir1 = "/home/ilps/Downloads/COMP432/h1/ml-10M100K/"
    files = ("ratings.dat", "movies.dat", "tags.dat")
    fileDirs = [baseDir1 + fileDir for fileDir in files]
    fileDirs.append("log")
    ratings = Ratings(fileDirs[0], fileDirs[1], fileDirs[2], fileDirs[3])
    ratings.main()