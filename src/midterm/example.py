#!/usr/bin/python -O
#
# Example of a program that uses that StackOverflow library
#

import stackoverflow


# gets the username or returns "Unkonwn" if the user is None
def getUserName(user):
    if user:
        return user.name
    else:
        return 'Unknown'

def main():
    # so is a stackoverflow.StackOverflow object

    # These lines speed up the loading of the dataset.
    # The first time the dataset is loaded, it is read directly from the files.
    # A cache file is then written.
    # In the future the dataset will be loaded directly from the cache.
    if stackoverflow.hasCachedFile():
        so = stackoverflow.readFromCache()  # This reads a pre-buit object
    else:
        so = stackoverflow.readAll(True)
        stackoverflow.writeToCache(so)  # Write it to the cache for the future

    # get an interesting question and print out some information about it
    q = so.questions[869]

    print '================================================================='
    print '================================================================='
    print 'question id %s and url %s' % (q.id, q.url)
    print '\ttitle:', q.title
    print '\ttext:', q.text

    # note that questions (and answers) may have a user attribute
    # of None if they are created by users not in the filtered set.
    print '\tcreator name', q.user.name

    print '================================================================='
    print '================================================================='
    print 'comments about question:'
    for c in q.comments:
        print '\tuser %s: %s' % (getUserName(c.user), c.text)

    print '================================================================='
    print '================================================================='
    print 'answers to question:'
    for a in q.answers:
        print '\tuser %s: %s' % (getUserName(a.user), a.text)
        print '================================================================='
        print '================================================================='

    print '================================================================='
    print '================================================================='
    a = q.acceptedAnswer
    print 'best answer is: user %s: %s' % (getUserName(a.user), a.text)
    print '================================================================='
    print '================================================================='

    # count all the comments in the tree of questions
    numComments = 0
    for q in so.questions:
        numComments += len(q.comments)
        for a in q.answers:
            numComments += len(a.comments)

    # This number won't match the number in so.comments
    # because it doesn't include comments by users in the filtered set
    # for questions not in the filtered set
    print 'total number of comments is', numComments


if __name__ == '__main__':
    main()
