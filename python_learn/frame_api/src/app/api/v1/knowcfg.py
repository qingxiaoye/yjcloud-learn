# !/usr/bin/python
# -*- coding:utf-8 -*-
import datetime as dtime
import logging
import os
from datetime import datetime

from flask import current_app
from sqlalchemy import func, asc, desc
from sqlalchemy import text, case, and_

from app.libs.builtin_extend import safe_cast_int, safe_cast_float
from app.libs.builtin_extend import msec2time
from app.libs.enums import TrafficFileStatus
from app.libs.error_code import ResultSuccess, PageResultSuccess, Success
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

api = Redprint('knowcfg')
logger = logging.getLogger(__name__)


@api.route('/know-get-cfg', methods=['POST'])
@auth.login_required
def know_get_cfg():
    """读取.yaml配置文件
        需要在src\app\__init__.py加app.config.update(plugins_cfg_dict)
    """
    base_plugin_cfg = current_app.config.get('PLUGINS')
    log_parser_cfg = base_plugin_cfg.get('LOG_PARSER')
    print(log_parser_cfg.get('PLUGIN_PATH'))
    return Success(msg="成功")
