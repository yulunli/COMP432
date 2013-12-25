"""
Author: Yu Zhao, Yulun Li

Description:
This program analyzes tweets.

Instruction:
You need a tweet file to run this program.


"""
from collections import defaultdict
from multiprocessing import Process, Manager
from multiprocessing.managers import DictProxy

import re
import time



class Tweets():
    def __init__(self, tweetDir):
        self.tweetDir = tweetDir
        # self.f = open(tweetDir, 'r')

    def allTweets(self):
        class Interable(object):
            f = open(self.tweetDir, 'r')
            """
            This function reads in the sequence of tweets, parse the four
            fields, and yields a data structure containing a single tweet.
            The data structure should contain the timestamp and record id
            as ints.
            """
            # initialize valid tweets counter
            def __iter__(self):
                numberOfValidTweets = 0
                # initialize tweet number counter (line number)
                # open log file for write in
                log = open ("errorLog" , 'w')
                # iterate through every line of tweets
                for line in self.f:
                    try:
                        # split each line into 4 elements in a list
                        fields = line.split('\t')
                        # construct a dictionary for each individual tweet
                        tweet = {'timeStamp': int(fields[0]), 'recordId': int(fields[1]), 'userName': str(fields[2]), 'tweetText': str(fields[3])}
                        # update counter
                        numberOfValidTweets += 1
                        # streaming the parsed result of each tweet
                        yield tweet
                    except ValueError:
                        # log tweet (line) number if failed to read
                        log.write("ValueError reading line: " + line)
                    except IndexError:
                        log.write("IndexError reading line: " + line)
                    # print out the number of valid tweets (tweets number get streamed)
                log.close()
                self.f.close()
        return Interable()

    def getMean(self, sample):
        """
        Return the mean of a given sample of type dictionary with integer values.
        """
        # Time complexity is O(u) for u usernames and that of len() is O(1)
        return sum(sample.values()) / len(sample)

    def getMedian(self, unsorted):
        """
        This function calculates the median of a given sample. The sample
        should be in the form of dictionary, where key is the useranme
        and value is the number of tweet associated to the username. It
        will call a helper function quickSelect()
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

    # Return the smallest kth item of the list using the quick select algo
    def quickSelect(self, unsortedList, k):
        """
        This function returns the smallest kth item of an unsorted list
        using quick select algorithm. The algorithm is in a recursive
        fashion. Complexity O(log(u))
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
        This function returns pivot position that partitions the list of
        the first list item. Complexity O(n)
        """
        # initialize pivot
        pivot = unpartitionedList[0]
        # initialize pivot position
        pivotPosition = 0
        for i in range(1, len(unpartitionedList)):
            if unpartitionedList[i][1] < pivot[1]:
                # update pivot position
                pivotPosition += 1
                # swaping the position of unpartitionedList[i] and unpartitionedList[pivotPosition]
                unpartitionedList[i], unpartitionedList[pivotPosition] = \
                    unpartitionedList[pivotPosition], unpartitionedList[i]
            # swaping the position of unpartitionedList[0] and unpartitionedList[pivotPosition]
        unpartitionedList[0], unpartitionedList[pivotPosition] = \
            unpartitionedList[pivotPosition], unpartitionedList[0]
        # return pivot position
        return pivotPosition

    def getTweetCounter(self, tempTweetCounter):
        i = 0
        for tweet in self.allTweets():
            i += 1
            if i % 10000 == 0:
                print(i)
            if tweet['userName'] in tempTweetCounter.keys():
                tempTweetCounter[tweet['userName']] += 1
            else:
                tempTweetCounter[tweet['userName']] = 1
                # return tweetCounter

    def getTfCounter(self, tfCounter):
        for tweet in self.allTweets():
            terms = re.split('\W+', tweet['tweetText'].lower())
            for term in terms:
                if term in tfCounter[tweet['userName']].keys():
                    tfCounter[tweet['userName']][term] += 1
                else:
                    tfCounter[tweet['userName']][term] =0

    def getDfCounterHelper(self, dfCounterHelper):
        for tweet in self.allTweets():
            terms = re.split('\W+', tweet['tweetText'].lower())
            for term in terms:
                if term in dfCounterHelper.keys():
                    dfCounterHelper[term].add(tweet['userName'])
                else:
                    dfCounterHelper[term] = set().add(tweet['userName'])

    def main(self):
        timer = {"start": time.time()}
        tweetCounter = defaultdict(int)
        tfCounter = defaultdict(lambda: defaultdict(int))
        dfCounterHelper = defaultdict(set)
        with Manager() as manager:
            # manager.register('defaultdict', defaultdict, DictProxy)
            # tempTweetCounter = manager.defaultdict
            tempTweetCounter = manager.dict()
            tempTfCounter = manager.dict()
            tempDfCounterHelper = manager.dict()
            p1 = Process(target=self.getTweetCounter, args=(tempTweetCounter, ))
            p2 = Process(target=self.getTfCounter, args=(tempTfCounter, ))
            p3 = Process(target=self.getDfCounterHelper, args=(tempDfCounterHelper, ))
            p1.start()
            p2.start()
            p3.start()
            p1.join()
            p2.join()
            p3.join()
            tweetCounter.update(tempTweetCounter)
            tfCounter.update(tempTfCounter)
            dfCounterHelper.update(tempDfCounterHelper)
        # tweetCounter = self.getTweetCounter()
        # t3 = time.time()
        # print("tweet: " + str(t3-t2))
        # t4 = time.time()
        # print("tf " + str(t4-t3))
        # dfCounterHelper = self.getDfCounterHelper()
        # t5 = time.time()
        # print("dfHelper: " + str(t5-t4))

        dfCounter = defaultdict(int)

        print("number of tweets counter: " + str(len(tweetCounter)))
        timer["DoneProcessingTweets"] = time.time()
        print("Processing time: " + str(timer["DoneProcessingTweets"] - timer["start"]))
        # -------------------------------------------------------
        # --------- construct document frequency dictionary ---------
        for key, value in dfCounterHelper.iteritems():
            dfCounter[key] = len(value) + dfValueBuffer
            # -----------------------------------------------------------
        print("Mean: " + str(self.getMean(tweetCounter)))

        print("Median: " + str(self.getMedian(tweetCounter)[1]) + " ("
              + self.getMedian(tweetCounter)[0] + ")")

        print("Top " + str(topUserThreshold) + " users: "
              + str(tweets.getTopItems(tweetCounter.items(), topUserThreshold)))

        for userName in validUser:
            if userName in tfCounter.keys():
                # obtain term frequency dictionary of a specific user
                tf = tfCounter[userName]
                # initialize tfIdf dictionary for each user
                tfIdf = {}
                for term, frequency in tf.iteritems():
                    # if the number of tweets surpass certain point threshold
                    if dfCounter[term] > dfThreshold:
                        # calculate tfIdf for each term
                        tfIdf[term] = 1.0 * frequency / dfCounter[term]
                print(userName + "'s " + "most interesting words: " + str(self.getTopItems(tfIdf.items(), 20)))
            else:
                print(userName + " does not exist")
        timer["Done"] = time.time()
        print("Running time: " + str(timer["Done"]-timer["start"]) + " seconds\nProcessing time: "
              + str(timer["DoneProcessingTweets"]-timer["start"]) + " seconds\nOthers: "
              + str(timer["Done"]-timer["DoneProcessingTweets"]) + " seconds")
        return None



if __name__ == "__main__":
    smallTweet = "/home/ilps/Downloads/COMP432/h0/tweets.100k"
    largeTweet = "/home/ilps/Downloads/COMP432/h0/tweets.large"
    topUserThreshold = 100
    validUser = ['rdematos', 'mccook', 'CatholicHawaii', 'mirnacavalcanti', 'HugoFeijo', 'bonniejpreston']
    dfValueBuffer = 5
    dfThreshold = 10
    tweets = Tweets(smallTweet)
    # tweets = Tweets(largeTweet)
    tweets.main()
    # for item  in tweets.allTweets():
    #     pass
