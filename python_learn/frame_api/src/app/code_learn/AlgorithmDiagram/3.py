# !/usr/bin/python
# -*- coding:utf-8 -*-

"""
递归函数：

"""


def countdown(i):
    print(i)
    if i <= 0:  # 基线条件
        return
    else:  # 递归条件
        countdown(i - 1)


"""
递归调用栈
"""


def fact(x):
    if x == 1:
        return 1
    else:
        return x * fact(x - 1)


if __name__ == '__main__':
    # countdown(2)
    print(fact(1))
