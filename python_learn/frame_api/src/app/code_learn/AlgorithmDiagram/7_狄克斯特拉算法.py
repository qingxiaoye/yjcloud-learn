# !/usr/bin/python
# -*- coding:utf-8 -*-
# 实现图
graph = {"start": {}, "a": {}, "b": {}, "fin": {}}
graph["start"]["a"] = 6
graph["start"]["b"] = 9

graph["a"]["fin"] = 1
graph["b"]["a"] = 3
graph["b"]["fin"] = 5

# 存储每个节点的开销
infinity = float("inf")
costs = {"a": 6, "b": 9, "fin": infinity}
# 存储父节点的散列表
# values表示父节点
parents = {"a": "start", "b": "start", "fin": None}
# 数组，用于记录处理过的节点，因为对于同一个节点，你不用处理多次。
processed = []


def find_lowest_cost_node(costs):
    lowest_cost = float("inf")
    lowest_cost_node = None
    for node in costs.keys():
        if costs[node] < lowest_cost and node not in processed:
            lowest_cost = costs[node]
            lowest_cost_node = node
    return lowest_cost_node


"""

(1) 找出最便宜的节点，即可在最短时间内前往的节点。
(2) 对于该节点的邻居，检查是否有路过该节点前往它们的更短路径，如果有，就更新其开销。
(3) 重复这个过程，直到对图中的每个节点都这样做了。
(4) 计算最终路径。（下一节再介绍！）

"""
node = find_lowest_cost_node(costs)  # 在未处理的节点中找出开销最小的节点
while node is not None:
    cost = costs[node]
    neighbors = graph[node]
    for i in neighbors.keys():
        new_cost = cost + neighbors[i]
        if costs[i] > new_cost:
            costs[i] = new_cost
            parents[i] = node
    processed.append(node)
    node = find_lowest_cost_node(costs)
    if node == 'fin':
        processed.append(node)
        break
print(processed)
