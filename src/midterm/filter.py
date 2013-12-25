#!/usr/bin/python -O
#
# Prunes down the StackOverflow data dump to contain all the information about a
# randomly selected subset of users.
#
# Must be run from within the data directory.
#


import random
from xml.dom.minidom import parseString
import traceback

import stackoverflow


def main(fractionRetained):
    userIds = filterUsers(fractionRetained)
    postIds = filterPosts(userIds)
    #userIds = set([u.id for u in stackoverflow.readUsers('users.filtered.xml')])
    #postIds = set([p.id for p in stackoverflow.readPosts('posts.filtered.xml')])
    commentIds = filterComments(userIds, postIds)


def filterUsers(fractionRetained):
    """ Keeps a percentage of all users.  """

    # filter the user file
    userIds = set()
    n = 0
    f = open('users.filtered.xml', 'w')
    for line in open('users.xml'):
        if line.strip().startswith('<row'):
            n += 1
            if random.random() < fractionRetained:
                f.write(line)
                xmlDoc = parseString(line)
                user = stackoverflow.User(xmlDoc)
                userIds.add(user.id)
        else:
            f.write(line)
    f.close()
    print 'filtered num users from %d to %d' % (n, len(userIds))
    return userIds

def filterPosts(userIds):
    # pass 1: collect ids for:
    #   - questions created by the specified users
    #   - answers created by the specified users
    #   - questions answered by the specified users
    n = 0
    postIds = set()
    for line in open('posts.xml'):
        if line.strip().startswith('<row'):
            n += 1
            xmlDoc = parseString(line)
            post = stackoverflow.createQuestionOrAnswer(xmlDoc)
            if post.userId in userIds:
                postIds.add(post.id)
                if isinstance(post, stackoverflow.Answer):
                    postIds.add(post.parentId)
                else:
                    assert(isinstance(post, stackoverflow.Question))

    # pass two: print out all those posts
    f = open('posts.filtered.xml', 'w')
    for line in open('posts.xml'):
        if line.strip().startswith('<row'):
            n += 1
            xmlDoc = parseString(line)
            post = stackoverflow.createQuestionOrAnswer(xmlDoc)
            if ((post.id in postIds)
            or  (isinstance(post, stackoverflow.Answer) and post.parentId in postIds)):
                postIds.add(post.id)
                f.write(line)
        else:
            f.write(line)
    f.close()
    print 'filtered num posts from %d to %d' % (n, len(postIds))

    return postIds

def filterComments(userIds, postIds):
    # filter the comments file
    e = 0
    m = 0
    n = 0
    f = open('comments.filtered.xml', 'w')
    for line in open('comments.xml'):
        if line.strip().startswith('<row'):
            n += 1
            xmlDoc = parseString(line)
            try:
                comment = stackoverflow.Comment(xmlDoc)
                #print 'checking of %s in postids' % comment.postId
                if comment.postId in postIds or comment.userId in userIds:
                    f.write(line)
                    m += 1
            except:
                #traceback.print_exc()
                e += 1
        else:
            f.write(line)
    f.close()
    print 'filtered num comments from %d to %d (%d errors)' % (n, m, e)
  

if __name__ == '__main__':
    main(0.005) 

