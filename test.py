from copy import copy

test = 'test note lol\n\n**bold*\n**bold\nbold\n*bold*\nbold**\n**bold**'
#       01234567890123 4 56789012 3456789 01234 5678901 2345678 901234567890123456789
#                 1111 1 11111222 2222222 33333 3333344 4444444 455555555556666666666
all_points = []
tmp = copy(test)
while len(tmp) > 2:
    point = tmp.find("**")
    tmp = tmp[(point+2):]
    # print([tmp])
    if all_points:
        point += all_points[-1]
        if len(all_points) % 2:
            point += 4
        else:
            point += 2
    all_points.append(point)
if len(all_points) % 2 != 0:
    all_points.pop(-1)
print(all_points)
