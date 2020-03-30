# !/usr/bin/python
# -*- coding:utf-8 -*-
import datetime as dtime
import logging
import os
from datetime import datetime

from sqlalchemy import func, asc, desc
from sqlalchemy import text, case, and_

from app.libs.builtin_extend import safe_cast_int, safe_cast_float
from app.libs.builtin_extend import msec2time
from app.libs.enums import TrafficFileStatus
from app.libs.error_code import ResultSuccess, PageResultSuccess
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v1
from app.models.qi_qia_models import QiScoreCall, QiInfoTraffic, QiInfoMapRule, QiResultsDetail, QiInfoUser, \
    QiInfoBranch, QiResultsBusinessAnalysis, QiInfoCallReasonType, QiResultsRepeatCall, QiInfoBusinessType, \
    QiResultsBusinessTrend, QiResultsHotword, QiCallDuration
from app.validators.base import PageForm, ColumnSortForm
from app.validators.forms_v1 import StatQiSituationForm, StatQiScoreForm, StatQiScoreBranchForm, \
    StatQiRuleForm, StatOpDurationForm, StatOpSilenceForm, StatOpRepeatForm, StatOpReasonForm, \
    StatOpHotForm, StatOpBusinessForm

api = Redprint('know')
logger = logging.getLogger(__name__)


@api.route('/op-dura-business-list', methods=['POST'])
@auth.login_required
def op_dura_business_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())
    column_name, column_order = ColumnSortForm.fetch_column_param(ColumnSortForm().validate_for_api())

    form = StatOpDurationForm().validate_for_api()
    # join 和 outerjoin 最好不要同时用，可以以下面的方式写一个子查询
    # with_labels()可以直接对QiInfoTraffic中的字段命名，格式为qi_info_traffic_call_id。
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
    ).with_labels().subquery('traffic_score')

    grp_q = db_v1.session.query(
        QiInfoBusinessType.id,
        QiInfoBusinessType.type_name,
        func.count(func.if_(
            traffic_score.c.qi_info_traffic_file_status >= TrafficFileStatus.FILE_QUALITY_FINISH.value, 1, None)
        ).label('cnt_qi'),
        func.avg(traffic_score.c.qi_score_call_qc_score).label('avg_score'),
        func.avg(QiCallDuration.duration).label('duration'),
        (func.avg(QiCallDuration.effective_duration) /
         func.avg(QiCallDuration.duration)).label('rate_effe'),
    ).filter(
        QiInfoBusinessType.type_code == QiResultsBusinessAnalysis.business_type,
        traffic_score.c.qi_info_traffic_call_id == QiResultsBusinessAnalysis.call_id,
        traffic_score.c.qi_info_traffic_call_id == QiCallDuration.call_id,
        QiInfoBusinessType.is_deleted == 0,
        QiResultsBusinessAnalysis.is_deleted == 0,
        QiCallDuration.is_deleted == 0,
    ).group_by(QiInfoBusinessType.type_code)

    if form.call_time_left.data:
        grp_q = grp_q.filter(QiCallDuration.call_start_time >= datetime.fromtimestamp(form.call_time_left.data))
    if form.call_time_right.data:
        grp_q = grp_q.filter(
            QiCallDuration.call_start_time <= datetime.fromtimestamp(form.call_time_right.data))
    # 在进行排序前进行一个子查询
    # 1可以减少修改代码的次数
    # 2不容易出错
    grp_q = grp_q.subquery('grp_q')

    q = db_v1.session.query(grp_q)
    # 排序处理
    # 多用字典的get()方法，真的很棒
    column_obj_map = {
        'cnt_qi': grp_q.c.cnt_qi,
        'avg_score': grp_q.c.avg_score,
        'duration': grp_q.c.duration,
        'rate_effe': grp_q.c.rate_effe,
    }
    if column_order == 'ascending':
        q = q.order_by(asc(column_obj_map.get(column_name, grp_q.c.id)))
    else:
        q = q.order_by(desc(column_obj_map.get(column_name, grp_q.c.id)))

    rvs = pager(q, page=cur_page, per_page=per_page)
    vms = []

    for rv in rvs.items:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        vm = {}
        vm['id'] = rv_dict['id']
        vm['type_name'] = rv_dict['type_name']
        # 这种对值进行转化很棒，用try 和 except
        vm['cnt_qi'] = safe_cast_int(rv_dict['cnt_qi'])
        vm['avg_score'] = round(safe_cast_float(rv_dict['avg_score']), 1)
        # 封装了一种函数，进行ms的转化
        vm['duration'] = str(msec2time(rv_dict['duration']))
        vm['rate_effe'] = "%.1f%%" % (safe_cast_float(rv_dict['rate_effe']) * 100)

        vms.append(vm)
    return PageResultSuccess(msg='通话时长详情表-通话时长分布', data=vms, page=rvs.page_view())
