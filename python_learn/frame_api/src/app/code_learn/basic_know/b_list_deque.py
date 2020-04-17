from collections import deque


def learn_list():
    list1 = [1, 2]

    # 在列表末尾添加新的对象
    # 1	list.append(obj)

    # 统计某个元素在列表中出现的次数
    # 2	list. count (obj)

    # 在列表末尾一次性追加另一个序列中的多个值（用新列表扩展原来的列表）
    # 3	list.extend(seq)
    list1.extend([3, 4])
    print(list1)
    # 从列表中找出某个值第一个匹配项的索引位置
    # 4	list.index(obj)

    # 将对象插入列表
    # 5	list.insert(index, obj)

    # 移除列表中的一个元素（默认最后一个元素），并且返回该元素的值
    # 6	list.pop([index=-1])

    # 移除列表中某个值的第一个匹配项
    # 7	list.remove(obj)
    list1.remove(4)
    print(list1)

    # 反向列表中元素
    # 8	list.reverse()

    # 对原列表进行排序
    # 9	list.sort(cmp=None, key=None, reverse=False)
    list1.sort(reverse=True)
    print(list1, )

    random = [(2, 2), (3, 4), (4, 1), (1, 3)]
    # 指定第二个元素排序
    # 这里传入lambda表达式形参x的实参为列表a中的每一个元素
    random.sort(key=lambda x: x[1])
    print(random)


learn_list()


def lean_deque():
    # https://blog.csdn.net/qq_34979346/article/details/83540389?depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-3&utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-3
    print('\033[31m ========== deque ========== \033[0m')
    print('\033[31m ======= 类似list的操作方法 ======= \033[0m')
    d = deque()
    d.append(3)
    d.append(8)
    print(d)
    # deque([3, 8, 1])
    "2. 两端都使用pop:"
    print('\033[31m ======= pop popleft ======= \033[0m')

    d = deque('12345')
    print(d)
    # deque(['1', '2', '3', '4', '5'])

    "删除最后面的一个值"
    pop_value = d.pop()
    print(pop_value, d)
    # 5 deque(['1', '2', '3', '4'])
    "删除最后面的一个值"

    leftpop_value = d.popleft()
    print(leftpop_value, d)
    # 1   deque(['2', '3', '4'])

    "限制deque的长度"
    "当限制长度的deque增加超过限制数的项时，另一边的项会自动删除"
    d = deque(maxlen=5)

    for i in range(30):
        d.append(str(i))
    print(d)

    "添加list各项追加deque中"
    d = deque([1, 2, 3, 4, 5])
    d.extend([0])
    print(d)
    # deque([1, 2, 3, 4, 5, 0])

    "添加list各项到deque左面"

    d.extendleft([6, 7, 8])
    print(d)
    # deque([8, 7, 6, 1, 2, 3, 4, 5, 0])
