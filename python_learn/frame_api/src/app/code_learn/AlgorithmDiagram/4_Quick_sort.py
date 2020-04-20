# !/usr/bin/python
# -*- coding:utf-8 -*-

def sum(arr):
    total = 0
    for x in arr:
        total += x
    return total


print(sum([1, 2, 3, 4]))

"""
快速排序
基线条件为数组为空或只包含一个元素。在这种情况下，只需原样返回数组——根本就不用排序。
步骤如下。
(1) 选择基准值。
(2) 将数组分成两个子数组：小于基准值的元素和大于基准值的元素。
(3) 对这两个子数组重复(1)和(2)
"""


def quicksort(arr):
    if len(arr) < 2:
        return arr
    else:
        pivot = arr[0]
        less = [i for i in arr[1:] if i < pivot]
        greater = [i for i in arr[1:] if i > pivot]
        return quicksort(less) + [pivot] + quicksort(greater)


print(quicksort([7, 10, 5, 3]))
