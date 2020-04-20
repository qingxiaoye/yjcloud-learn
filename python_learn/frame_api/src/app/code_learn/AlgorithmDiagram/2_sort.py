# !/usr/bin/python
# -*- coding:utf-8 -*-
"""
将数组元素按从小到大的顺序排列
"""


def findSmallest(arr):
    smallest = arr[0]
    smallest_index = 0
    for i in range(len(arr)):
        if arr[i] < smallest:
            smallest = arr[i]
            smallest_index = i
    return smallest_index


def selectionSort(arr):
    newarr = []
    for i in range(len(arr)):
        smallest_index = findSmallest(arr)
        newarr.append(arr.pop(smallest_index))
    return newarr


print(selectionSort([5, 3, 6, 2, 10]))
