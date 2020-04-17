from collections import deque
"1. deque提供了类似list的操作方法"
d = deque()
d.append(3)
d.append(8)
print(d)
# deque([3, 8, 1])
"2. 两端都使用pop:"

d = deque('12345')
print(d)
# deque(['1', '2', '3', '4', '5'])

pop_value=d.pop()
print(pop_value)
# 抛出的是’5’, d.leftpop()
# 抛出的是’1’，可见默认pop()
# 抛出的是最后一个元素。
#
# 4.
# 限制deque的长度
#
# d = deque(maxlen=20)
#
# for i in range(30):
#     d.append(str(i))
#
# 此时d的值为d = deque(
#     ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28',
#      '29'], maxlen=20), 可见当限制长度的deque增加超过限制数的项时，另一边的项会自动删除。
#
#  添加list各项到deque中：
#
# d = deque([1, 2, 3, 4, 5])
#
# d.extend([0])
#
# 那么此时d = deque([1, 2, 3, 4, 5, 0])
#
# d.extendleft([6, 7, 8])
#
# 此时d = deque([8, 7, 6, 1, 2, 3, 4, 5, 0])
#
# 通过以上的一些操作，我们大致可以了解deque()
# 的性质了
