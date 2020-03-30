# -*- coding:utf-8 -*-
import re
import datetime
import time
# import traceback
import logging
import traceback

import torch
from sqlalchemy import and_
from sqlalchemy.sql.expression import func

# from app.libs.emotion_libs.emotion_rules import load_vocab, get_feat, get_prediction, Weight, Thread
from app.libs.DFA_parser import main_func
from app.libs.warning import warn_message, warn_ding_talk, warn_apps
from app.models.base import db_v1
from app.models.qi_qia_models import QiInfoKeyword, QiInfoPrecondition, QiInfoDetailedpcdt, QiLabelParagraph, \
    QiInfoDetailedkw, QiInfoSpeed, QiInfoDuration, QiInfoTraffic, QiInfoInterruption, QiInfoSilence, QiLabelSentence, \
    QiResultsDetail, QiInfoWarning, QiInfoTabooWord, QiInfoEmotion

import sys
sys.path.append('D:/pycharm_project/AI_Speech_QIA/src/app/libs/emotion_libs')
from app.libs.emotion_libs.emotion_rules import load_vocab, get_feat, get_prediction, Weight, Thread
logger = logging.getLogger(__name__)


def to_db(call_id, paragraph_id, detail_rule_id, type_id, hit_location):
    with db_v1.auto_commit():
        # session = db_v1.db_session()
        model_info = QiResultsDetail()
        model_info.insert_time = int(time.time())
        model_info.is_deleted = 0
        model_info.call_id = call_id
        model_info.paragraph_id = paragraph_id
        model_info.detail_rule_id = detail_rule_id
        model_info.qc_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        model_info.hit_status = 1
        model_info.type = type_id
        model_info.review_status = 0
        model_info.hit_location = hit_location
        db_v1.session.add(model_info)
    return True


def keywords_rule(call_datas, rule_id, map_id, warning_id, map_rule_name):
    rule_result = db_v1.session.query(QiInfoKeyword.is_precondition,
                                      QiInfoKeyword.precondition_id,
                                      QiInfoKeyword.keywords_rule,
                                      QiInfoKeyword.check_range,
                                      QiInfoKeyword.left_boundary,
                                      QiInfoKeyword.right_boundary).filter_by(id=rule_id).all()
    if rule_result:
        keywords_id = []
        for i in rule_result[0].keywords_rule.split(','):
            keywords_id.append(int(i))
        keywords = db_v1.session.query(QiInfoDetailedkw.is_contains, QiInfoDetailedkw.keywords).filter(
            QiInfoDetailedkw.id.in_(keywords_id))

        is_color_word = 0
        for i in keywords:
            is_color_word += i.is_contains

        if rule_result[0].is_precondition == 1:
            pre_result = db_v1.session.query(QiInfoPrecondition.map_precondition_id,
                                             QiInfoPrecondition.role).filter(
                QiInfoPrecondition.id == rule_result[0].precondition_id).all()
            pre_id = []
            for i in pre_result[0].map_precondition_id.split(','):
                pre_id.append(int(i))
            pre_keywords = db_v1.session.query(QiInfoDetailedpcdt.keywords).filter(QiInfoDetailedpcdt.id.in_(pre_id)).all()
            pre_datas = db_v1.session.query(QiLabelParagraph.id, QiLabelParagraph.task_id, QiLabelParagraph.paragraph_id,
                                            QiLabelParagraph.order_number, QiLabelParagraph.text).filter(
                and_(QiLabelParagraph.role == pre_result[0].role, QiLabelParagraph.call_id.in_(call_datas))).all()

            pre_hit_number = {}
            for data in pre_datas:
                is_pre_hit = 0
                for pre_keyword in pre_keywords:
                    result = re.search(pre_keyword.keywords, data.text)
                    if not result is None:
                        is_pre_hit += 1
                if len(pre_keywords) == is_pre_hit:  # 前置条件多个细则均命中，那么保存前置条件命中的id, order_number
                    pre_hit_number[data.id] = data.order_number

            qi_data = {}
            for key, value in pre_hit_number.items():
                tmp_data = db_v1.session.query(QiLabelParagraph.task_id, QiLabelParagraph.paragraph_id,
                                               QiLabelParagraph.order_number).filter(
                    and_(QiLabelParagraph.id == key), QiLabelParagraph.call_id.in_(call_datas)).all()
                tmp = db_v1.session.query(QiLabelParagraph.task_id, QiLabelParagraph.paragraph_id,
                                          QiLabelParagraph.order_number).filter(
                    and_(QiLabelParagraph.id == key), QiLabelParagraph.call_id.in_(call_datas)).subquery()
                datas = db_v1.session.query(QiLabelParagraph.call_id, QiLabelParagraph.task_id,
                                            QiLabelParagraph.paragraph_id, QiLabelParagraph.order_number,
                                            QiLabelParagraph.text, QiLabelParagraph.role).join(
                    tmp, and_(QiLabelParagraph.call_id.in_(call_datas),
                              QiLabelParagraph.task_id == tmp.c.task_id,
                              QiLabelParagraph.role == 1,
                              QiLabelParagraph.order_number >= tmp.c.order_number + rule_result[0].left_boundary*2,
                              QiLabelParagraph.order_number <= tmp.c.order_number + rule_result[0].right_boundary*2)).all()
                qi_data[tmp_data[0].paragraph_id] = datas

            if is_color_word != 0:
                # '有包含规则，如果正则匹配到，并且其余的细则也都命中，说明命中，高亮且字也高亮')
                for key, value in qi_data.items():
                    hit_value = []
                    color_str = {}
                    for data in value:
                        is_hit = 0
                        color_id = []
                        for key_word in keywords:
                            if key_word.is_contains == 0:  # 不包含即命中
                                result = re.search(key_word.keywords, data.text)
                                if result is None:  # 命中
                                    is_hit += 1
                            else:
                                result = re.search(key_word.keywords, data.text)  # 包含即命中
                                if not result is None:  # 命中
                                    is_hit += 1
                                    result_iter = re.finditer(key_word.keywords, data.text)
                                    for i in result_iter:
                                        color_id.append(str(i.start()) + ',' + str(i.end() - 1))
                                color_str[data.paragraph_id] = "|".join(color_id)
                        if is_hit == len(keywords_id):
                            hit_value.append(data.paragraph_id)
                            if warning_id:
                                warning_data = db_v1.session.query(QiInfoWarning).filter(
                                    QiInfoWarning.id == warning_id).first_or_404()
                                warning_message = warning_data['message']
                                warning_ding_talk = warning_data['ding_talk']
                                warning_apps = warning_data['apps']
                                if warning_message:
                                    warn_message(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                                 data.paragraph_id,
                                                 map_rule_name, warning_message)
                                if warning_ding_talk:
                                    warn_ding_talk(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                                   data.paragraph_id,
                                                   map_rule_name, warning_ding_talk)
                                if warning_apps:
                                    warn_apps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                              data.paragraph_id,
                                              map_rule_name, warning_apps)
                            try:
                                to_db(data.call_id, data.paragraph_id, map_id, 1, color_str[data.paragraph_id])
                            except Exception as e:
                                logger.error(traceback.format_exc())
            else:
                # '全是不包含，如果正则匹配到，说明没有命中')
                for key, value in qi_data.items():
                    hit_value = []
                    for data in value:
                        is_hit = 0
                        for key_word in keywords:
                            result = re.search(key_word.keywords, data.text)
                            if result is None:  # 说明没有匹配到
                                is_hit += 1
                        if is_hit == len(keywords_id):
                            hit_value.append(data.paragraph_id)
                    if len(hit_value) == len(value):
                        # '说明范围内的句子都没有匹配到，那么就是都不包含，那么就是命中，高亮order_number对应的句子，key')
                        if warning_id:
                            warning_data = db_v1.session.query(QiInfoWarning).filter(
                                QiInfoWarning.id == warning_id).first_or_404()
                            warning_message = warning_data['message']
                            warning_ding_talk = warning_data['ding_talk']
                            warning_apps = warning_data['apps']
                            if warning_message:
                                warn_message(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), value[0].call_id, key,
                                             map_rule_name, warning_message)
                            if warning_ding_talk:
                                warn_ding_talk(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), value[0].call_id, key,
                                               map_rule_name, warning_ding_talk)
                            if warning_apps:
                                warn_apps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), value[0].call_id, key,
                                          map_rule_name, warning_apps)
                        try:
                            to_db(value[0].call_id, key, map_id, 1, None)
                        except Exception as e:
                            logger.error(traceback.format_exc())

            # 有前置条件的情况，此时，关键词细则中要么都是不包含，要么都是包含，要么包含&不包含，
            # 但是关键词细则的多个细则是交集的关系，只有paragraph_id命中次数等于细则个数才算是命中

        else:
            if rule_result[0].check_range == 0:
                qi_datas = db_v1.session.query(QiLabelParagraph.call_id, QiLabelParagraph.task_id,
                                               QiLabelParagraph.paragraph_id, QiLabelParagraph.order_number,
                                               QiLabelParagraph.text).filter(QiLabelParagraph.call_id.in_(call_datas)).all()
            elif rule_result[0].check_range == 1:
                tmp = db_v1.session.query(QiLabelParagraph.task_id,
                                          func.min(QiLabelParagraph.order_number).label('min_order_number')).filter(
                    QiLabelParagraph.call_id.in_(call_datas)).group_by(QiLabelParagraph.task_id).subquery()
                qi_datas = db_v1.session.query(QiLabelParagraph.call_id, QiLabelParagraph.task_id, QiLabelParagraph.paragraph_id,
                                         QiLabelParagraph.order_number, QiLabelParagraph.text).join(
                    tmp, and_(QiLabelParagraph.call_id.in_(call_datas),
                              QiLabelParagraph.task_id == tmp.c.task_id,
                              QiLabelParagraph.order_number == tmp.c.min_order_number)).all()
            else:
                tmp = db_v1.session.query(QiLabelParagraph.task_id, func.max(QiLabelParagraph.order_number)
                                    .label('max_order_number')).filter(QiLabelParagraph.role == 1).group_by(QiLabelParagraph.task_id).subquery()
                qi_datas = db_v1.session.query(QiLabelParagraph.call_id, QiLabelParagraph.task_id, QiLabelParagraph.paragraph_id,
                                         QiLabelParagraph.order_number, QiLabelParagraph.text).join(
                    tmp, and_(QiLabelParagraph.call_id.in_(call_datas),
                              QiLabelParagraph.task_id == tmp.c.task_id,
                              QiLabelParagraph.order_number == tmp.c.max_order_number)).all()

            if is_color_word != 0:
                color_str = {}
                for data in qi_datas:
                    is_hit = 0
                    color_id = []
                    for key_word in keywords:
                        if key_word.is_contains == 0:  # 不包含即命中
                            result = re.search(key_word.keywords, data.text)
                            if result is None:  # 命中
                                is_hit += 1
                        else:
                            result = re.search(key_word.keywords, data.text)  # 包含即命中
                            if not result is None:  # 命中
                                is_hit += 1
                                result_iter = re.finditer(key_word.keywords, data.text)
                                for i in result_iter:
                                    color_id.append(str(i.start()) + ',' + str(i.end() - 1))
                            color_str[data.paragraph_id] = "|".join(color_id)
                    if is_hit == len(keywords_id):
                        if warning_id:
                            warning_data = db_v1.session.query(QiInfoWarning).filter(
                                QiInfoWarning.id == warning_id).first_or_404()
                            warning_message = warning_data['message']
                            warning_ding_talk = warning_data['ding_talk']
                            warning_apps = warning_data['apps']
                            if warning_message:
                                warn_message(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                             data.paragraph_id,
                                             map_rule_name, warning_message)
                            if warning_ding_talk:
                                warn_ding_talk(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                               data.paragraph_id,
                                               map_rule_name, warning_ding_talk)
                            if warning_apps:
                                warn_apps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                          data.paragraph_id,
                                          map_rule_name, warning_apps)
                        try:
                            to_db(data.call_id, data.paragraph_id, map_id, 1, color_str[data.paragraph_id])
                        except Exception as e:
                            logger.error(traceback.format_exc())
            else:
                for data in qi_datas:
                    is_hit = 0
                    for key_word in keywords:
                        result = re.search(key_word.keywords, data.text)
                        if result is None:  # 说明没有匹配到
                            is_hit += 1
                    if is_hit == len(keywords_id):
                        if warning_id:
                            warning_data = db_v1.session.query(QiInfoWarning).filter(
                                QiInfoWarning.id == warning_id).first_or_404()
                            warning_message = warning_data['message']
                            warning_ding_talk = warning_data['ding_talk']
                            warning_apps = warning_data['apps']
                            if warning_message:
                                warn_message(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                             data.paragraph_id,
                                             map_rule_name, warning_message)
                            if warning_ding_talk:
                                warn_ding_talk(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                               data.paragraph_id,
                                               map_rule_name, warning_ding_talk)
                            if warning_apps:
                                warn_apps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                          data.paragraph_id,
                                          map_rule_name, warning_apps)
                        try:
                            to_db(data.call_id, data.paragraph_id, map_id, 1, None)
                        except Exception as e:
                            logger.error(traceback.format_exc())
    # return True


def speed_rule(call_datas, rule_id, map_id, warning_id, map_rule_name):
    session = db_v1.session()
    rule_result = session.query(QiInfoSpeed.rule_type,
                                QiInfoSpeed.speed_counts,
                                QiInfoSpeed.out_rule).filter_by(id=rule_id, is_deleted=0).all()
    if rule_result:
        datas = session.query(QiLabelParagraph.paragraph_id, QiLabelParagraph.call_id, QiLabelParagraph.task_id,
                              QiLabelParagraph.duration, func.char_length(QiLabelParagraph.text).label('len_text')).filter(
            and_(QiLabelParagraph.role == 1, func.char_length(QiLabelParagraph.text) >= rule_result[0].out_rule,
                 QiLabelParagraph.call_id.in_(call_datas))).all()
        hit_pid = []
        # hit_tid = []
        if rule_result[0].rule_type == 1:   # 小于
            for data in datas:
                if (data.len_text/data.duration)*60000 < rule_result[0].speed_counts:
                    hit_pid.append(data.paragraph_id)
                    if warning_id:
                        warning_data = db_v1.session.query(QiInfoWarning).filter(
                            QiInfoWarning.id == warning_id).first_or_404()
                        warning_message = warning_data['message']
                        warning_ding_talk = warning_data['ding_talk']
                        warning_apps = warning_data['apps']
                        if warning_message:
                            warn_message(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id, data.paragraph_id,
                                         map_rule_name, warning_message)
                        if warning_ding_talk:
                            warn_ding_talk(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                           data.paragraph_id, map_rule_name, warning_ding_talk)
                        if warning_apps:
                            warn_apps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id, data.paragraph_id,
                                      map_rule_name, warning_apps)
                    try:
                        to_db(data.call_id, data.paragraph_id, map_id, 1, None)
                    except Exception as e:
                        logger.error(traceback.format_exc())
                    # hit_tid.append(data.task_id)
        else:  # 超过
            for data in datas:
                if (data.len_text/data.duration)*60000 > rule_result[0].speed_counts:
                    hit_pid.append(data.paragraph_id)
                    if warning_id:
                        warning_data = db_v1.session.query(QiInfoWarning).filter(QiInfoWarning.id == warning_id).first_or_404()
                        warning_message = warning_data['message']
                        warning_ding_talk = warning_data['ding_talk']
                        warning_apps = warning_data['apps']
                        if warning_message:
                            warn_message(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id, data.paragraph_id,
                                         map_rule_name, warning_message)
                        if warning_ding_talk:
                            warn_ding_talk(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                           data.paragraph_id, map_rule_name, warning_ding_talk)
                        if warning_apps:
                            warn_apps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id, data.paragraph_id,
                                      map_rule_name, warning_apps)
                    try:
                        to_db(data.call_id, data.paragraph_id, map_id, 1, None)
                    except Exception as e:
                        logger.error(traceback.format_exc())
                    # hit_tid.append(data.task_id)


def duration_rule(call_datas, rule_id, map_id, warning_id, map_rule_name):
    session = db_v1.session()
    rule_result = session.query(QiInfoDuration.duration, QiInfoDuration.rule_type).filter_by(id=rule_id).all()
    if rule_result:
        datas = session.query(QiInfoTraffic.call_id, QiInfoTraffic.duration).filter(QiInfoTraffic.call_id.in_(call_datas)).all()
        hit_cid = []
        if rule_result[0].rule_type == 1:
            for data in datas:
                if data.duration > rule_result[0].duration:
                    hit_cid.append(data.call_id)
                    if warning_id:
                        warning_data = db_v1.session.query(QiInfoWarning).filter(
                            QiInfoWarning.id == warning_id).first_or_404()
                        warning_message = warning_data['message']
                        warning_ding_talk = warning_data['ding_talk']
                        warning_apps = warning_data['apps']
                        if warning_message:
                            warn_message(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id, None,
                                         map_rule_name, warning_message)
                        if warning_ding_talk:
                            warn_ding_talk(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                           None, map_rule_name, warning_ding_talk)
                        if warning_apps:
                            warn_apps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id, None,
                                      map_rule_name. warning_apps)
                    try:
                        to_db(data.call_id, None, map_id, 0, None)
                    except Exception as e:
                        logger.error(traceback.format_exc())
        else:
            for data in datas:
                if data.duration < rule_result[0].duration:
                    hit_cid.append(data.call_id)
                    if warning_id:
                        warning_data = db_v1.session.query(QiInfoWarning).filter(
                            QiInfoWarning.id == warning_id).first_or_404()
                        warning_message = warning_data['message']
                        warning_ding_talk = warning_data['ding_talk']
                        warning_apps = warning_data['apps']
                        if warning_message:
                            warn_message(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id, None,
                                         map_rule_name, warning_message)
                        if warning_ding_talk:
                            warn_ding_talk(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                           None, map_rule_name, warning_ding_talk)
                        if warning_apps:
                            warn_apps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id, None,
                                      map_rule_name, warning_apps)
                    try:
                        to_db(data.call_id, None, map_id, 0, None)
                    except Exception as e:
                        logger.error(traceback.format_exc())
    # return hit_cid


def interruption_rule(call_datas, rule_id, map_id, warning_id, map_rule_name):
    session = db_v1.session()
    rule_result = session.query(QiInfoInterruption.cross_time, QiInfoInterruption.out_rule).filter_by(id=rule_id).all()
    if rule_result:
        datas = session.query(QiLabelParagraph.call_id, QiLabelParagraph.task_id, QiLabelParagraph.paragraph_id,
                              QiLabelParagraph.start_time, QiLabelParagraph.end_time,
                              func.char_length(QiLabelParagraph.text).label('len_text'), QiLabelParagraph.role).filter(
            QiLabelParagraph.call_id.in_(call_datas)).order_by("task_id", "start_time").all()
        hit_pid = []
        for i in range(1, len(datas)):
            if datas[i].task_id != datas[i-1].task_id:
                continue
            if not datas[i].role is None:
                if (datas[i-1].end_time - datas[i].start_time) > rule_result[0].cross_time:
                    if datas[i].role == 1:
                        if (datas[i].len_text >= rule_result[0].out_rule) and (datas[i].paragraph_id not in hit_pid):
                            hit_pid.append(datas[i].paragraph_id)
                            if warning_id:
                                warning_data = db_v1.session.query(QiInfoWarning).filter(
                                    QiInfoWarning.id == warning_id).first_or_404()
                                warning_message = warning_data['message']
                                warning_ding_talk = warning_data['ding_talk']
                                warning_apps = warning_data['apps']
                                if warning_message:
                                    warn_message(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datas[i].call_id,
                                                 datas[i].paragraph_id, map_rule_name, warning_message)
                                if warning_ding_talk:
                                    warn_ding_talk(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datas[i].call_id,
                                                   datas[i].paragraph_id, map_rule_name, warning_ding_talk)
                                if warning_apps:
                                    warn_apps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datas[i].call_id,
                                              datas[i].paragraph_id, map_rule_name, warning_apps)
                            try:
                                to_db(datas[i].call_id, datas[i].paragraph_id, map_id, 1, None)
                            except Exception as e:
                                logger.error(traceback.format_exc())

                    else:
                        if (datas[i-1].len_text >= rule_result[0].out_rule) and (datas[i-1].paragraph_id not in hit_pid):
                            hit_pid.append(datas[i-1].paragraph_id)
                            if warning_id:
                                warning_data = db_v1.session.query(QiInfoWarning).filter(
                                    QiInfoWarning.id == warning_id).first_or_404()
                                warning_message = warning_data['message']
                                warning_ding_talk = warning_data['ding_talk']
                                warning_apps = warning_data['apps']
                                if warning_message:
                                    warn_message(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datas[i].call_id,
                                                 datas[i].paragraph_id, map_rule_name, warning_message)
                                if warning_ding_talk:
                                    warn_ding_talk(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datas[i].call_id,
                                                   datas[i].paragraph_id, map_rule_name, warning_ding_talk)
                                if warning_apps:
                                    warn_apps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datas[i].call_id,
                                              datas[i].paragraph_id, map_rule_name, warning_apps)
                            try:
                                to_db(datas[i-1].call_id, datas[i-1].paragraph_id, map_id, 1, None)
                            except Exception as e:
                                logger.error(traceback.format_exc())
    # return hit_pid


def silence_rule(call_datas, rule_id, map_id, warning_id, map_rule_name):
    session = db_v1.session()
    rule_result = session.query(QiInfoSilence.quiet_time).filter_by(id=rule_id, is_deleted=0).all()
    if rule_result:
        datas = session.query(QiLabelSentence.call_id, QiLabelSentence.task_id, QiLabelSentence.paragraph_id,
                              QiLabelSentence.start_time, QiLabelSentence.end_time, QiLabelSentence.role,
                              QiLabelSentence.text, func.char_length(QiLabelSentence.text).label('len_text')).filter(
            QiLabelSentence.call_id.in_(call_datas)).order_by("task_id", "start_time").all()

        hit_pid = []
        re_str = '(等一下|稍等)'
        for i in range(1, len(datas)):
            if datas[i].task_id != datas[i - 1].task_id:
                continue
            if not datas[i].role is None:
                if (datas[i].start_time - datas[i - 1].end_time) > rule_result[0].quiet_time:
                    if datas[i].role == 1:
                        n = 1
                        sum_words = datas[i].len_text
                        while datas[i].task_id == datas[i-n].task_id:
                            if datas[i-n].role != 1 or datas[i].paragraph_id == datas[i-n].paragraph_id:
                                n += 1
                                sum_words += datas[i-n].len_text
                            else:
                                re_result = re.search(re_str, datas[i-n].text)
                                if (re_result is None) or (sum_words >= 8):
                                    if datas[i].paragraph_id not in hit_pid:
                                        hit_pid.append(datas[i].paragraph_id)
                                        if warning_id:
                                            warning_data = db_v1.session.query(QiInfoWarning).filter(
                                                QiInfoWarning.id == warning_id).first_or_404()
                                            warning_message = warning_data['message']
                                            warning_ding_talk = warning_data['ding_talk']
                                            warning_apps = warning_data['apps']
                                            if warning_message:
                                                warn_message(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                             datas[i].call_id,
                                                             datas[i].paragraph_id, map_rule_name, warning_message)
                                            if warning_ding_talk:
                                                warn_ding_talk(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                               datas[i].call_id,
                                                               datas[i].paragraph_id, map_rule_name, warning_ding_talk)
                                            if warning_apps:
                                                warn_apps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                          datas[i].call_id,
                                                          datas[i].paragraph_id, map_rule_name, warning_apps)
                                        try:
                                            to_db(datas[i].call_id, datas[i].paragraph_id, map_id, 1, None)
                                        except Exception as e:
                                            logger.error(traceback.format_exc())
                                break
                    else:
                        m = 1
                        sum_words = datas[i].len_text
                        while datas[i].task_id == datas[i-m].task_id:
                            if datas[i-m].role != 1:
                                m += 1
                                sum_words += datas[i-m].len_text
                            else:
                                re_result = re.search(re_str, datas[i-m].text)
                                if (re_result is None) or (sum_words >= 8):
                                    j = 1
                                    while datas[i].task_id == datas[i+j].task_id:
                                        if datas[i+j].role != 1:
                                            j += 1
                                        else:
                                            if datas[i+j].paragraph_id not in hit_pid:
                                                hit_pid.append(datas[i+j].paragraph_id)
                                                if warning_id:
                                                    warning_data = db_v1.session.query(QiInfoWarning).filter(
                                                        QiInfoWarning.id == warning_id).first_or_404()
                                                    warning_message = warning_data['message']
                                                    warning_ding_talk = warning_data['ding_talk']
                                                    warning_apps = warning_data['apps']
                                                    if warning_message:
                                                        warn_message(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                     datas[i].call_id,
                                                                     datas[i].paragraph_id, map_rule_name, warning_message)
                                                    if warning_ding_talk:
                                                        warn_ding_talk(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                       datas[i].call_id,
                                                                       datas[i].paragraph_id, map_rule_name, warning_ding_talk)
                                                    if warning_apps:
                                                        warn_apps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                  datas[i].call_id,
                                                                  datas[i].paragraph_id, map_rule_name, warning_apps)
                                                try:
                                                    to_db(datas[i+j].call_id, datas[i+j].paragraph_id, map_id, 1, None)
                                                except Exception as e:
                                                    logger.error(traceback.format_exc())
                                            break
                                break
    # return hit_pid


def taboo_rule(call_datas, rule_id, map_id, warning_id, map_rule_name):
    rule_result = db_v1.session.query(QiInfoTabooWord).filter_by(id=rule_id, is_deleted=0).all()
    if rule_result:
        datas = db_v1.session.query(QiLabelParagraph.call_id, QiLabelParagraph.paragraph_id, QiLabelParagraph.text).filter(
            QiLabelParagraph.call_id.in_(call_datas)).all()
        for data in datas:
            ParseOp = main_func()
            parse_res = ParseOp.words_replace(data.text)
            if parse_res["defraud"]:
                hit_location = []
                for i in parse_res["defraud"]:
                    hit_location.append(str(i["start"]) + ',' + str(i["end"]))
                color_location = "|".join(hit_location)
                if warning_id:
                    warning_data = db_v1.session.query(QiInfoWarning).filter(
                        QiInfoWarning.id == warning_id).first_or_404()
                    warning_message = warning_data['message']
                    warning_ding_talk = warning_data['ding_talk']
                    warning_apps = warning_data['apps']
                    if warning_message:
                        warn_message(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                     data.paragraph_id,
                                     map_rule_name, warning_message)
                    if warning_ding_talk:
                        warn_ding_talk(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                       data.paragraph_id,
                                       map_rule_name, warning_ding_talk)
                    if warning_apps:
                        warn_apps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                  data.paragraph_id,
                                  map_rule_name, warning_apps)
                try:
                    to_db(data.call_id, data.paragraph_id, map_id, 1, color_location)
                except Exception as e:
                    logger.error(traceback.format_exc())


def emotion_rule(call_datas, rule_id, map_id, warning_id, map_rule_name):
    rule_result = db_v1.session.query(QiInfoEmotion).filter_by(id=rule_id, is_deleted=0).all()
    if rule_result:
        datas = db_v1.session.query(QiLabelParagraph.call_id, QiLabelParagraph.paragraph_id, QiLabelParagraph.text).filter(
            QiLabelParagraph.call_id.in_(call_datas), QiLabelParagraph.role == 1).all()
        import torch
        model = torch.load('D:/pycharm_project/AI_Speech_QIA/src/app/libs/emotion_libs/model/higru-sf_DownloadedYyh.pt', map_location='cp')
        for data in datas:
            sentence = [(data.text, 0)]
                        # ('我觉得这次的外卖太难吃了差评', 0),
                        # ('哈哈哈哈说的对', 0),
                        # ('所以今天你让我很生气', 0)]
            vocab, vocab_emo = load_vocab(
                'D:/pycharm_project/AI_Speech_QIA/src/app/libs/emotion_libs/DownloadedYyh_vocab.pt',
                'D:/pycharm_project/AI_Speech_QIA/src/app/libs/emotion_libs/DownloadedYyh_emodict.pt')
            feats, emo_list = get_feat(sentence, vocab)
            emotion_result = get_prediction(feats, model, vocab_emo, emo_list, Weight, Thread)
            if emotion_result[0].lower() == 'negative'.lower():
                if warning_id:
                    warning_data = db_v1.session.query(QiInfoWarning).filter(
                        QiInfoWarning.id == warning_id).first_or_404()
                    warning_message = warning_data['message']
                    warning_ding_talk = warning_data['ding_talk']
                    warning_apps = warning_data['apps']
                    if warning_message:
                        warn_message(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                     data.paragraph_id,
                                     map_rule_name, warning_message)
                    if warning_ding_talk:
                        warn_ding_talk(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                       data.paragraph_id,
                                       map_rule_name, warning_ding_talk)
                    if warning_apps:
                        warn_apps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.call_id,
                                  data.paragraph_id,
                                  map_rule_name, warning_apps)
                try:
                    to_db(data.call_id, data.paragraph_id, map_id, 1, None)
                except Exception as e:
                    logger.error(traceback.format_exc())

















