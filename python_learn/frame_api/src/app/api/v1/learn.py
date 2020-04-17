# !/usr/bin/python
# -*- coding:utf-8 -*-
# coding = utf -8
import os
import time
import logging
from datetime import datetime
from collections import defaultdict, deque
from flask import g, current_app, request

from sqlalchemy import text, case, and_
from sqlalchemy import func

from app.libs.token_auth import auth
from app.validators.forms_v1 import StatQiSituationForm, StatQiScoreForm, StatQiScoreBranchForm, \
    StatQiScoreAgentForm, StatQiRuleForm, StatOpDurationForm, StatOpSilenceForm, StatOpRepeatForm, StatOpReasonForm, \
    StatOpHotForm, StatOpBusinessForm
from app.libs.redprint import Redprint
from app.libs.error_code import ResultSuccess, PageResultSuccess
from app.libs.qpaginate import pager

from app.models.base import db_v1
from app.models.qi_qia_models import QiScoreCall, QiInfoTraffic, QiInfoMapRule, QiResultsDetail, QiInfoUser, \
    QiInfoBranch, QiResultsBusinessAnalysis, QiInfoCallReasonType, QiResultsRepeatCall, QiInfoBusinessType, \
    QiResultsBusinessTrend, QiResultsHotword, QiCallDuration, QiInfoRole
from app.validators.base import PageForm

api = Redprint('learn')
logger = logging.getLogger(__name__)


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


def _get_user_full_info():
    """
    没有使用 @auth.login_required的接口，不要用这个方法，会报404
    :return:
    """
    user, role = db_v1.session.query(
        QiInfoUser, QiInfoRole
    ).filter(
        QiInfoUser.id == g.user.uid,
        QiInfoUser.rid == QiInfoRole.id,
        QiInfoUser.is_deleted == 0,
    ).first_or_404()

    # user.bid 为 -1或者空的时候，branch不存在，得给个默认值
    branch = db_v1.session.query(QiInfoBranch).filter_by(id=user.bid).first()

    if not branch or user.bid == -1:
        branch = QiInfoBranch()
        branch.id = -1
        branch.branch_name = '未分配'
        branch.branch_code = '-'

    return user, role, branch


@api.route('/op_reason_trend', methods=['POST'])
@auth.login_required
def op_reason_trend():
    _list_per_data_filter_01()
    item = []
    return ResultSuccess(msg='质检概况列表和饼图', data=item)


def _list_per_data_filter_01():
    cur_user, cur_role, cur_branch = _get_user_full_info()
    print(cur_role.rcode)
    if cur_role.rcode in ['qioperator', 'teammanager', ]:
        branch_all = QiInfoBranch.query.filter_by(QiInfoBranch.is_deleted == 0).all()
        # list可以[(1, 0), (2, 1)]存储数据
        branch_id_pairs = [(branch.id, branch.superior_id) for branch in branch_all]
        print(branch_id_pairs)
        branch_all_sub = _branch_sub_rel_reformer(branch_id_pairs,
                                                  max_deep=current_app.config['BUSI_BRANCH_SUBREL_MAXDEEP'])
        print('branch_all_sub',branch_all_sub)
        branch_flist = branch_all_sub.get(cur_branch.id, [])
        branch_flist.append(cur_branch.id)

        agent_user_flist = db_v1.session.query(QiInfoUser).filter(
            QiInfoBranch.is_deleted == 0,
            QiInfoBranch.id.in_(branch_flist),
            QiInfoUser.bid == QiInfoBranch.id
        ).all()
        agent_id_flist = [user.agent_id for user in agent_user_flist]
        print(agent_id_flist)
    return agent_id_flist
