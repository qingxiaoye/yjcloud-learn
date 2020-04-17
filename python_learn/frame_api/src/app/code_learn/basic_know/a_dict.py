# !/usr/bin/python
# -*- coding:utf-8 -*-

from collections import defaultdict, Counter

print('\033[31m================字典的基础知识========================== \033[0m')
print('\033[31m===  items() === \033[0m')
"items() 方法把字典中每对 key 和 value 组成一个元组，并把这些元组放在列表中返回"
d = {'one': 1, 'two': 2, 'three': 3}
print(d.items())  # dict_items([('one', 1), ('two', 2), ('three', 3)])
for k, v in d.items():
    print(k, v)
for i in d.items():
    print(i)
# ('one', 1)
# ('two', 2)
# ('three', 3)

print('\033[31m===== 字典排序 ===== \033[0m')
print('\033[31m== 对字典排序 == \033[0m')
"reverse=True表示按照降序排序"
x = {"name": 4, "num": 370}
y = {"name": 2, "num": 999}
listA = [x, y]
list2 = sorted(listA, key=lambda sort_value: sort_value['num'], reverse=True)
print(list2)
# [{'name': 2, 'num': 999}, {'name': 4, 'num': 370}]

print('\033[31m== 根据values排序，返回排序后的keys == \033[0m')
dict1 = {"规则4": 2, "规则5": 5}
dict1_sorted = sorted(dict1, key=dict1.get, reverse=True)
print(dict1_sorted)
# ['规则5', '规则4']


print('\033[31m================defaultdict的妙用========================== \033[0m')
"""
1 当字典中没有的键第一次出现时，default_factory自动为其返回一个空列表，list.append()会将值添加进新列表；
2 再次遇到相同的键时，list.append()将其它值再添加进该列表
3 当字典中没有该值时会返回一个默认值
"""
"""
https://blog.csdn.net/yangsong95/article/details/82319675?depth_1-utm_source=distribute.pc_relevant.none-task&utm_source=distribute.pc_relevant.none-task
"""
print('\033[31m========= 生成一个list字典，把keys相同的元素放到一个list ========= \033[0m')
s = [('yellow', 1), ('blue', 2), ('yellow', 3), ('blue', 4), ('red', 1)]
d_list = defaultdict(list)
for k, v in s:
    d_list[k].append(v)
print('d_list', d_list)
# d_list defaultdict(<class 'list'>, {'yellow': [1, 3], 'blue': [2, 4], 'red': [1]})

print('\033[31m========= 生成一个int字典，把keys相同的元素求和 ========= \033[0m')
d_int = defaultdict(int)
for k, v in s:
    d_int[k] += v
print('d_int', d_int)
# d_int defaultdict(<class 'int'>, {'yellow': 4, 'blue': 6, 'red': 1})

print('\033[31m========= 不同坐席-不同规则id的个数 lambda和defaultdict结合使用 ========= \033[0m')

s = [('agent1', 4), ('agent1', 5), ('agent1', 4), ('agent2', 5), ('agent2', 4), ('agent2', 4)]
hit_rule_ids_per_agent = defaultdict(lambda: defaultdict(int))
for k, v in s:
    hit_rule_ids_per_agent[k][v] += 1
print(hit_rule_ids_per_agent)
# defaultdict(<function <lambda> at 0x000001F020BEC1E0>,
# {'agent1': defaultdict(<class 'int'>, {4: 2, 5: 1}),
# 'agent2': defaultdict(<class 'int'>, {5: 1, 4: 2})})


print('\033[31m========= 对层级字典里的values进行排序，======== \033[0m')
rule_dict = {4: "规则4", 5: "规则5"}
for k, v in hit_rule_ids_per_agent.items():
    v_sorted = sorted(v, key=v.get, reverse=True)
    hit_rule_ids_per_agent[k] = [rule_dict.get(i, '-') for i in v_sorted]
print(hit_rule_ids_per_agent)
# defaultdict(<function <lambda> at 0x000001B16696C1E0>,
# {'agent1': ['规则4', '规则5'], 'agent2': ['规则4', '规则5']})


print('\033[31m================字典的神奇操作========================== \033[0m')
print('\033[31m========== 字典相同key的value相加 ========== \033[0m')

x = {"name": 4, "num": 370, "age": 370}
y = {"name": 2, "num": 14}
print(dict(Counter(x) + Counter(y)))
# {'name': 2, 'num': 356, 'age': 370}

print('\033[31m========== 对含有下级数据的累加到上级 ==========\033[0m')
dict_for = {1: 4,
            2: 370,
            3: 370,
            4: 90}
dict_for_with_sub = defaultdict(int)

branch_all_sub = {1: [2, 3, 4], 2: [3, 4]}
for k, v in dict_for.items():
    dict_for_with_sub[k] = v
    for sub in branch_all_sub.get(k, []):
        dict_for_with_sub[k] += dict_for.get(sub, 0)

print('\033[31m ========== get ========== \033[0m')
colors_list = ['black', 'yellow', 'red', 'blue']
dd = {}
for color in colors_list:
    dd[color] = d_int.get(color, '--')
print(dd)
# {'black': '--', 'yellow': 4, 'red': 1, 'blue': 6}

print('\033[31m ========== add ========== \033[0m')
branch_id_pairs = [(1, 0), (2, 1), (3, 1), (4, 3), (5, 3), (6, 2), (7, 2), (8, 7)]
branch_sub_rel = defaultdict(set)
for b_id, b_supid in branch_id_pairs:
    branch_sub_rel[b_supid].add(b_id)
print(branch_sub_rel)
# defaultdict(<class 'set'>, {0: {1}, 1: {2, 3}, 3: {4, 5}, 2: {6, 7}, 7: {8}})

