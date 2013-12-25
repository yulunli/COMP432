import random

size = 5


def getAdjMatrix(size):
    matrix = []
    for i in range(size):
        matrix.append([])
    for rowNum in range(size):
        for colNum in range(size):
            if colNum == rowNum:
                matrix[colNum].append(1)
            elif colNum < rowNum:
                matrix[colNum].append(random.randint(0, 1))
            else:
                matrix[colNum].append(0)
    for rowNum in range(size):
        for colNum in range(size):
            if rowNum > colNum:
                matrix[rowNum][colNum] = matrix[colNum][rowNum]
    return matrix


def getR(size):
    r = []
    for i in range(size):
        r.append(random.randint(0, 1))
    return r


def getX(size):
    adj = getAdjMatrix(size)
    rVector = getR(size)
    result = []
    for i in range(size):
        numerator = 0.0
        aij = adj[i]
        for a in range(size):
            numerator += aij[a] * rVector[a]
        denominator = sum(aij)
        result.append(numerator/denominator)
    return result

print(getX(size))

