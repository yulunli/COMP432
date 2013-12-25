"""
Author: Yu Zhao, Yulun Li

Description:
This program analyzes tweets.

Instruction:
- Edit the baseDir to your tweet file directory.
- Requires the pp library to run

Result:
Small tweet:
- The mean and median of tweets per user are 28 and 23 in the small dataset.
- Top 100 tweeters have about 80-100 tweets.
Large tweet:
- The mean and median of tweets per user are much large, 1351 nd 707 respectively.
- Top tweeters have about 4,000-20,000 tweets.

Highlight: we figured out multiprocessing and running time is shortened to 2.05 sec from 2.88 sec for small tweet
and to 42 sec from 68 sec for big tweet.

"""
import collections
import pp
import re
import time


class Tweets():

    dfValueBuffer = 5
    dfThreshold = 10
    topUserThreshold = 100
    topInterestingWords = 20

    def __init__(self, tweetDir):
        self.tweetDir = tweetDir

    def allTweets(self):
        """
        Source: http://stackoverflow.com/a/1985733/2469192
        Set up as an Iterable so that the generator can be reused.
        """
        class Iterable(object):
            """
            Creates a reusable tweet generator.
            Codes related to the logger are commented out because the multiple processes cannot write to the same
            log file (the logger itself is thread safe).
            We can capture the whole tweet even if there are '\' or '\n' in between because we catch the
            value error and append it to the previous feed.
            """
            f = open(self.tweetDir, 'r')
            def __iter__(self):
                # log = open ("errorLog" , 'w')
                tweet = {'timeStamp': -1, 'recordId': -1, 'userName': "", 'tweetText': ""}
                for line in self.f:
                    try:
                        fields = line.split('\t')
                        tweet = {'timeStamp': int(fields[0]), 'recordId': int(fields[1]), 'userName': str(fields[2]), 'tweetText': str(fields[3])}
                        yield tweet
                        tweet = {'timeStamp': -1, 'recordId': -1, 'userName': "", 'tweetText': ""}
                    except ValueError:
                        tweet['tweetText'] += line
                        # log.write("ValueError reading line: " + line)
                    except IndexError:
                        # We are not sure how to fix this.
                        pass
                        # log.write("IndexError reading line: " + line)
                # log.close()
                self.f.close()
        return Iterable()

    def getMean(self, sample):
        """
        Return the mean of a given sample of type dictionary with integer values.
        Time complexity is O(u) for u usernames and that of len() is O(1)
        """
        return sum(sample.values()) / len(sample)

    def getMedian(self, unsorted):
        """
        Returns the median of a dictionary that maps a userName
        to the number of its tweets. It will call a helper function quickSelect()
        """
        # find index number of median
        indexOfMedian = (len(unsorted) - 1) / 2
        # construct a list comprised of only frequencies using existing
        # dictionary, then pass the list to quickSelect() function
        return self.quickSelect(unsorted.items(), indexOfMedian)

    def getTopItems(self, sample, k):
        """
        This function returns the top k keys from a dictionary (sample).
        The sample should be in the form of dictionary, where key is the
        useranme and value is the number of tweet associated to the
        username. It will call a helper function quickSelect()
        """
        threshold = self.quickSelect(sample, len(sample)-k)
        result = []
        for item in sample:
            if item[1] >= threshold[1]:
                result.append(item)
        return result

    def quickSelect(self, unsortedList, k):
        """
        Return the smallest kth item of the list using quick select.
        The algorithm is in a recursive fashion.
        Complexity O(log(u))
        """
        # calling helper function lomutoPartition for pivot position
        s = self.lomutoPartition(unsortedList)
        # if pivot position == k, return pivot position
        if s == k:
            return unsortedList[s]
        # if pivot position > k, process values before pivot position
        elif s > k:
            return self.quickSelect(unsortedList[0:s], k)
        # if pivot position < k, process values after pivot position
        else:
            return self.quickSelect(unsortedList[s+1:len(unsortedList)], k-1-s)

    def lomutoPartition(self, unpartitionedList):
        """
        Returns pivot position that partitions the list of the first list item.
        Complexity O(n)
        """
        # initialize pivot
        pivot = unpartitionedList[0]
        # initialize pivot position
        pivotPosition = 0
        for i in range(1, len(unpartitionedList)):
            if unpartitionedList[i][1] < pivot[1]:
                # update pivot position
                pivotPosition += 1
                unpartitionedList[i], unpartitionedList[pivotPosition] = \
                    unpartitionedList[pivotPosition], unpartitionedList[i]
        unpartitionedList[0], unpartitionedList[pivotPosition] = \
            unpartitionedList[pivotPosition], unpartitionedList[0]
        # return pivot position
        return pivotPosition

    def getTweetCounter(self):
        """
        Returns a dictionary that maps a userName to its number of tweets.
        Time complexity O(n) because retrieving a userName is constant time.
        """
        tempTweetCounter = collections.defaultdict(int)
        for tweet in self.allTweets():
            tempTweetCounter[tweet['userName']] += 1
        print("Total number of tweets: " + str(sum(tempTweetCounter.values())))
        return tempTweetCounter

    def getTfCounter(self):
        """
        Returns a dictionary that maps a userName to a nested dictionary that maps a term to its term frequency.
        Time complexity O(n)+O(numberOfTerms).
        Did not use defaultdict because the parallel API doesn't like it.
        Our implementation in the non-parallel version:

        tfCounter = defaultdict(lambda: defaultdict(int))
        for tweet in self.allTweets():
            for term in re.split('\W+', tweet['tweetText'].lower()):
                tfCounter[tweet['userName']][term] += 1
        """
        tfCounter = {}
        for tweet in self.allTweets():
            if tweet['userName'] not in tfCounter:
                tfCounter[tweet['userName']] = {}
            for term in re.split('\W+', tweet['tweetText'].lower()):
                if term in tfCounter[tweet['userName']]:
                    tfCounter[tweet['userName']][term] += 1
                else:
                    tfCounter[tweet['userName']][term] = 0
        return tfCounter

    def getDfCounter(self):
        """
        Returns a dictionary that maps a term to the number of documents that contain the term.
        Time complexity O(n)+O(numberOfTerms).
        """
        # The helper maps a term to a set of userNames that have used the term.
        dfCounterHelper = collections.defaultdict(set)
        for tweet in self.allTweets():
            for term in re.split('\W+', tweet['tweetText'].lower()):
                dfCounterHelper[term].add(tweet['userName'])
        # The actual df counter that maps the term to the size of list of unique users that have used the term.
        dfCounter = collections.defaultdict(int)
        for key, value in dfCounterHelper.iteritems():
            dfCounter[key] = len(value) + self.dfValueBuffer
        return dfCounter

    def main(self):
        """
        Generate the tweetCounter, tfCounter and dfCounter in parallel.
        """
        job_server = pp.Server()
        if job_server.get_ncpus() > 4:
            job_server.set_ncpus(4)
        print "Starting pp with", job_server.get_ncpus(), "workers"
        p1 = job_server.submit(self.getDfCounter, (), (self.allTweets, ), ('collections', 're', ))
        p2 = job_server.submit(self.getTfCounter, (), (self.allTweets, ), ('collections', 're', ))
        p3 = job_server.submit(self.getTweetCounter, (), (self.allTweets, ), ('collections', ))
        dfCounter = p1()
        tfCounter = p2()
        tweetCounter = p3()

        print("Mean: " + str(self.getMean(tweetCounter)))

        print("Median: " + str(self.getMedian(tweetCounter)[1]) + " ("
              + self.getMedian(tweetCounter)[0] + ")")

        print("Top " + str(self.topUserThreshold) + " users: "
              + str(tweets.getTopItems(tweetCounter.items(), self.topUserThreshold)))

        for userName in validUser:
            if userName in tfCounter.keys():
                # obtain term frequency dictionary of a specific user
                tf = tfCounter[userName]
                tfIdf = {}
                for term, frequency in tf.iteritems():
                    # Ignore terms with document frequencies lower than threshold
                    if dfCounter[term] > self.dfThreshold:
                        tfIdf[term] = 1.0 * frequency / dfCounter[term]
                print(userName + "'s " + "most interesting words: " +
                      str(self.getTopItems(tfIdf.items(), self.topInterestingWords)))
            else:
                print(userName + " does not exist. ")
        job_server.print_stats()


if __name__ == "__main__":
    baseDir = "/home/ilps/Downloads/COMP432/h0"
    smallTweetDir = "/tweets.100k"
    largeTweetDir = "/tweets.large"
    validUser = ['rdematos', 'mccook', 'CatholicHawaii', 'mirnacavalcanti', 'HugoFeijo', 'bonniejpreston']
    # tweets = Tweets(baseDir + smallTweetDir)
    tweets = Tweets(baseDir + largeTweetDir)
    t1 = time.time()
    tweets.main()
    print(time.time()-t1)