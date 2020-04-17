# # !/usr/bin/python
# # -*- coding:utf-8 -*-
from collections import defaultdict, Counter, deque

list1 = [(1, 0), (2, 1), (3, 1), (4, 3), (5, 3), (6, 2), (7, 2), (8, 7)]


def _branch_sub_rel_reformer(branch_id_pairs, max_deep=10):
    branch_sub_rel = defaultdict(set)
    for b_id, b_supid in branch_id_pairs:
        branch_sub_rel[b_supid].add(b_id)
    branch_all_sub_rel = defaultdict(set)
    for k, sub_ids in branch_sub_rel.items():
        all_sub_ids = set()
        id_stack = deque([k, ])
        deep_counter = 0
        deep_limit = max_deep - 1
        while len(id_stack) > 0:
            if deep_counter > deep_limit:
                break
            s_id = id_stack.popleft()
            for sub_rel_id in branch_sub_rel.get(s_id, set()):
                all_sub_ids.add(sub_rel_id)
                id_stack.append(sub_rel_id)

            deep_counter += 1
        branch_all_sub_rel[k] = all_sub_ids

    return {k: list(v) for k, v in branch_all_sub_rel.items()}


_branch_sub_rel_reformer(list1)
