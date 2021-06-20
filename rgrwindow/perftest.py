import time



def whileLoop(N):
    res = -1
    count = 0
    lap1 = time.time()
    while count < N:
        count += 1
    lap2 = time.time()
    if count==N:
        res = lap2-lap1
    return res

def forLoop(N):
    res = -1
    count = 0
    lap1 = time.time()
    for i in range(N):
        count += 1
    lap2 = time.time()
    if count==N:
        res = lap2-lap1
    return res

def listLoop(tab):
    res = -1
    lap1 = time.time()
    count = 0
    for t in tab:
        count += 1
    lap2 = time.time()
    if count == len(tab):
        res = lap2 - lap1
    return res


N = 20000000
pythonList = [0,] * N

forTime = forLoop(N)
print(f"FOR   loop = {forTime} sec.")

whileTime = whileLoop(N)
print(f"WHILE loop = {whileTime} sec.")

listTime = listLoop(pythonList)
print(f"LIST  loop = {listTime} sec.")

