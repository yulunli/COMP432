from collections import defaultdict
import random
import re
import stackoverflow
import datetime

__author__ = 'Yulun Li'


class AnalyzeSo():
    USA_WORDS = ['us', 'usa', 'united states of america', 'alabama', 'al', 'alaska', 'ak', 'arizona', 'az', 'arkansas',
                 'ar', 'california', 'ca', 'colorado', 'co', 'connecticut', 'ct', 'delaware', 'de', 'florida', 'fl',
                 'georgia', 'ga', 'hawaii', 'hi', 'idaho', 'id', 'illinois', 'il', 'indiana', 'in', 'iowa', 'ia',
                 'kansas', 'ks', 'kentucky', 'ky', 'louisiana', 'la', 'maine', 'me', 'maryland', 'md',
                 'massachusetts', 'ma', 'michigan', 'mi', 'minnesota', 'mn', 'mississippi', 'ms', 'missouri', 'mo',
                 'montana', 'mt', 'nebraska', 'ne', 'nevada', 'nv', 'new hampshire', 'nh', 'new jersey', 'nj',
                 'new mexico', 'nm', 'new york', 'ny', 'north carolina', 'nc', 'north dakota', 'nd', 'ohio', 'oh',
                 'oklahoma', 'ok', 'oregon', 'or', 'pennsylvania', 'pa', 'rhode island', 'ri', 'south carolina', 'sc',
                 'south dakota', 'sd', 'tennessee', 'tn', 'texas', 'tx', 'utah', 'ut', 'vermont', 'vt',
                 'virginia', 'va', 'washington', 'wa', 'west virginia', 'wv', 'wisconsin', 'wi', 'wyoming', 'wy',
                 'redmond']

    def __init__(self):
        if stackoverflow.hasCachedFile():
            self.so = stackoverflow.readFromCache()
        else:
            self.so = stackoverflow.readAll(True)
            stackoverflow.writeToCache(self.so)

    def getUsers(self):
        validUserId = [user.id for user in self.so.users]
        activeUserId = []

        validUserPostContrib = defaultdict(int)
        for post in self.so.posts:
            if post.userId in validUserId:
                validUserPostContrib[post.userId] += 1
        validUserPostResult = self.plotLorenz(validUserPostContrib)
        print(validUserPostResult[0], validUserPostResult[2][:2])
        # validUserPostResult[1].show()
        activeUserId.extend(validUserPostResult[2][2])

        validUserCommentContrib = defaultdict(int)
        for comment in self.so.comments:
            if comment.userId in validUserId:
                validUserCommentContrib[comment.userId] += 1
        validUserCommentResult = self.plotLorenz(validUserCommentContrib)
        print(validUserCommentResult[0], validUserCommentResult[2][:2])
        # validUserCommentResult[1].show()
        activeUserId.extend([user for user in validUserPostResult[2][2] if user not in activeUserId])
        inactiveUserId = [user.id for user in self.so.users if user.id not in activeUserId]

        self.analyzeUserGroup(activeUserId)
        # self.analyzeUserGroup(inactiveUserId)

        return None

    def analyzeUserGroup(self, userIds):
        users = [self.getUser(userId) for userId in userIds]
        averageAge = sum([user.age for user in users]) / len(users)
        averageReputation = sum([user.reputation for user in users]) / len(users)
        averageViews = sum([user.views for user in users]) / len(users)
        averageNetScore = sum([(int(user.up) - int(user.down)) for user in users]) / len(users)
        locations = [user.location.lower() for user in users]
        percentLocationUnknown = sum([1.0 for location in locations if location == "unknown"]) / len(locations)
        usaLocations = 0.0
        for location in locations:
            isUS = 0
            for place in location.split(","):
                if place.strip() in self.USA_WORDS:
                    isUS = 1
            usaLocations += isUS
        percentLocationInUS = usaLocations / len(locations)
        averageTimeDistance = sum([(datetime.datetime.strptime(" ".join(user.creation.split("T")[0].split("-")),
                                                               "%Y %m %d") - datetime.datetime.today()).days for user in
                                   users]) / len(users)
        averageCreationDate = (datetime.datetime.today() + datetime.timedelta(days=averageTimeDistance)).date()
        year, month, date = averageCreationDate.year, averageCreationDate.month, averageCreationDate.day
        aboutStringLength = []
        for user in users:
            aboutString = re.sub(r'[\n\r]+', ' ', user.about)
            aboutString = re.sub(r'[^\s\w_]+', ' ', aboutString).lower().strip()
            aboutStringLength.append(len(aboutString.split()))
        averageAboutStringLength = sum(aboutStringLength) / len(aboutStringLength)
        print("Number of users: " + str(len(userIds)))
        print("Average age: " + str(averageAge))
        print("Average reputation: " + str(averageReputation))
        print("Average Views: " + str(averageViews))
        print("Average net score: " + str(averageNetScore))
        print("Percentage indicating 'unknown'" + str(percentLocationUnknown))
        print("Percentage indicating US: " + str(percentLocationInUS))
        print("Average date creating account: " + str(year) + " " + str(month) + " " + str(date))
        print("averageAboutStringLength: " + str(averageAboutStringLength))

    def getUser(self, userId):
        for user in self.so.users:
            if user.id == userId:
                return user
        return None

    def plotLorenz(self, valueDict):
        total = sum(valueDict.values())
        sortedList = sorted(valueDict.values())
        step = 1.0 / len(valueDict)
        cumulative = 0.0
        i = 0.0
        percent = [0.0]
        distribution = [0.0]
        inequalityDistance = [0.0]
        for value in sortedList:
            i += 1
            percent.append(i / len(valueDict))
            cumulative += value
            distribution.append(cumulative / total)
        areaUnderLorenz = 0.0

        for i in range(1, len(percent)):
            inequalityDistance.append(percent[i] - distribution[i])
            areaUnderLorenz += (distribution[i] + distribution[i - 1]) * step / 2
        gini = 1 - areaUnderLorenz * 2
        activeCutoff = inequalityDistance.index(max(inequalityDistance))
        activeUsers = [user for user in valueDict if valueDict[user] >= sortedList[activeCutoff]]
        import matplotlib.pyplot as plt

        plt.plot(percent, distribution)
        return gini, plt, (1 - activeCutoff / float(len(valueDict)), 1 - distribution[activeCutoff], activeUsers)

    def getArff(self):
        testSize = 99999
        answers = []
        acceptedAnswers = []
        unacceptedAnswers = []

        featureKeys = [
            # "answerId",
            "numAnswers",
            "accepted",
            "answerNumWords",
            "answerIntervalDays",
            "answerIsTopScore",
            "answerScore",
            "answerNumLines",
            "answerNumComments",
            "answerNormalizedText",
            "userReputation",
            "userScore",
            "userViews",
            "textNumSlashes",
        ]
        features = {}
        for featureKey in featureKeys:
            features[featureKey] = []

        for post in self.so.posts:
            if isinstance(post, stackoverflow.Question):
                for answer in post.answers:
                    answer.question = post
                    if answer.isAccepted:
                        acceptedAnswers.append(answer)
                    else:
                        unacceptedAnswers.append(answer)
        print("Ima done!")
        # random.shuffle(acceptedAnswers)
        # random.shuffle(unacceptedAnswers)
        answers.extend(acceptedAnswers[:testSize])
        answers.extend(unacceptedAnswers[:testSize])
        for answer in answers:
            question = answer.question
            questionAnswers = question.answers

            # features["answerId"].append(answer.id)
            features["numAnswers"].append(len(questionAnswers))
            features["accepted"].append(answer.isAccepted)

            answerString = answer.text
            normalizedAnswerString = re.sub(r'[\n\r]+', ' ', answerString)
            normalizedAnswerString = re.sub(r'[^\s\w_]+', ' ', normalizedAnswerString).lower().strip()
            if "\r" in normalizedAnswerString:
                print normalizedAnswerString
            answerNumWords = len(normalizedAnswerString.split())
            trimmedAnswerNumWords = answerNumWords if answerNumWords < 500 else 500
            features["answerNumWords"].append(trimmedAnswerNumWords)

            questionCreationDate = datetime.datetime.strptime(
                " ".join(question.creation.split("T")[0].split("-")),
                "%Y %m %d")
            answerCreationDate = datetime.datetime.strptime(
                " ".join(answer.creation.split("T")[0].split("-")),
                "%Y %m %d")
            answerIntervalDays = (answerCreationDate - questionCreationDate).days
            trimmedAnswerIntervalDays = answerIntervalDays if answerIntervalDays < 120 else 120
            features["answerIntervalDays"].append(trimmedAnswerIntervalDays)

            answerScores = [int(questionAnswer.score) for questionAnswer in questionAnswers]
            answerScore = float(answer.score)
            features["answerIsTopScore"].append(answerScore == max(answerScores) and max(answerScores) > 0)

            features["answerScore"].append(answerScore)

            answerNumLines = len(answer.text.split("\n"))
            trimmedAnswerNumLines = answerNumLines if answerNumLines < 350 else 350
            features["answerNumLines"].append(trimmedAnswerNumLines)

            features["answerNumComments"].append(len(answer.comments))
            features["answerNormalizedText"].append("'" + normalizedAnswerString + "'")

            userReputation = answer.user.reputation if answer.user is not None else -1
            features["userReputation"].append(userReputation)

            userScore = int(answer.user.up) - int(answer.user.down) if answer.user is not None else 0
            features["userScore"].append(userScore)

            userViews = answer.user.views if answer.user is not None else -1
            userViews = userViews if userViews < 2500 else 2500
            features["userViews"].append(userViews)

            textNumSlash = len(re.compile(r'/').findall(answer.text))
            trimmedTextNumSlash = textNumSlash if textNumSlash < 10 else 10
            features["textNumSlashes"].append(trimmedTextNumSlash)

        features["userScore"] = self.normalizeUserScores(features["userScore"])

        users = self.transpose([features[feature] for feature in featureKeys])

        with open("so.arff", 'w') as arffFile:
            arffFile.write('''@RELATION so

% @ATTRIBUTE answerID numeric
@ATTRIBUTE numAnswers numeric
@ATTRIBUTE accepted {True,False}
@ATTRIBUTE answerNumWords numeric
@ATTRIBUTE answerIntervalDays numeric
@ATTRIBUTE answerIsTopScore {True,False}
@ATTRIBUTE answerScore numeric
@ATTRIBUTE answerNumLines numeric
@ATTRIBUTE answerNumComments numeric
@ATTRIBUTE answerNormalizedText string
@ATTRIBUTE userReputation numeric
@ATTRIBUTE userScore {-1, 0, 1, 2}
@ATTRIBUTE userViews numeric
@ATTRIBUTE textNumSlashes numeric

@DATA\n''')
            for user in users:
                arffFile.write(",".join([str(value) for value in user]) + "\n")

    def transpose(self, matrix):
        matrixT = []
        for i in range(len(matrix[0])):
            matrixT.append([])
        for row in matrix:
            for col in range(len(row)):
                matrixT[col].append(row[col])
        return matrixT

    def normalizeUserScores(self, scores):
        normalizedScores = []
        sortedScores = sorted(scores)
        cutoff = sortedScores[int(len(scores) * 0.8)]
        if isinstance(scores, list):
            for score in scores:
                if score < 0:
                    normalizedScores.append(-1)
                elif score < 1:
                    normalizedScores.append(0)
                elif score < cutoff:
                    normalizedScores.append(1)
                else:
                    normalizedScores.append(2)
        return normalizedScores

    def main(self):
        # self.getUsers()
        self.getArff()


if __name__ == '__main__':
    analyzeSo = AnalyzeSo()
    analyzeSo.main()
