# -*- coding: utf-8 -*-
import datetime

from sqlalchemy import and_, func
import logging
import traceback

from app.libs.calculate_score import qia_score
from app.libs.qi_qia_rules import keywords_rule, speed_rule, interruption_rule, duration_rule, silence_rule, \
    taboo_rule, emotion_rule
from app.models.base import db_v1
from app.models.qi_qia_models import QiInfoProject, QiInfoTraffic, QiInfoMapRule, QiInfoTemplate

logger = logging.getLogger(__name__)

def speech_qia(call_datas):
    project_datas = db_v1.session.query(QiInfoTraffic.original_project).filter(and_(
        QiInfoTraffic.call_id.in_(call_datas), QiInfoTraffic.is_deleted == 0)).group_by(QiInfoTraffic.original_project).all()
    original_project = []
    for project_data in project_datas:
        original_project.append(project_data.original_project)
    template_id_datas = db_v1.session.query(QiInfoProject.original_project, QiInfoProject.qi_template,
                                            func.max(QiInfoProject.create_time)).filter(
        and_(QiInfoProject.original_project.in_(original_project), QiInfoProject.is_deleted == 0))
    for template_id_data in template_id_datas:
        call_data = db_v1.session.query(QiInfoTraffic.call_id).filter(
            and_(QiInfoTraffic.call_id.in_(call_datas), QiInfoTraffic.is_deleted == 0,
                 QiInfoTraffic.original_project == template_id_data.original_project)).all()
        call_data_id = []
        for i in call_data:
            call_data_id.append(i.call_id)
        template_datas = db_v1.session.query(QiInfoTemplate).filter(and_(
            QiInfoTemplate.id == template_id_data.qi_template, QiInfoTemplate.is_deleted == 0))
        rule_datas = db_v1.session.query(QiInfoMapRule.id, QiInfoMapRule.rule_type, QiInfoMapRule.rule_id,
                                         QiInfoMapRule.template_name, QiInfoMapRule.rule_name, QiInfoMapRule.warning_id
                                         ).filter(and_(
            QiInfoMapRule.template_id == template_id_data.qi_template, QiInfoMapRule.is_deleted == 0))
        for rule_data in rule_datas:
            map_rule_name = rule_data.template_name + '-' + rule_data.rule_name
            if rule_data.rule_type == 0:
                keywords_rule(call_data_id, rule_data.rule_id, rule_data.id, rule_data.warning_id, map_rule_name)
            elif rule_data.rule_type == 1:
                taboo_rule(call_data_id, rule_data.rule_id, rule_data.id, rule_data.warning_id, map_rule_name)
            elif rule_data.rule_type == 2:
                speed_rule(call_data_id, rule_data.rule_id, rule_data.id, rule_data.warning_id, map_rule_name)
            elif rule_data.rule_type == 3:
                interruption_rule(call_data_id, rule_data.rule_id, rule_data.id, rule_data.warning_id, map_rule_name)
            elif rule_data.rule_type == 4:
                duration_rule(call_data_id, rule_data.rule_id, rule_data.id, rule_data.warning_id, map_rule_name)
            elif rule_data.rule_type == 5:
                silence_rule(call_data_id, rule_data.rule_id, rule_data.id, rule_data.warning_id, map_rule_name)
            elif rule_data.rule_type == 6:
                emotion_rule(call_data_id, rule_data.rule_id, rule_data.id, rule_data.warning_id, map_rule_name)
        # 所有都质检完，计算这个模板下所有call_id质检评分
        base_score = template_datas[0].base_score
        try:
            qia_score(call_data_id, base_score)
        except Exception as e:
            logger.error(traceback.format_exc())

    return True




