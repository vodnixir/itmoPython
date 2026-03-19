iterables = ([1, 2], [3, 4], [5, 6], [7, 8], [9, 10])
print(list(map(lambda *args: args, *iterables)))

# print(list(zip([1,2])))
# # [(1,), (2,)] [(1, 3, 5), (2, 4, 6)]
# print(list(zip([1,2],[3,4])))
# # [(1, 3), (2, 4)]
# print(list(zip([1,2],[3,4],[5,6])))
# # [(1, 3, 5), (2, 4, 6)]




