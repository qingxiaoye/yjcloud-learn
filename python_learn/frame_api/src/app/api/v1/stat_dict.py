# !/usr/bin/python
# -*- coding:utf-8 -*-
# coding = utf -8
import os
import time
import logging
from datetime import datetime
from collections import defaultdict, deque, Counter
from flask import g, current_app, request

from sqlalchemy import text, case, and_, desc
from sqlalchemy import func

from app.api.sysmng.branch import _branch_sub_rel_reformer
from app.libs.builtin_extend import safe_cast_float, safe_cast_int, safe_division
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

api = Redprint('stat')
logger = logging.getLogger(__name__)


@api.route('/qi-score-branch-list', methods=['POST'])
@auth.login_required
def qiastat_qi_score_branch_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = StatQiScoreBranchForm().validate_for_api()
    # 主表
    q = db_v1.session.query(QiInfoBranch).filter(QiInfoBranch.is_deleted == 0, ).order_by(
        desc(QiInfoBranch.create_time))
    if form.branch_name.data and form.branch_name.data != '':
        q = q.filter(QiInfoBranch.branch_name.like('%' + form.branch_name.data + "%"))
    vm_keys_branch = ['id', 'superior_id', 'branch_name', 'branch_code', ]

    rvs = pager(q, page=cur_page, per_page=per_page)
    vms = []
    for rv in rvs.items:
        vm = {}
        for v_key in vm_keys_branch:
            vm[v_key] = getattr(rv, v_key, None)

        vms.append(vm)

    # 上級部門組裝
    branch_all = QiInfoBranch.query.filter(QiInfoBranch.is_deleted == 0).all()
    branch_all_dict = {branch.id: branch for branch in branch_all}
    default_branch = QiInfoBranch()
    default_branch.branch_name = '——'
    default_branch.branch_code = '——'
    for vm in vms:
        vm['sup_branch_name'] = branch_all_dict.get(vm['superior_id'], default_branch).branch_name
        vm['sup_branch_code'] = branch_all_dict.get(vm['superior_id'], default_branch).branch_code

    # 計數agent
    branch_id_pairs = [(branch.id, branch.superior_id) for branch in branch_all]
    branch_all_sub = _branch_sub_rel_reformer(
        branch_id_pairs,
        max_deep=current_app.config['BUSI_BRANCH_SUBREL_MAXDEEP']
    )
    user_all = QiInfoUser.query.filter(
        QiInfoUser.is_deleted == 0,
        QiInfoUser.agent_id != -1,
    ).all()

    cnt_agent_per_branch = defaultdict(int)
    for user in user_all:
        cnt_agent_per_branch[user.bid] += 1

    cnt_agent_with_sub_branch = defaultdict(int)
    # for 循环的嵌套使用
    for bid, cnt_agent in cnt_agent_per_branch.items():
        cnt_agent_with_sub_branch[bid] = cnt_agent
        for sub_bid in branch_all_sub.get(bid, []):
            cnt_agent_with_sub_branch[bid] += cnt_agent_per_branch.get(sub_bid, 0)
    for vm in vms:
        vm['cnt_agent'] = cnt_agent_with_sub_branch.get(vm['id'], 0)

    # avg_score
    traffic_score = db_v1.session.query(
        QiInfoTraffic, QiScoreCall
    ).outerjoin(
        QiScoreCall,
        and_(
            QiInfoTraffic.call_id == QiScoreCall.call_id,
            QiScoreCall.is_deleted == 0
        )
    ).filter(
        QiInfoTraffic.is_deleted == 0
    ).with_labels()
    # 数据过滤
    if form.call_time_left.data and form.call_time_left.data != '':
        traffic_score = traffic_score.filter(
            QiInfoTraffic.call_start_time >= datetime.fromtimestamp(form.call_time_left.data)
        )
    if form.call_time_right.data and form.call_time_right.data != '':
        traffic_score = traffic_score.filter(
            QiInfoTraffic.call_start_time <= datetime.fromtimestamp(form.call_time_right.data)
        )
    traffic_score = traffic_score.subquery('traffic_score')

    branch_user = db_v1.session.query(
        QiInfoBranch.id.label('qi_info_branch_id'),
        QiInfoUser.agent_id.label('qi_info_user_agent_id'),
    ).outerjoin(
        QiInfoUser,
        and_(QiInfoBranch.id == QiInfoUser.bid,
             QiInfoUser.is_deleted == 0,
             QiInfoUser.bid != -1,
             )
    ).filter(
        QiInfoBranch.is_deleted == 0,
    ).with_labels()
    branch_user = branch_user.subquery('branch_user')

    stat_traffic_sc_all = db_v1.session.query(
        branch_user.c.qi_info_branch_id.label('bid'),
        func.sum(traffic_score.c.qi_score_call_qc_score).label('sum_qc_score'),
        func.count(func.if_(traffic_score.c.qi_score_call_qc_score, True, None)).label('cnt_qc_score'),
    ).outerjoin(
        traffic_score,
        branch_user.c.qi_info_user_agent_id == traffic_score.c.qi_info_traffic_agent_id,
    ).group_by(branch_user.c.qi_info_branch_id)

    stat_traffic_sc_all = stat_traffic_sc_all.all()
    # sum_score，cnt_score
    sum_score_per_branch = defaultdict(int)
    cnt_score_per_branch = defaultdict(int)

    for rv in stat_traffic_sc_all:
        sum_score_per_branch[rv.bid] = safe_cast_float(rv.sum_qc_score)
        cnt_score_per_branch[rv.bid] = safe_cast_int(rv.cnt_qc_score)

    sum_score_with_sub_branch = defaultdict(int)
    for bid, sum_score in sum_score_per_branch.items():
        sum_score_with_sub_branch[bid] = sum_score
        for sub_bid in branch_all_sub.get(bid, []):
            sum_score_with_sub_branch[bid] += sum_score_per_branch.get(sub_bid, 0)

    cnt_score_with_sub_branch = defaultdict(int)
    for bid, cnt_score in cnt_score_per_branch.items():
        cnt_score_with_sub_branch[bid] = cnt_score
        for sub_bid in branch_all_sub.get(bid, []):
            cnt_score_with_sub_branch[bid] += cnt_score_per_branch.get(sub_bid, 0)

    for vm in vms:
        vm['avg_score'] = safe_division(
            sum_score_with_sub_branch.get(vm['id'], 0),
            cnt_score_with_sub_branch.get(vm['id'], 0),
            precision=2
        )

    # hit_rules

    traffic_rules = db_v1.session.query(
        QiInfoTraffic.agent_id,
        QiResultsDetail.detail_rule_id,
    ).filter(
        QiInfoTraffic.call_id == QiResultsDetail.call_id,
        QiInfoTraffic.is_deleted == 0,
        QiResultsDetail.is_deleted == 0, )
    if form.call_time_left.data and form.call_time_left.data != '':
        traffic_rules = traffic_rules.filter(
            QiInfoTraffic.call_start_time >= datetime.fromtimestamp(form.call_time_left.data)
        )
    if form.call_time_right.data and form.call_time_right.data != '':
        traffic_rules = traffic_rules.filter(
            QiInfoTraffic.call_start_time <= datetime.fromtimestamp(form.call_time_right.data)
        )
    traffic_rules = traffic_rules.subquery('traffic_rules')

    hit_rule_all = db_v1.session.query(
        branch_user.c.qi_info_branch_id.label('bid'),
        traffic_rules.c.detail_rule_id,
        func.count(func.if_(traffic_rules.c.detail_rule_id, True, None)).label('cnt_rules'),
    ).outerjoin(
        traffic_rules,
        branch_user.c.qi_info_user_agent_id == traffic_rules.c.agent_id,
    ).group_by(branch_user.c.qi_info_branch_id, traffic_rules.c.detail_rule_id)

    hit_rule_all = hit_rule_all.all()
    hit_rule_ids_per_branch = defaultdict(lambda: defaultdict(int))
    for rv in hit_rule_all:
        hit_rule_ids_per_branch[rv.bid][rv.detail_rule_id] += rv.cnt_rules
    hit_rules_ids_with_sub_branch = defaultdict(int)
    for bid, hit_rule_ids in hit_rule_ids_per_branch.items():
        hit_rules_ids_with_sub_branch[bid] = hit_rule_ids
        for sub_bid in branch_all_sub.get(bid, []):
            dict_1 = hit_rule_ids_per_branch.get(sub_bid, {})
            dict_2 = hit_rules_ids_with_sub_branch[bid]
            hit_rules_ids_with_sub_branch[bid] = dict(Counter(dict_1) + Counter(dict_2))
    map_rule_all = QiInfoMapRule.query.filter_by().all()
    map_rule_name_dict = {map_rule.id: '{}-{}'.format(map_rule.template_name, map_rule.rule_name) for map_rule in
                          map_rule_all}
    hit_rules_id_with_sub_branch = defaultdict(int)
    for bid, hit_rule_pair in hit_rules_ids_with_sub_branch.items():
        rule_ids_sorted = sorted(hit_rule_pair, key=hit_rule_pair.get, reverse=True)
        hit_rules_id_with_sub_branch[bid] = [map_rule_name_dict[rule_id] for rule_id in rule_ids_sorted if rule_id]
    for vm in vms:
        vm['hit_rules'] = hit_rules_id_with_sub_branch.get(vm['id'], [])
    vms = sorted(vms, key=lambda x: x['avg_score'], reverse=True)

    return PageResultSuccess(msg='部门评分列表', data=vms, page=rvs.page_view())
