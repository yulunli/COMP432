import numpy as np
import pylab as P

baseDir = "/home/ilps//Downloads/tembolabs/ratio"
my_dpi = 96

data = [[], [], []]

with open(baseDir, "r") as dat:
    for line in dat:
        start = 6
        end = 9
        values = line.split(",")[start:end]
        for x in range(end - start):
            if values[x] != "":
                data[x].append(float(values[x]))


for i in range(len(data)):
    data[i] = sorted(data[i])[1:len(data[i]) - 2]
P.figure(figsize=(800/my_dpi, 800/my_dpi), dpi=my_dpi)
n, bins, patches = P.hist(data, 10, color=['lightblue', 'chartreuse', 'crimson'], label=['1 Year Avg', '3 Year Avg', '5 Year Avg'])
P.legend()
P.grid(True)
P.xlabel("z-score")
P.ylabel("Number of funds")
P.title("Closed-end Fund Z-score Histogram")
P.savefig('firstHist.png', dpi=my_dpi)