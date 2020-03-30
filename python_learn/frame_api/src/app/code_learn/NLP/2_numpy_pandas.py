# !/usr/bin/python
# -*- coding:utf-8 -*-
import numpy as np


def learn_np():
    data = [1, 2, '3']
    arr1 = np.array(data * 2)
    arr1_astype = arr1.astype(np.int32)
    print(arr1_astype.dtype)
    # ['1' '2' '3' '1' '2' '3']
    print(arr1)
    # print(n*10)
    print('shape获取np数组的维度 %s', arr1.shape)
    # (6,)
    print('bdim获取np数组的维度 %s', arr1.ndim)
    # 1
    print('取出shape返回的值', arr1.shape[0] == 6)
    "当成员有一个是float或者Unicode类型时，则返回的就是二者之一"
    print('dtype获取np数组内元素类型', arr1.dtype)
    # < U11,表示unicode
    print('嵌套序列')
    data2 = [[1, 2, 3], [4, 5, 6]]
    arr2 = np.array(data2)
    print(arr2)
    print(arr2.shape)
    #  (2, 3)
    print(arr2.ndim)
    # 2
    print('ones & zeros & empty')
    # print(np.zeros((3, 2), dtype=int))
    # print(np.ones((3, 2), dtype=int))
    # print(np.empty((2, 3, 4)))
    print('矢量化运算')
    "数组通常在不需要循环的情况下就可以进行批量化运算"
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    print(x + y)
    print('索引和切片操作')
    arr3 = np.array([0, 1, 2, 3])
    "切片"
    print(arr3[:3])  # [0 1 2]
    "索引赋值"
    arr3[1] = 10
    print(arr3)  # [ 0 10  2  3]
    arr3_cppy = arr3.copy()
    "copy"
    arr3_cppy[2] = 4
    print(arr3_cppy)
    print(arr3)
    "二维数组"
    arr4 = np.array([[0, 1, 2, 3], [4, 5, 6, 7]])
    print(arr4[0, 1])  # 1
    print(arr4[0][1])  # 1
    "花式索引"
    arr5 = np.empty((6, 2), dtype=np.int32)
    for i in range(6):
        arr5[i] = i
    "以特定的顺序选取来选取制定的子集，也可以用负数倒序选取"
    print(arr5[[2, 1, 3, -1]])
    print('--------------')
    arr6 = np.arange(12).reshape((3, 4))
    print(arr6)
    # [[ 0  1  2  3]
    #  [ 4  5  6  7]
    #  [ 8  9 10 11]]
    print(arr6[[0, 1], [2, 3]])
    # [2 7]
    "进行行的选择后，载进行列的选择"
    print(arr6[[0, 1]][:, [0]])
    # [[0]
    #  [4]]
    print(arr6[np.ix_([0, 1], [0])])
    print('-' * 6)
    "数组的转置"
    arr6 = np.arange(12).reshape((3, 4))
    print(arr6.T)
    print(arr6.transpose())

    print('-' * 7)
    "数组的计算"
    arr7 = np.random.rand(3, 4)
    # arr7 = np.arange(10).reshape((5, 2))
    print(arr7)
    # [[0 1]
    #  [2 3]
    #  [4 5]
    #  [6 7]
    #  [8 9]]
    # print(arr7.mean())
    # print(np.mean(arr7))
    # print(np.sum(arr7))
    # print(np.cumsum(arr7))
    # print(np.sum(arr7, axis=1))
    # [ 1  5  9 13 17]
    # argmax argmin cumsum
    arr7.sort()
    print(arr7)
    print('-'*2,'文件操作','-'*2)

    print('-'*2,'线性代数','-'*2)
    x=np.arange(6).reshape((3,2))
    y=np.arange(4).reshape((2,2))
    print(x.dot(y))


if __name__ == '__main__':
    learn_np()
