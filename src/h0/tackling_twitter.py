import pprint
import collections
import operator
import re
import math
import time

"""
Author: Zixiao Wang
"""

class Twitter_Tackler:

    def __init__(self, fname):
        self.fname = fname

        #self.userToTweet = collections.defaultdict(set) #set of record_id for each user
        #self.articles = collections.defaultdict(str) #record_id to text

    def readTweets(self):
        """
            This method reads in the tweets texts
            and yield tweet.

            dictionary tweetInfo is yield to the caller:
            {
                timestamp -> timestamp of the tweet
                record_id -> id of the tweet
                username -> identifier for each user
                text -> content of the tweet
            }
        """
        print "Reading Twitter Data ..."
        with open(self.fname,'r') as f:
            for line in f:
                try:
                    content = line.rstrip("\n")
                    if content[-1] != '\\':
                        tweetInfo = self.parseTweet(content)
                        if len(tweetInfo) == 4:
                            yield tweetInfo
                except Exception:
                    print "Error occurred when reading"
        print "Twitter Data Loaded"

    def smartReadTweets(self):
        """
            Extra Credit 2: handle multi-line tweets

            This method reads in the tweets texts
            and yield tweet. It does handles multi-line tweets

            You can uncomment the last print statement to test it.

            dictionary tweetInfo is yield to the caller:
            {
                timestamp -> timestamp of the tweet
                record_id -> id of the tweet
                username -> identifier for each user
                text -> content of the tweet
            }
        """
        print "Reading Twitter Data ..."
        with open(self.fname,'r') as f:
            whole = "" #captures the whole text for multi line
            for line in f:
                try:
                    content = line.rstrip("\n")
                    if content[-1] != '\\' and whole == '': #clean line, go ahead
                        tweetInfo = self.parseTweet(content)
                        if len(tweetInfo) == 4:
                            yield tweetInfo
                    elif content[-1] == '\\': #lines before last line
                        whole += " "+content.rstrip('\\')
                        #print "middle line %s" % content
                    else: #last line, parse and load
                        whole += " "+content
                        #print "last line %s" % content
                        tweetInfo = self.parseTweet(whole)
                        whole = "" # resetting whole
                        if len(tweetInfo) == 4:
                            yield tweetInfo
                            #print tweetInfo
                except Exception:
                    print "Error occurred when reading"
        print "Twitter Data Loaded"


    def parseTweet(self, content):
        """
            This method parse and store each tweet in the dictionary
        """
        texts = content.split("\t")
        tweetInfo = {}
        if len(texts) == 4:
            tweetInfo = {"timestamp":texts[0],"record_id":texts[1],"username":texts[2],"text":texts[3]}
        return tweetInfo

    def countTweets(self):
        count = 0
        with open(self.fname,'r') as f:
            whole = ""
            for line in f:
                try:
                    content = line.rstrip("\n")
                    if content[-1] != '\\' and whole == "": #clean line, go ahead
                        count+=1
                    elif content[-1] == '\\': #lines before last line
                        whole += "a" #dummy content
                    else: #last line, parse and load
                        count+=1
                        whole = ""
                except Exception:
                    print "Error occurred when reading"
        return count

    def tweetCountByUser(self):
        """
            Returns dictionary
            {
                key -> usernmae
                value -> count of tweets by the user
            }

            This method groups tweets by user.
            You can also get number of tweets for each user.

            The complexity is O(n), where n is the number of tweets.
            We are looping through each tweet, parse it
            and update the count for the specific user. The parsing 
            part takes constant time and because we are using dictionary
            (hashmap), updating counts also takes constant time.
        """

        """
            The advantage of using defaultdict is that we can
            pass it a function whose return value is the default 
            value for key that has uninitialized value.

            In our case, we initialize integer 0 as the default value
            by passing int() function. If were using the standard
            dictionary, we need to have a try/except block to 
            deal with the unintialized value.
        """
        countInfo = collections.defaultdict(int)
        #for tweet in self.readTweets():
        for tweet in self.smartReadTweets():
            user = tweet['username']
            countInfo[user]+=1
        return countInfo

    def analyze(self):
        """
            Extra Credit 4: finding mean takes me O(n) where n is the number of tweets

            Returns dictionary with two fixed keys
            {
                key1 mean -> mean number of tweets per user
                key2 median -> median number of tweets per user
            }

            Analysis 1 Result:
            mean number of tweets per user: 28

            This method completes the first 
            analysis (part 3) of the homework.

            It uses countTweetByUser() function,
            which has complexity of O(n) where n
            is the number of tweet, to get the total
            number of tweets for each user.

            The number of keys in dictionary 
            returned by countTweetByUser() gives us
            the number of user, u.

            To find the mean, we use the total number of tweets,n,
            divided by the number of user, u. This takes constant
            time provided that both n and u exists.

            Here both tweetCountByUser() and countTweets() takes O(n) time to complete,
            but the complexity is still O(2n) = O(n)
            We can certainly combine both function to read
            in the tweets while doing all the work. But that does
            not seem to be a good design.

            Getting mean is a matter of using n divided by m, this takes constant time
            after find the value of n and m. 

            We can call topNActiveUser() m/2 to get the median. Function topNActiveUser()
            will take O(ulogu) to sort the user by the tweet counts if we have pre-constructed
            userCountInfo dictionary.

            Therefore, in total, the anaylsis above takes O(n+ulogu) where n is the number of
            tweets and u is the number of the users.

            Results:
            mean 28
            median 22

        """
        userCountInfo = self.tweetCountByUser()
        n = self.countTweets()
        m = len(userCountInfo)
        mean = n/m
        #print "Analysis 1(a): mean number of tweets per user is %d" % mean

        median = int(self.topNActiveUser(userCountInfo, m/2)[-1][1])
        #print "Analysis 1(b): median number of tweets per user is %d" % median
        #m = len(userCountInfo)
        #median= self.quickSelect(userCountInfo.items(), 0, m-1,m/2 )

        return {"mean": mean, "median":median}


    def topNActiveUser(self, userCountInfo, n):
        """
            param userCountInfo: the result of tweetCountByUser
            param n: the number of top users need
            Return top n (user_name, count) sorted by count

            The complexity of sorted() is O(ulog(u)) according python's documentation
            where u is the number of users.

            Reading in the data and construct userCountInfo takes O(n), where n is the number of tweets.
            The complexity of sorted() is O(ulog(u)) according python's documentation
            where u is the number of users.

            Therefore, in total, this method has complexity O(n+ulogu).

            Here are the top 100 users (A list of tuples):
            [('AlphaShooter', 99), ('Alaeddin', 97), ('candyaddict', 96), ('CatholicHawaii', 95), ('jrolstad', 95), ('210cm', 93), 
            ('NorthMetroSBDC', 93), ('JohnMorley', 93), ('duncangibbs', 93), ('jackygreen', 91), 
            ('savingstrangers', 91), ('DAVIDMOREEN', 91), ('Andrewdf', 91), ('NintendoPortal', 90), ('rdematos', 90), 
            ('colopy', 90), ('markshea', 90), ('MojoBanjo2008', 90), ('helenabouchez', 90), ('SaheliDatta', 90), 
            ('kyuzo', 90), ('kvoelker', 90), ('candie_pants', 90), ('jonoproctor', 90), 
            ('mitsukai', 90), ('mkraiderz', 90), ('mccook', 89), ('TWBCanada', 89), ('vipsphinx', 89), 
            ('brianvosburgh', 89), ('nixguy', 89), ('annezieger', 89), ('jenniferalaine', 89), 
            ('h8torade', 89), ('Jeffrey_Smith', 88), ('cecysnyder', 88), ('netinfluence', 88),
            ('cabarney', 88), ('ninad', 88), ('FERISHIA', 88), ('gbalnis', 88), ('infogoddes', 87), ('acquia', 87), 
            ('juliejones5998', 87), ('echofoxtrot', 87), ('gautamrishi', 87), ('X360A', 86), ('College_Mogul', 86),
            ('rsmudge', 86), ('tvnewsradio', 86), ('HondaWang', 86), ('stephensullivan', 85), ('allisoncoles', 85), 
            ('SeanWoodruff', 85), ('nathan_ives', 85), ('paulmdickey', 85), ('emptyhead', 85), ('smeranda', 85), 
            ('Circle909', 85), ('ruthlessorg', 84), ('dieselv2', 84), ('ossigeno', 84), ('SweetnLeo', 84), 
            ('montuschi', 84), ('andersljonsson', 84), ('TheRedMeanie', 84), ('benhoffman', 83), ('skeetermurphy', 83), 
            ('jake_grey', 83), ('PeggySue67', 83), ('tolifiers', 83), ('ArmandoCrespo', 83), ('TheLion', 83), ('alexspencer', 83), 
            ('jshalvi', 83), ('razorfrog', 83), ('LeeAndrew', 83), ('asmaam', 83), ('xolepino', 82), ('ericpursh', 82), 
            ('kris10good', 82), ('pisanojm', 82), ('jradoff', 82), ('cshirk', 81), ('TomHasselman', 81), ('abhatiauk', 81), 
            ('Know4LIFE', 81), ('Stormancast', 81), ('hopers', 81), ('think_sis', 81), ('gadhill', 81), ('gabevidal', 81), 
            ('onezerosix', 81), ('jbellanca', 80), ('domino1182', 80), ('marthamath', 80), ('djschultz', 80), 
            ('thewebwoman', 80), ('halcollins', 80), ('noexg', 80)]
        """
        sortedUserCount = sorted(userCountInfo.iteritems(), key=operator.itemgetter(1), reverse=True) #tuple here
        #print "Anaylsis 2: top 100 users "
        #print sortedUserCount[0:100]

        return sortedUserCount[0:n]

    def quickSelect(self, items, first, last, k):
        """
            Extra Credit 4: using QuickSelect for finding median
            This is partly working, it's close but the first k 
            items are not fully sorted
        """
        if first < last:
            pivot = self.partition(items, first, last)
            if (k < pivot-first):
                return self.quickSelect(items, first, pivot-1, k)
            elif (k > pivot):
                return self.quickSelect(items, pivot+1, last, k-pivot)
            else:
                return items[k]

    def partition(self, items, first, last):
        p = items[first][1]
        i = first
        for j in range(first + 1,last + 1):
            if items[j][1] <= p:
                i = i + 1
                items[j], items[i] = items[i], items[j]
        items[first], items[i] = items[i], items[first]
        return i

    def allDocs(self):
        """
            Generate document for all users
            by collecting a list of text tweeted by the user
        """
        print "Generating Document ..."
        corpus = collections.defaultdict(list)

        #for tweet in self.readTweets():
        for tweet in self.smartReadTweets():
            #Getting basic info
            text = tweet['text'] # get contents
            user = tweet['username'] #get username
            text_list = self.split(text)

            #Building dictionary
            corpus[user].extend(text_list)

        print "Document Done "
        return corpus

    def dateAnaylsis(self):
        """
            Extra Credit 3: not finished 
            Find the number of tweets 
            per day of year, 
            per day of week, 
            per hour of day.
        """
        tweetByDate = collections.defaultdict(lambda: collections.defaultdic(lambda: collections.defaultdic))

        for tweet in self.smartReadTweets():
            #Getting basic info
            time = tweet['timestamp'] # get contents



    def wordDocMaps(self, allDocs):
        """
            return {"wtdMap":wtdMap, "dtwMap": dtwMap}

            wtdMap - wordToDocument dictionary
            {
                key -> word
                value -> set of docs that has the word
            }

            dtwMap - documentToWord dictionary
            {
                key -> username (document unique to each user)
                value -> set of words that used by the user
            }
        """
        wtdMap = collections.defaultdict(set)
        dtwMap = collections.defaultdict(set)
        for (user,doc) in allDocs.items():
            for w in doc:
                dtwMap[user].add(w)
                wtdMap[w].add(user)
        return {"wtdMap":wtdMap, "dtwMap": dtwMap}

    def dfForUser(self, username, allDocs):
        """
            Return document frequencies for each word in
            a user's document
        """
        wordDfMap = collections.defaultdict(int)
        doc = allDocs[username]
        for word in doc:
            wordDfMap[word]+=1
        return wordDfMap

    def dfForAllUsers(self, wordDocMaps):
        """
            Return document frequencies for each word in corpus
            for all users
        """
        wordDfMap = collections.defaultdict(int)

        for w in wordDocMaps['wtdMap']:
            wordDfMap[w] = len(wordDocMaps['wtdMap'][w])
        return wordDfMap

    def tfForUser(self, username, allDocs):
        """
            Return the term frequencies for the words by the user

            For each words in the user's document,
            we want to check with all the documents in coporus to see
            if it exits
        """
        wordTfMap = collections.defaultdict(int)
        doc = allDocs[username]
        for w in doc:
            wordTfMap[w]+=1

        return wordTfMap

    def topKWordsForUser(self, username, allDocs, wordDocMaps, k, extra=0, threshold=0):
        """
            param username: the username exsit in the twitter data
            param allDocs: a dictionary containing document for each use
                        we can run self.allDocs() to get the dictionary
            param k: the top k word we would like to get.
            param wordDocMaps: dictionary with two maps as values.
                            wtdMaps -> wordToDocument Mapping
                            dtwMaps -> documentToword Mapping
                            we can run self.wordDocMaps(allDocs) to get dictionary

            param extra: added to iterm frequency to control for rare words
            param threshold: set up for document frequency to control for rare words
            return a list of top k words sorted using Tf-Idf scores

            RESULTS (top 20):
            
            Because I have used the constant for term frequency and threshold for document frequency,
            scores from this program might be different from the normal TI-IDF scores. 
            To get the usual scores, run topKWordsForUser(u, allDocs, wdMaps, 20, 0, 0). Specifically,
            use 0 for the last two parameters.

            Running for user rdematos
            [('le_fino', 5.5), ('3275', 4.5), ('wuhan', 3.5), ('3282', 3.5), ('d700', 3.5), 
            ('080', 3.5), ('taipei', 2.5), ('ceseco', 2.5), ('36hrs', 2.5), ('tokyo', 2.0384615384615383), 
            ('24mm', 1.5), ('bikers', 1.5), ('s5cr', 1.5), ('s5cg', 1.5), ('1e0sp', 1.5), ('9556', 1.5), 
            ('1l3bb', 1.5), ('busan', 1.5), ('820', 1.5), ('lcahlander', 1.5)]

            Running for user mccook
            [('clearwire', 3.5), ('dobbsr', 2.5), ('thelostagency', 2.5), ('gegere', 2.25), ('gatekeeper', 1.5),
            ('sallymander', 1.5), ('6jbxk3', 1.5), ('5z6fbo', 1.5), ('raked', 1.5), ('leftyshields', 1.5), 
            ('grumpygrandma', 1.5), ('contrived', 1.5), ('4wlck', 1.5), ('peer2peer', 1.5), 
            ('working_mg', 1.5), ('hanger', 1.5), ('dune', 1.5), ('affective', 1.5), ('hithah', 1.5), ('busing', 1.5)]

            Running for user CatholicHawaii
            [('diocesan', 14.5), ('bishop', 7.75), ('catholichawaii', 7.5), ('diocese', 6.5), 
            ('silva', 4.5), ('canonization', 4.5), ('pastoral', 4.5), ('presbyteral', 4.5), 
            ('parish', 3.8333333333333335), ('kalaupapa', 3.5), ('synod', 3.5), 
            ('honolulu', 2.875), ('punahou', 2.5), ('philomena', 2.5), ('annos', 2.5), 
            ('papaikou', 2.5), ('multos', 2.5), ('pahala', 2.5), ('vicars', 2.5), ('maryknoll', 2.5)]

            Complexity Analysis:
            
            The overall complexity of the tf-idf rating 
            operation takes O(n+w+k+klogk), where
            n is the number of tweets, w is the number of words inside
            all users' documents, and k is the number of words inside 
            the document of the current user. In the case of the real
            data, n and w should dominate k.

            Before running this method, we need to precompute allDocs,
            which contains document for each user, and wordDocMaps, 
            which contains a map from word to document and another map
            from document to word.

            Function allDoc() has time complexity O(n), where n is the number
            of tweets. The for-loop inside allDoc() 
            function go through each line of the tweet,
            so it takes O(n), where n is the number of tweets. Finding
            user key in corpus takes constant time O(1) for the dictionary.
            Extending the array takes O(k) where k is the number of words
            in each tweet. Because of the size limit of the tweet, we can assume
            that k << n. Therefore, the overal run time of the allDoc() function
            is O(n).

            Function wordDocMaps has time complexity O(w), where w
            is the number of words inside the whole corpus. The outter for loop
            go throught all m items in allDocs, where m is the number 
            of the user, because each user has one and only one document. 
            The inner for loop go through each word in each document. We
            can treat the nested loop as a single loop going through all
            w words inside all documents. So the complexity of the nested 
            for loop is O(w). Because looking up in the dictionary and adding
            an item array takes constant time, the overall complexity of the
            function is O(w).

            Notice that because we compute allDocs and wordDocMaps before
            running this function, the complexity of two input parameters 
            if we want to find topKWords for more than one user.

            Inside this function, we first called dfForAllUsers(), which
            has complexity O(w). The for loop runs w iterations and the operation
            inside for loop takes constant time.

            Function tfForUser() has time complexity O(k), where k is the
            number of words in the user's document. Inside the for
            loop, which runs k iterations, looking up the key
            in wordTfMap dictionary and updating it takes constant time.

            The for loop inside the current function runs k iterations, where k is 
            the number of words in the user's document. All computation inside
            the for loop takes constant time. So the complexity of the for
            loop is O(k).

            Because the dictionary tf_idf always has k or less times. Sorting
            the dictionary using the built-in sorted() function takes 
            klogk.

            In conclusion, the overall complexity of the tf-idf rating 
            operation takes O(n+2w+2k+klogk) = O(n+w+k+klogk), where
            n is the number of tweets, w is the number of words inside
            all users' documents, and k is the number of words inside 
            the document of the current user.
        """
        dfMap = self.dfForAllUsers(wordDocMaps)
        #sortedDf = sorted(dfMap.iteritems(), key=operator.itemgetter(1), reverse=True) #tuple here
        #print sortedDf[0:20]


        tfMap = self.tfForUser(username,allDocs)
        #sortedTF = sorted(tfMap.iteritems(), key=operator.itemgetter(1), reverse=True) #tuple here
        #print sortedTF[0:20]

        tf_idf = collections.defaultdict(float)

        for (w,tf) in tfMap.items():
            if w in dfMap:
                df = dfMap[w]
                #print df
                #print tf
                #idf = math.log(float(n)/float(df))
                if(df > threshold):
                    tf_idf[w] = float(tf+extra) / float(df)

        sortedTf_idf = sorted(tf_idf.iteritems(), key=operator.itemgetter(1), reverse=True) #tuple here

        return sortedTf_idf[:k]


    def split(self, s):
        """
            Helper method for spliting tweet text
            Split by white space characters
        """
        return re.split('\W+', s.lower())

if __name__ == "__main__":
    t1 = time.time()
    # Running the small dataset
    baseDir = "/home/ilps/Downloads/COMP432/h0"
    smallTweetDir = "/tweets.100k"
    largeTweetDir = "/tweets.large"
    tackler = Twitter_Tackler(baseDir + largeTweetDir)
    print tackler.analyze()

    allDocs = tackler.allDocs()
    wdMaps = tackler.wordDocMaps(allDocs)
    print "number of user %d" % len(allDocs)

    usernames = ['rdematos', 'mccook', 'CatholicHawaii']
    for u in usernames:
        print "Running for user %s" % u
        tf_idf = tackler.topKWordsForUser(u, allDocs, wdMaps, 20, 0.5, 0.2)
        print tf_idf
        print ""
    t2 = time.time()
    print(t2-t1)
    # Extra Credit 1: Running the large dataset, it works!
    # In this dataset, the tweets for each user is group together.
    # In the small dataset, the tweets of the user are not necessarily grouped.
    """
    tackler = Twitter_Tackler("dat/tweets.large")
    allDocs = tackler.allDocs()
    wdMaps = tackler.wordDocMaps(allDocs)
    print "number of user %d" % len(allDocs)

    usernames = ['agentozzy','RoyLantu','arprice']
    for u in usernames:
        print "Running for user %s" % u
        tf_idf = tackler.topKWordsForUser(u, allDocs, wdMaps, 20, 0.5, 0.2)
        print tf_idf
        print ""
   """