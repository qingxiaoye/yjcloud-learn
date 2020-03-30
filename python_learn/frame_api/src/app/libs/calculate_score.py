# -*- coding: utf-8 -*-
from sqlalchemy import func, distinct, and_, text
import time
import datetime
from app.models.base import db_v1
from app.models.qi_qia_models import QiInfoTraffic, QiResultsDetail, QiInfoMapRule, QiScoreCall, QiInfoProject, \
    QiInfoTemplate


def qia_score(call_data, base_score):
    qc_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    tmp1 = db_v1.session.query(QiResultsDetail.call_id, func.sum(QiInfoMapRule.rule_score).label(
        "total_role_score")).filter(QiResultsDetail.call_id.in_(call_data), QiResultsDetail.hit_status == 1).join(
        QiInfoMapRule, QiResultsDetail.detail_rule_id == QiInfoMapRule.id).\
        group_by(QiResultsDetail.call_id).subquery()
    tmp2 = db_v1.session.query(QiResultsDetail.call_id, func.group_concat(
        distinct(func.concat(QiInfoMapRule.template_name, '-', QiInfoMapRule.rule_name)).op('SEPARATOR')(text('"|"'))).label(
        "hit_rules")).filter(QiResultsDetail.call_id.in_(call_data), QiResultsDetail.hit_status == 1).join(
        QiInfoMapRule, QiResultsDetail.detail_rule_id == QiInfoMapRule.id).group_by(QiResultsDetail.call_id).subquery()
    qc_datas = db_v1.session.query(QiInfoTraffic.call_id, (base_score + tmp1.c.total_role_score).label("qc_score"),
                                   tmp2.c.hit_rules).filter(QiInfoTraffic.call_id.in_(call_data)).outerjoin(
        tmp1, QiInfoTraffic.call_id == tmp1.c.call_id).outerjoin(tmp2, QiInfoTraffic.call_id == tmp2.c.call_id)

    # update_file_status = []
    # update_hit_status = []
    # update_unhit_status = []
    # for qc_data in qc_datas:
    #     update_file_status.append(qc_data.call_id)
    #     if not qc_data.hit_rules:
    #         update_hit_status.append(qc_data.call_id)
    #     else:
    #         update_unhit_status.append(qc_data.call_id)
    with db_v1.auto_commit():
        for qc_data in qc_datas:
            if qc_data.qc_score:
                model_info = QiScoreCall()
                model_info.insert_time = int(time.time())
                model_info.is_deleted = 0
                model_info.call_id = qc_data.call_id
                model_info.qc_time = qc_time
                model_info.hit_rules = qc_data.hit_rules
                model_info.qc_score = qc_data.qc_score
                db_v1.session.add(model_info)
                db_v1.session.query(QiInfoTraffic).filter(QiInfoTraffic.call_id == qc_data.call_id).update(
                    {"file_status": 3})
                if qc_data.hit_rules:
                    db_v1.session.query(QiInfoTraffic).filter(QiInfoTraffic.call_id == qc_data.call_id).update(
                     {"hit_status": 1})
                else:
                    db_v1.session.query(QiInfoTraffic).filter(QiInfoTraffic.call_id == qc_data.call_id).update(
                     {"hit_status": 2})


def update_score(call_id):
    # 计算基础分值
    project_datas = db_v1.session.query(QiInfoTraffic.original_project).filter(and_(
        QiInfoTraffic.call_id == call_id), QiInfoTraffic.is_deleted == 0).all()
    template_id_datas = db_v1.session.query(QiInfoProject.original_project, QiInfoProject.qi_template,
                                            func.max(QiInfoProject.create_time)).filter(
        and_(QiInfoProject.original_project == project_datas[0].original_project), QiInfoProject.is_deleted == 0).all()
    template_datas = db_v1.session.query(QiInfoTemplate).filter(and_(
        QiInfoTemplate.id == template_id_datas[0].qi_template, QiInfoTemplate.is_deleted == 0)).all()
    # 汇总命中情况
    tmp1 = db_v1.session.query(QiResultsDetail.call_id, func.sum(QiInfoMapRule.rule_score).label(
        "total_role_score")).filter(QiResultsDetail.call_id == call_id, QiResultsDetail.hit_status == 1).join(
        QiInfoMapRule, QiResultsDetail.detail_rule_id == QiInfoMapRule.id). \
        group_by(QiResultsDetail.call_id).subquery()
    tmp2 = db_v1.session.query(QiResultsDetail.call_id, func.group_concat(
        distinct(func.concat(QiInfoMapRule.template_name, '-', QiInfoMapRule.rule_name)).op('SEPARATOR')(
            text('"|"'))).label(
        "hit_rules")).filter(QiResultsDetail.call_id == call_id, QiResultsDetail.hit_status == 1).join(
        QiInfoMapRule, QiResultsDetail.detail_rule_id == QiInfoMapRule.id).group_by(
        QiResultsDetail.call_id).subquery()
    qc_datas = db_v1.session.query(QiInfoTraffic.call_id, (template_datas[0].base_score + tmp1.c.total_role_score).label("qc_score"),
                                   tmp2.c.hit_rules).filter(QiInfoTraffic.call_id == call_id).outerjoin(
        tmp1, QiInfoTraffic.call_id == tmp1.c.call_id).outerjoin(tmp2, QiInfoTraffic.call_id == tmp2.c.call_id)
    hit_rules = qc_datas[0].hit_rules
    qc_score = qc_datas[0].qc_score
    if qc_score is None:
        qc_score = 100
        db_v1.session.query(QiScoreCall).filter(QiScoreCall.call_id == call_id).update(
            {"hit_rules": hit_rules, "qc_score": qc_score})


