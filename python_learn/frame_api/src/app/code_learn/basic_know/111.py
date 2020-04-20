class A(object):
    bar = 1

a = A()
print(getattr(a, 'bar') )       # 获取属性 bar 值


print(getattr(a, 'bar2', 3))    # 属性 bar2 不存在，但设置了默认值
