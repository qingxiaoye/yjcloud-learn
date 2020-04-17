# !/usr/bin/python
# -*- coding:utf-8 -*-
import numpy as np
def add(x, y):
    z = x + y #9
    return z#10
def sub(x, y):
    z = x - y #12
    return z #13（end）
def debug_over():  # 3
    print('ssss')  # 4
    a = 10  # 5
    b = 5  # 6
    print(np.arange(10))  # 7
    add(a, b) #8
    sub(a, b) #11
if __name__ == '__main__':  # 1
    debug_over()  # 2
