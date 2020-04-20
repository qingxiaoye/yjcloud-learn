# -*- coding:utf-8 -*-

"""
Python3 的六个标准数据类型中：
不可变数据（3 个）：Number（数字）、String（字符串）、Tuple（元组）；
可变数据（3 个）：List（列表）、Dictionary（字典）、Set（集合）。
"""
import math

"""
del语句删除一些对象引用
del var1[,var2[,var3[....,varN]]]
del var1, var2
"""

"""
Python取整——向上取整、向下取整、四舍五入取整、向0取整
"""
print('向上取整')
print(math.ceil(1.6), math.ceil(-1.6))
# 向上取整  2 -1
print('向下取整')
print(math.floor(1.6), math.floor(-1.6))
# 向下取整  1 -2
print('四舍五入：')
print(round(1.3), round(1.6))
# 1 2
"""
但值得一提的是这里对小数末尾为5的处理方法：
    当末尾的5的前一位为奇数：入；
    当末尾的5的前一位为偶数：舍。
"""
print(round(8.5), round(9.5))
# 8 10
print(round(-9.5), round(-8.5))
# -10 -8
print('================计算================')
print('除法', 10 / 3)
print('除法求整数', 10 // 3)
print('除法求余数', 10 % 3)
# 除法 3.3333333333333335
# 除法求整数 3
# 除法求余数 1
print('================list================')
str1 = 'I want to go home'
list1 = str1.split(' ')
"""
截取list  
    list[头下标:尾下标]
    索引值以 0 为开始值，-1 为从末尾的开始位置。
"""

"list里面的元素是可变的"
list1[2:5] = []
print(list1)
# ['I', 'want']

"""
[star_num:end_num:step]
    不包括end_num
    步长为 2（间隔一个位置）来截取字符串
    如果step为负数表示逆向读取，以下实例用于翻转字符串：
    star_num:end_num的值也要为负，最后一个元素所在的位置为-1
"""
list2 = str1.split(' ')
print(list2)
# ['I', 'want', 'to', 'go', 'home']
print(list2[-1:-5:-1])
# ['home', 'go', 'to', 'want']


print('================set集合================')
"""
创建一个空的集合必须用set()
"""
print('==== .add ====')
fruits = {"apple", "banana", "cherry"}
fruits.add("orange")
print(fruits)


student = {'Tom', 'Jim', 'Mary', 'Tom', 'Jack', 'Rose'}
print(student)  # 输出集合，重复的元素被自动去掉
# {'Rose', 'Mary', 'Jim', 'Tom', 'Jack'}

# set可以进行集合运算
a = set('abcd')
b = set('cde')

print(a)
print(b)
print(a - b)  # a 和 b 的差集
# {'b', 'a'}
print(b - a)  # b 和 a 的差集
# {'e'}
print(a | b)  # a 和 b 的并集
# {'b', 'a', 'd', 'e', 'c'}
print(a & b)  # a 和 b 的交集
# {'c', 'd'}
print(a ^ b)  # a 和 b 中不同时存在的元素
# {'b', 'a', 'e'}


print('================math================')
print(math.pow(2,3))
print(2**3)
# 8.0
# 8
print(math.modf(10.9))
# (0.9000000000000004, 10.0)










