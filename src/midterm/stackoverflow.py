#!/usr/bin/python -O
#
# A library that assists in analyzing the StackOverflow data dump.
# Created by Shilad Sen for Comp 440's Midterm Exam.
#


import cPickle
import gc
import os
import random
import re
import sys

from xml.dom.minidom import parseString

def hasCachedFile():
    return os.path.isfile('so.pickled')

def writeToCache(obj):
    f = open('so.pickled', 'w')
    cPickle.dump(obj, f)
    f.close()


def readFromCache():
    f = open('so.pickled', 'r')
    o = cPickle.load(f)
    f.close()
    return o


class StackOverflow:
    """A container for data in the StackOverflow website."""
    def __init__(self, users, posts, comments, questions):

        # A list of user objects in the filtered set of users
        self.users = users

        # A list of posts, each of which is a Question or an Answer object,
        # that are either asked or answered by users in the filtered set
        self.posts = posts

        # A list of comments by a) users in the filtered set, or b) about
        # posts in the filtered post set.  Note that not all these comments
        # will appear in the "comments" attribute of question or answer
        # object because comments by users in the filtered set may be about
        # posts not in the filtered set.
        self.comments = comments

        # A list of question objects in the filtered set.
        # You can traverse the questions by using the "answers"
        # attribute of question objects, or by using the comments
        # or user attributes of either questions or answers.
        # See example.py for more information.
        self.questions = questions

class User:
    """Respresents a StackOverflow user."""
    def __init__(self, xmlDoc):
        self.id = xmlAttr(xmlDoc, 'Id')                     # user id (a string)
        self.reputation = int(xmlAttr(xmlDoc, 'Reputation'))# score
        self.creation = xmlAttr(xmlDoc, 'CreationDate')     # date created
        self.name = xmlAttr(xmlDoc, 'DisplayName')          # username
        self.lastAccess = xmlAttr(xmlDoc, 'LastAccessDate') # last visited
        self.location = xmlAttr(xmlDoc, 'Location', 'Unknown')
        self.age = int(xmlAttr(xmlDoc, 'Age', -1))          # age, or -1
        self.views = int(xmlAttr(xmlDoc, 'Views'))          # num views, or 0
        self.up = xmlAttr(xmlDoc, 'UpVotes')                # num up-votes
        self.down = xmlAttr(xmlDoc, 'DownVotes')            # num down-votes
        self.about = stripHtml(xmlAttr(xmlDoc, 'AboutMe', ''))  # bio

def createQuestionOrAnswer(xmlDoc):
    """
        Creates either a question or an answer depending on the
        PostTypeId attribute.
    """
    if xmlAttr(xmlDoc, 'PostTypeId') == "1":
        return Question(xmlDoc)
    else:
        return Answer(xmlDoc)

class Question:
    """Represents a question (if postType == 1) or an answer to a question."""
    def __init__(self, xmlDoc):
        self.id = xmlAttr(xmlDoc, 'Id')                     # post id (a string)

        #  answer object for chosen by user as best (filled in afterwards)
        # May be None if no answer was accepted
        self.acceptedAnswer = None
    
        # a list of answer objects associated with this question
        self.answers = []

        # Comments associated with this question
        self.comments = []

        # User who created the question
        # May be None if the user isn't in the filtered set
        self.user = None

        # Miscellaneous attributes
        self.creation = xmlAttr(xmlDoc, 'CreationDate')
        self.score = xmlAttr(xmlDoc, 'Score')               # score
        self.views = int(xmlAttr(xmlDoc, 'ViewCount'))      # num views
        self.title = xmlAttr(xmlDoc, 'Title')
        self.numComments = int(xmlAttr(xmlDoc, 'CommentCount', 0))
        self.numFavorites = int(xmlAttr(xmlDoc, 'FavoriteCount', 0))

        # Textual content without html
        self.text = stripHtml(xmlAttr(xmlDoc, 'Body'))

        tagStr = xmlAttr(xmlDoc, 'Tags', '')             # list of tags
        if tagStr:
            self.tags = tagStr[1:-1].split('><')
        else:
            self.tags = []

        self.url = 'http://stackoverflow.com/questions/%s' % self.id

        # these attributes are only used during filtering and reading
        self.acceptedAnswerId = xmlAttr(xmlDoc, 'AcceptedAnswerId', -1)
        self.userId = xmlAttr(xmlDoc, 'OwnerUserId', -1)   # user id of creator


class Answer:
    """Represents a question (if postType == 1) or an answer to a question."""
    def __init__(self, xmlDoc):
        self.id = xmlAttr(xmlDoc, 'Id')                     # post id (a string)

        # The question object associated with this answer
        self.question = None
    
        # Whether or not this question was accepted as the best answer
        self.isAccepted = False

        # Comments associated with this answer
        self.comments = []

        # User who created the question
        # May be None if the user isn't in the filtered set
        self.user = None

        self.creation = xmlAttr(xmlDoc, 'CreationDate')
        self.score = xmlAttr(xmlDoc, 'Score')               # score
        self.views = int(xmlAttr(xmlDoc, 'ViewCount'))      # num views
        self.numComments = int(xmlAttr(xmlDoc, 'CommentCount', 0))
        self.numFavorites = int(xmlAttr(xmlDoc, 'FavoriteCount', 0))

        # Textual content with and without html
        self.text = stripHtml(xmlAttr(xmlDoc, 'Body'))

        tagStr = xmlAttr(xmlDoc, 'Tags', '')             # list of tags
        if tagStr:
            self.tags = tagStr[1:-1].split('><')
        else:
            self.tags = []

        # only used during filtering and reading
        self.parentId = xmlAttr(xmlDoc, 'ParentId')
        self.userId = xmlAttr(xmlDoc, 'OwnerUserId', -1)   # user id of creator

class Comment:
    """Represents a comment about a question or an answer """
    def __init__(self, xmlDoc):
        self.post = None    # Post (question or answer) associated with comment
        self.user = None    # 
        self.score = int(xmlAttr(xmlDoc, 'Score', 0))
        self.text = xmlAttr(xmlDoc, 'Text')

        # only used during filtering and reading
        self.postId = xmlAttr(xmlDoc, 'PostId')
        self.userId = xmlAttr(xmlDoc, 'UserId')


def readAll(readAllUsers=True):
    """
        Returns a StackOverflow object for files in the current directory.
        If readAllUsers is True, then reads in information about all users 
        so that most posts and comments will have a populated user field,
        even if those users are not in the filtered set.
    """
    users = readUsers('users.filtered.xml')
    posts = readPosts('posts.filtered.xml')
    comments = readComments('comments.filtered.xml')
    if readAllUsers:
        allUsers = readUsers('users.xml')
        questions = assemble(allUsers, posts, comments)
    else:
        questions = assemble(users, posts, comments)
    return StackOverflow(users, posts, comments, questions)

def readComments(file):
    comments = []
    for line in open(file):
        line = line.strip()
        if not line.startswith('<row'):
            continue
        xmlDoc = parseString(line)
        comment = Comment(xmlDoc)
        comments.append(comment)
        if len(comments) % 50000 == 0:
            sys.stderr.write('read %d comments\n' % len(comments))
    print 'total: read %d comments' % len(comments)
    return comments
        
def readUsers(file):
    users = []
    for line in open(file):
        line = line.strip()
        if not line.startswith('<row'):
            continue
        xmlDoc = parseString(line)
        user = User(xmlDoc)
        users.append(user)
        if len(users) % 50000 == 0:
            sys.stderr.write('read %d users\n' % len(users))
            gc.collect()
    sys.stderr.write('read a total of %d users\n' % len(users))
    gc.collect()
    return users
         
def readPosts(file):
    posts = []
    for line in open(file):
        line = line.strip()
        if not line.startswith('<row'):
            continue
        xmlDoc = parseString(line)
        post = createQuestionOrAnswer(xmlDoc)
        posts.append(post)
    sys.stderr.write('read %d posts\n' % len(posts))
    return posts


def assemble(users, posts, comments):
    usersById = {}
    postsById = {}
    for u in users:
        usersById[u.id] = u
    for p in posts:
        postsById[p.id] = p

    questions = []
    for p in posts:
        if isinstance(p, Question):
            questions.append(p)
        elif postsById.has_key(p.parentId):
            q = postsById[p.parentId]
            p.question = q
            q.answers.append(p)
        p.user = usersById.get(p.userId)

    for q in questions:
        if q.acceptedAnswerId != -1:
            a = postsById[q.acceptedAnswerId]
            q.acceptedAnswer = a
            a.isAccepted = True

    for c in comments:
        c.user = usersById.get(c.userId)
        if postsById.has_key(c.postId):
            p = postsById[c.postId]
            c.post = p
            p.comments.append(c)

    return questions


def xmlAttr(xmlDoc, attr, defaultValue=None):
    exists = xmlDoc.documentElement.hasAttribute(attr)
    if not exists and defaultValue == None:
        raise KeyError, 'unknown attribute %s' % attr 
    elif not exists:
        return defaultValue
    else:
        return xmlDoc.documentElement.getAttribute(attr)

HTML_STRIP = re.compile(r'<[^<]*?/?>')
WHITESPACE_STRIP = re.compile(r' \\s+')


def stripHtml(html):
    stripped = HTML_STRIP.sub('', html)
    return WHITESPACE_STRIP.sub('', stripped)
   

if __name__ == '__main__':
    readAll()
