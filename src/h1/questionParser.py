"""

This activity was developed by David Klock (now at Microsoft).

"""

import codecs
import random
import string

TYPE_INFORMATION = 'I'
TYPE_CONVERSATION = 'C'

class QuestionParser:
    def __init__(self, filename):
        self.questions = set()
        for line in codecs.open(filename, 'r', 'latin-1'):
            tokens = line.strip().split(" | ")
            if len(tokens) == 2:
                question = tokens[0]
                questionType = tokens[1]
                if questionType == 'I':
                    self.questions.add(Question(question, TYPE_INFORMATION))
                elif questionType == 'C':
                    self.questions.add(Question(question, TYPE_CONVERSATION))
                else:
                    raise TypeError("Question type must be I or C: %s" % line)

    def run(self):
        trueInfo, falseInfo, trueConv, falseConv = self.parseQuestions()
        trueInfoNum = len(trueInfo)
        allInfoNum = trueInfoNum + len(falseConv)
        trueConvNum = len(trueConv)
        allConvNum = trueConvNum + len(falseInfo)
        sensitivity = float(trueConvNum)/allConvNum
        specificity = float(trueInfoNum)/allInfoNum
        score = (sensitivity+specificity)*50
        print("\nTrueInfo:")
        for question in random.sample(trueInfo, min(len(trueInfo), 10)):
            print("\t%s" % question.questionString.replace(' xques', '?').replace(' xperi', '.').replace(' xcomm', ',').replace(' xexcl', '!'))
        print("\nTrueConv:")
        for question in random.sample(trueConv, min(len(trueConv), 10)):
            print("\t%s" % question.questionString.replace(' xques', '?').replace(' xperi', '.').replace(' xcomm', ',').replace(' xexcl', '!'))
        print("\nFalseInfo (conversational incorrectly classified as informational):")
        for question in random.sample(falseInfo, min(len(falseInfo), 10)):
            print("\t%s" % question.questionString.replace(' xques', '?').replace(' xperi', '.').replace(' xcomm', ',').replace(' xexcl', '!'))
        print("\nFalseConv (informational incorrectly classified as conversational):")
        for question in random.sample(falseConv, min(len(falseConv), 10)):
            print("\t%s" % question.questionString.replace(' xques', '?').replace(' xperi', '.').replace(' xcomm', ',').replace(' xexcl', '!'))
        print("")
        print("Statistics:")
        print("\tSensitivity (TrueConv/TotalConv): %f" % sensitivity)
        print("\tSpecificity (TrueInfo/TotalInfo): %f" % specificity)
        print("\tScore:                            %f" % score)

    def parseQuestions(self):
        trueInfo = set()
        falseInfo = set()
        trueConv = set()
        falseConv = set()
        for question in self.questions:
            parsedType = self.parseQuestion(question.questionString)
            if parsedType == TYPE_INFORMATION:
                if question.questionType == TYPE_INFORMATION:
                    trueInfo.add(question)
                else:
                    falseInfo.add(question)
            elif parsedType == TYPE_CONVERSATION:
                if question.questionType == TYPE_INFORMATION:
                    falseConv.add(question)
                else:
                    trueConv.add(question)
            else:
                raise TypeError("Question type must be TYPE_CONVERSATIONAL\
                                or TYPE_INFORMATIONAL, not %s" % parsedType.__repr__())
        return (trueInfo, falseInfo, trueConv, falseConv)

    # TODO: Fill me in!  This method takes a question string and
    # returns either TYPE_CONVERSATION or TYPE_INFORMATION.
    def parseQuestion(self, question):
        words = question.split(' ')
        indicator = 0
        if "how" in words or "i" in words:
            if "should" not in words:
                if "which" not in words:
                    indicator += 1

        return TYPE_INFORMATION if indicator == 1 else TYPE_CONVERSATION
        # info_words = ["how", "who", "what", "where", "when", "why"]
        # conv_words = ["i"]
        # info_score = 0
        # conv_score = 0
        # for info_word in info_words:
        #     if info_words in words:
        #         info_score += 1
        # for conv_word in conv_words:
        #     if conv_word in words:
        #         conv_score += 1
        # if info_score >= conv_score:
        #     return TYPE_INFORMATION
        # else:
        #     return TYPE_CONVERSATION



class Question:
    def __init__(self, questionString, questionType):
        self.questionString = questionString
        self.questionType = questionType

    def __repr__(self):
        returnString = ("Info" if self.questionType == TYPE_INFORMATION else "Conv")
        returnString += ": "
        returnString += self.questionString
        return returnString


if __name__ == "__main__":
    questionParser = QuestionParser("labeledQuestions.txt")
    questionParser.run()