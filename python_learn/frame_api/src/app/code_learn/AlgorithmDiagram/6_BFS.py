# !/usr/bin/python
# -*- coding:utf-8 -*-
"""
广度优先搜索
"""
from collections import deque


def person_is_seller(person):
    return person[-1] == 'm'


graph = {}
graph["you"] = ["alice", "bob", "claire"]
graph["bob"] = ["anuj", "peggy"]
graph["alice"] = ["peggy"]
graph["claire"] = ["thom", "jonny"]
# graph["anuj"] = []
# graph["peggy"] = []
# graph["thom"] = []
# graph["jonny"] = []

"""
查找you是否有朋友的名字以b结尾
"""


def search(name):
    search_queue = deque()
    if graph.get(name):
        search_queue += graph[name]
        searched = []  # 避免多次查找，如果你检查两次，就做了无用功。因此，
        while search_queue:
            person = search_queue.popleft()  # 当队列不为空的时候，从队列取出一个值
            if not person in searched:
                if person_is_seller(person):
                    print(person + " is a mango seller!")
                    return True  # 找到
                else:

                    search_queue += graph[person] if graph.get(person) else ''  # 将这个人的朋友都加入搜索队列
                    searched.append(person)
    else:
        print('朋友圈中没有改朋友')
        return False  # 找到


search('you')
