import datetime
import random

def getMS():
    dt = datetime.datetime.now()
    ms = dt.microsecond / 1000
    ms += dt.second * 1000
    ms += dt.minute * 60000
    ms += dt.hour * 3600000
    return ms

with open("files.txt", "r") as fh:
    filenames = map(lambda fn: fn.strip(), fh.readlines())

random.seed()

NUMBER_OF_OPENS = 100000
TIMES_PER_CASE = 3

testcases = ["1000000", "100000", "10000", "1000", "100"]

for i in range(TIMES_PER_CASE):
    for testcase in testcases:
        starttime = getMS()
        for j in range(NUMBER_OF_OPENS):
            filename = "test/" + testcase + "/" + random.choice(filenames)
            open(filename, "rb").close()
        endtime = getMS()

        print testcase, i, endtime - starttime