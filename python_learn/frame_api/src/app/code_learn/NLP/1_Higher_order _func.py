# !/usr/bin/python
# -*- coding:utf-8 -*-

"""
lambda:
    又被称为匿名函数
    格式：
        参数列表：函数体
"""
import time
from functools import reduce


def add(x, y):
    return x + y


# 将add()函数用lambda的形式进行定义
def learn_lambda():
    print('lambda学习')
    add_lambda = lambda x, y: x + y
    print(add_lambda(3, 4))  # 7


"""三元运算符"""


def learn_ternary():
    print('三元运算符学习')
    condition = True
    print(1 if condition else 2)


"""
map函数
    输入是一个list返回是一个list
    map和reduce经常结合用
"""


def learn_map():
    print('map学习')
    list1 = [1, 2, 3]
    r1 = map(lambda x: x + x, list1)
    print(list(r1))
    # [2, 4, 6]
    r2 = map(lambda x, y: x + y, [1, 2, 3], [4, 5, 6])
    print(list(r2))
    # [5, 7, 9]


"""
filter过滤器
"""


def learn_filter():
    print('学习filter')
    list1 = ['hello', '', 'APPLE']

    def is_not_None(s):
        return s and len(s.strip()) > 0

    result1 = filter(is_not_None, list1)
    print(list(result1))
    # ['hello', 'APPLE']


"""
reduce函数
reduce(func, list)
汇聚
"""


def learn_reduce():
    print('学习reduce函数')
    f = lambda x, y: x + y
    r1 = reduce(f, [1, 2, 3])
    print(r1)
    # 6
    r2 = reduce(f, [1, 2, 3], 10)
    print(r2)
    # 16


"""
三大推导式
"""


def learn_derivation_list():
    print('三大推导式list')
    list1 = [1, 2, 3, 4, 5]
    f = map(lambda x: x * x, list1)
    print(list(f))
    # [1, 4, 9, 16, 25]
    list2 = [i * i for i in list1 if i > 1]
    print(list2)
    # [1, 4, 9, 16, 25]


def learn_derivation_set():
    print('三大推导式set')
    set1 = {1, 2, 3, 4, 5}
    f = map(lambda x: x * x, set1)
    print(list(f))
    # [1, 4, 9, 16, 25]
    list2 = {i * i for i in set1 if i > 1}
    print(list2)
    # {16, 9, 4, 25}


def learn_derivation_dict():
    print('三大推导式dict')
    dict1 = {"name": "xqq",
             "age": 18,
             "gender": "girl"}
    s1 = {value: key for key, value in dict1.items() if value == "girl"}
    print(s1)


"""
闭包:
一个返回值是函数的函数
"""


def run_time():
    def now_time():
        print('闭包')
        print(time.time())

    return now_time


"""
装饰器
当函数的参数不确定时，可以使用*args和**kwargs
*args没有key值，**kwargs有key值
*args：位置参数
**kwargs：关键字参数
"""


def learn_deco(func):
    def get_time(*args, **kwargs):
        print('装饰器&参数')
        print('args', args)  # (1, 2)
        func(*args, **kwargs)
    return get_time


"装饰器的学习"


@learn_deco
def run_deco(*args, **kwargs):
    print('运行函数')
    for args_value in args:
        print('args_value', args_value)
    for key in kwargs:
        print('keyword_arg:%s:%s' % (key, kwargs[key]))


if __name__ == '__main__':
    # learn_lambda()
    # learn_ternary()
    # learn_map()
    # learn_filter()
    # learn_reduce()
    # learn_derivation_list()
    # learn_derivation_set()
    # learn_derivation_dict()
    f = run_time()
    print(f)  # <function run_time.<locals>.now_time at 0x000001ECB7BCD1E0>
    f()
    # learn_deco()
    run_deco(1, 2, x=1)
