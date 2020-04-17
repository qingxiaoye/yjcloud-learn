# # -*- coding:utf-8 -*-
"""
本部分资料是与语法糖有关的知识
"""

"============= while ======================= "
num = [1, 2, 3, 4]
mark = 0
while mark < len(num):
    n = num[mark]
    if n % 2 == 0:
        n
        # break
    mark += 1
else:
    print("done")

start_num = 1
files_callid_bulk = []
single_bulk = 2
finish_flag = False
finish_value = 5
while not finish_flag:
    end_num = start_num + single_bulk
    for i in range(start_num, end_num):
        if end_num <= finish_value:
            end_num = start_num + single_bulk
            print(i)
        else:
            finish_flag = True
            break
    start_num += single_bulk

"============= zip() 并行迭代 ======================="
a = [1, 2, 3]
b = ['one', 'two', 'three']
zip_list = list(zip(a, b))
zip_list1 = zip_list

"============= 列表推导式 ======================="

x = [num for num in range(6)]
# [0, 1, 2, 3, 4, 5]
y = [num for num in range(6) if num % 2 == 0]
# [0, 2, 4]

# 多层嵌套

rows = range(1, 4)
cols = range(1, 3)
x = [(i, j) for i in rows for j in cols]
x = x
