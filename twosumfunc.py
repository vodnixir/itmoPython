def ts(l, n):
    if len(l)<=1:
        print('Неподходящий размер массива')
    else:
        for i in range(len(l)):
            for j in range(i, len(l)):
                if l[i] + l[j] == n and i != j:
                    return i, j

