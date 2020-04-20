"""
getattr
描述
    getattr() 函数用于返回一个对象属性值。
语法
    getattr(object, name[, default])
"""


class A(object):
    bar = 1


a = A()
print(getattr(a, 'bar'))  # 获取属性 bar 值
print(getattr(a, 'bar2', 3))  # 属性 bar2 不存在，但设置了默认值
