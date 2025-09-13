def ts(l, n):
    for i in range(len(l)):
        for j in range(i, len(l)):
            if l[i] + l[j] == n and i != j:
                return i, j


l = [3, 5, 7, 9, 3, 4, 7, 8, 4, 3, 5, 6, 6]
n = 12

