# !/usr/bin/python
# -*- coding:utf-8 -*-

"""
二分法：
    输入是一个有序的元素列表，和查找到元素 。
    如果要查找的元素包含在列表中，二分查找返回其位置；否则返回null
    1 从中间开始查找
        if等于则返回位置：
        elif 查找的元素大于中间元素：
            则从中间到结束
        elif 查找的元素小于中间元素：
            则从开始到中间

    对于中间位置的确定：int，取整

"""


def binary_search(list1, item):
    low = 0
    high = len(list1) - 1
    while low <= high:
        mid = int((low + high) / 2)

        guess = list1[mid]
        if guess == item:
            return mid
        elif item > guess:
            low = mid + 1
        elif item < guess:
            high = mid - 1
    return '该元素不存在list里面'

if __name__ == '__main__':
    print (binary_search([1, 2, 3, 4], 7))
