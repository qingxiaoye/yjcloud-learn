# !/usr/bin/python
# -*- coding:utf-8 -*-
from collections import deque

graph = {}
graph["you"] = ["alice", "bob", "claire"]
graph["bob"] = ["anuj", "peggy"]
graph["alice"] = ["peggy"]
graph["claire"] = ["thom", "jonny"]
xx= 'xqq' if graph.get('sssssss') else ''
search_queue=deque()
search_queue += 'xqq'
print(search_queue,len(search_queue))
print(type(xx))