"""
Author: Yulun Li

Combined the tags by root domains, so "http://pandora.com" and "http://www.pandora.com" have their tags combined.
Thus we get 259 urls with more than 700 tag applications, rather than 256 urls.

Movie clustering most representative results (5 clusters, freqThreshold 250,smoothingThreshold 3):
Cluster 1: theopencd.org, softwarefor.org, filehippo.com, 100-downloads.com, tinyapps.org
Cluster 2: pandora.com, last.fm, magnatune.com, radioblogclub.com, webjay.org
Cluster 3: yubnub.org, ning.com, squidoo.com, webserver001.goowy.com, 37signals.com
Cluster 4: subtraction.com, veerle.duoh.com, mezzoblue.com, kottke.org, 9rules.com
Cluster 5: script.aculo.us, dojotoolkit.org, mochikit.com, prototype.conio.net, jquery.com

Tag clustering most representative results (5 clusters, freqThreshold 250,smoothingThreshold 3):
Cluster 1: howto, reference, tutorial, tutorials, graphics
Cluster 2: music, radio, mp3, musica, streaming
Cluster 3: webdev, web, webdesign, css, webdevelopment
Cluster 4: software, freeware, windows, utilities, free
Cluster 5: blog, daily, technology, tech, news

Added method getTopMembers so that we print out the 5 members in the cluster that are the closest to the centroid.

Added smoothingThreshold so that the tags that have been applied fewer times than that will be ignored.
Running the data with 250 freqThreshold rather than 700, but it can go lower as well.

Used matplotlib to print out the average similarity score
of all the members of the cluster to the respective centroid.
The graph we attached is the average sim score from 1 cluster to 60 clusters for urls.
Seen from the graph, as the number of clusters increases,
the marginal increase in the sum of similarities decreases.
"""

__author__ = 'Yulun Li'

from collections import defaultdict
import math
import platform
import random
import urlparse


class Cluster():
    """
    Cluster type has a centroid and a dictionary of members.
    Each member has a dictionary of items mapped to their number of appearances.
    For example, to cluster urls, a member is an url and its items are the tags applied to it.
    To cluster tags, a member is a tag and its items are the urls that have been applied with the tag.
    """

    def __init__(self):
        self.centroid = {}
        self.members = {}

    def clearMembers(self):
        # Reset members of the cluster.
        self.members.clear()

    def clearCentroid(self):
        # Reset centroid
        self.centroid.clear()

    def addMember(self, member, items):
        self.members[member] = items


class KMeans():
    NUM_ITERATE = 10
    MAX_NUM_CLUSTERS = 60

    def __init__(self, tagsDir, logPath, clusterUrls, freqThreshold, smoothingThreshold):
        self.tagsDir = tagsDir
        self.logPath = logPath
        self.toBeClustered = self.getToBeClustered(clusterUrls, freqThreshold, smoothingThreshold)

    def getDomain(self, url):
        # Return the domain name of a url and naively resolve urls with subdomain name "www".
        domain = urlparse.urlparse(url).netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain

    def getToBeClustered(self, clusterUrls, freqThreshold, smoothingThreshold):
        # Return a dictionary with urls and their tags as a child dictionary.
        tempToBeClustered = defaultdict(lambda: defaultdict(float))
        with open(self.tagsDir, 'r') as tagsFile:
            for line in tagsFile:
                tokens = line.split("\t")
                if len(tokens) >= 4:
                    url, tag = self.getDomain(tokens[2]), tokens[3].lower().rstrip("\n")
                    # Either cluster urls or tags.
                    if clusterUrls:
                        tempToBeClustered[url][tag] += 1
                    else:
                        tempToBeClustered[tag][url] += 1
        toBeClustered = {}
        deleteKeys = []
        for key, value in tempToBeClustered.iteritems():
            if sum(value.values()) >= freqThreshold:
                # For smoothing, delete items fewer than threshold.
                deleteInner_Keys = []
                for inner_key in value:
                    if value[inner_key] < smoothingThreshold:
                        deleteInner_Keys.append(inner_key)
                for deleteInner_Key in deleteInner_Keys:
                    del value[deleteInner_Key]
                toBeClustered[key] = value
                # Record members that don't have items after smoothing.
                if len(value) == 0:
                    deleteKeys.append(key)
        for deleteKey in deleteKeys:
            del toBeClustered[deleteKey]
        print("Ready to cluster " + str(len(toBeClustered)) + (" urls" if clusterUrls else " tags"))
        return toBeClustered

    def similarity(self, vector1, vector2):
        # Returns the cosine similarity of two vectors of type dict.
        xDotX, xDotY, yDotY = 0, 0, 0
        for key, value in vector1.iteritems():
            if key in vector2:
                xDotY += vector1[key] * vector2[key]
        xDotX = sum([i ** 2 for i in vector1.values()])
        yDotY = sum([i ** 2 for i in vector2.values()])
        similarity = xDotY / math.sqrt(xDotX * yDotY)
        return similarity

    def getCentroid(self, cluster):
        # Returns the centroid of a cluster.
        centroid = defaultdict(float)
        for key, value in cluster.iteritems():
            for inner_key, inner_value in value.iteritems():
                centroid[inner_key] += inner_value
        for key, value in centroid.iteritems():
            centroid[key] /= len(cluster)
        return centroid

    def getClusters(self, numClusters, numIterate):
        # Return sum of similarity scores of each iteration as a list and clusters.
        clusters = []
        sumOfSims = []  # After each iteration, the sum of sim scores will be saved here.
        keys = self.toBeClustered.keys()
        random.shuffle(keys)
        for j in range(numIterate + 1):
            # print("Number of iteration: " + str(j) + "/" + str(numIterate) if j > 0 else "Loading clusters...")
            sumOfSim = 0
            if len(clusters) != 0:
                # Do this for each iteration.
                for member, items in self.toBeClustered.iteritems():
                    tempSims = []
                    for cluster in clusters:
                        tempSims.append(self.similarity(items, cluster.centroid))
                    a = tempSims.index(max(tempSims))
                    clusters[a].addMember(member, items)
                    sumOfSim += max(tempSims)
            else:
                # Do this when each cluster is still empty.
                for i in range(numClusters):
                    clusters.append(Cluster())
                for i in range(len(keys)):
                    k = i % numClusters
                    clusters[k].addMember(keys[i], self.toBeClustered[keys[i]])
            for cluster in clusters:
                if len(cluster.members) != 0:
                    # Reset centroid only if there are members.
                    cluster.centroid = self.getCentroid(cluster.members)
                if j < numIterate:
                    # Reset members unless it's the last iteration.
                    cluster.clearMembers()
            if sumOfSim != 0:
                sumOfSims.append(sumOfSim)
        return sumOfSims, clusters

    def getTopMembers(self, cluster):
        """
        Return the most representative members in a cluster
        as a list of tuples of item name and sum of similarity scores from the centroid.
        """
        unsortedResult = []
        for member, tags in cluster.members.iteritems():
            unsortedResult.append((member, self.similarity(tags, cluster.centroid)))
        return sorted(unsortedResult, key=lambda result: result[1], reverse=True)[:5]

    def plotAverageSim(self):
        # Plot the average of similarity score of a cluster that's below MAX_NUM_CLUSTERS.
        scores = []
        for i in range(1, self.MAX_NUM_CLUSTERS):
            result = self.getClusters(i, self.NUM_ITERATE)
            tempSum = 0
            for cluster in result[1]:
                tempSum += len(cluster.members)
            scores.append(result[0][-1] / tempSum)
        import matplotlib.pyplot as plt

        plt.plot(scores)
        plt.show()

    def main(self):
        # clusters = self.getClusters(5, self.NUM_ITERATE)[1]
        # for i in range(len(clusters)):
        #     result = self.getTopMembers(clusters[i])
        #     print("Cluster " + str(i + 1) + ": " + ", ".join([item[0] for item in result]))

        self.plotAverageSim()


def resolveBaeDir():
    # Specify your baseDir
    if 'Darwin' in platform.uname()[0]:
        return ""
    elif 'Linux' in platform.uname()[0]:
        return "/home/ilps/Downloads/COMP432/h2/"
    elif 'Windows' in platform.uname()[0]:
        return "C:\\Users\\Yu\\Downloads\\"
    else:
        return ""


if __name__ == "__main__":
    filename = "tag_apps.txt"
    fileDirs = [resolveBaeDir() + filename, "log"]
    clusterUrls = True
    freqThreshold = 250
    smoothingThreshold = 3
    km = KMeans(fileDirs[0], fileDirs[1], clusterUrls, freqThreshold, smoothingThreshold)
    km.main()