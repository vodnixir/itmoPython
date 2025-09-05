def f(l,n):
    for i in range(len(l)):
        for j in range(i,len(l)):
            if l[i] + l[j] == n and i != j:
                return li, lj
                        
l =  [3,5,7,9,3,4,7,8,4,3,5,6,6]
n = 12

print(f(l,n))



# def f(l,n):
#     li = []
#     lj = []
#     for i in range(len(l)):
#         for j in range(i,len(l)):
#             if l[i] + l[j] == n and i != j:
#                 li.append(i)
#                 lj.append(j)
#     return li, lj
                        
# l =  [3,5,7,9,3,4,7,8,4,3,5,6,6]
# n = 12

# li, lj = f(l,n)
# for i in range(len(li)):
#     print(li[i],lj[i])


