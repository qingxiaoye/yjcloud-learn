# -*- coding: utf-8 -*-
# from enum import Enum
from enum import Enum


class ClientTypeEnum(Enum):
    USER_NICKNAME = 100
    USER_EMAIL = 101
    USER_MOBILE = 102

    USER_MINA = 200
    USER_WX = 201


class ChoicesExItemEnum(Enum):
    ALL = 0  # 全有
    NEITHER = -1  # 全没有


class ChoicesExTypeEnum(Enum):
    TYPE_NOT = 0  # 不扩展
    TYPE_NEITHER = 1  # 扩展全没有
    TYPE_ALL = 2  # 扩展全有
    TYPE_NEITHER_ALL = 3  # 扩展全有


class TrafficFileStatus(Enum):
    NO_FILE_HANDLE = 0  # 未处理
    FILE_PREPROCESS_FINISH = 1  # 预处理完成
    FILE_TRANSLATION_FINISH = 2  # 转译完成
    FILE_QUALITY_FINISH = 3  # 质检完成
    FILE_REVIEW_FINISH = 4  # 已复核


class TrafficHitStatus(Enum):
    NO_QUALITY = 0  # 未质检
    HIT_SUCCESS = 1  # 命中
    HIT_FAILED = 2  # 未命中


class ReviewStatus(Enum):
    NO_REVIEW = 0  # 未复核
    REVIEW_RIGHT = 1  # 复核结果为正确
    REVIEW_WRONG = 2  # 复核结果为错误


class TrafficAppealStatus(Enum):
    NO_APPEAL = 0  # 未复核
    APPEAL_FINISH = 1  # 申诉处理完成
    APPEAL_UNFINISHED = 2  # 申诉待处理


class DetailHitStatus(Enum):
    HIT_SUCCESS = 1  # 命中
    HIT_FAILED = 0  # 未命中


class DetailHitType(Enum):
    TYPE_PARAGRAPH = 1  # 命中段落
    TYPE_CALL = 0  # 命中通话时长规则


class ResultAppealStatus(Enum):
    APPEAL_SPONSOR = 0  # 发起
    APPEAL_WITHDRAW = 1  # 撤销
    APPEAL_AGREE = 3  # 同意
    APPEAL_REJECT = 4  # 驳回


class RuleType(Enum):
    TYPE_KEYWORDS = 0  # 关键词规则
    TYPE_TABOO = 1  # 服务忌语规则
    TYPE_SPEED = 2  # 语速规则
    TYPE_INTERRUPT = 3  # 抢插话规则
    TYPE_DURATION = 4  # 通话时长规则
    TYPE_SILENCE = 5  # 静音时长规则
    TYPE_EMOTION = 6  # 异常情绪规则


class RoleLabel(Enum):
    LABEL_AGENT = 1  # 座席
    LABEL_CLIENT = 0  # 客户


class KeyWordsContain(Enum):
    CONTAIN = 1  # 包含
    NO_CONTAIN = 0  # 不包含


class PreconditionContain(Enum):
    CONTAIN = 1  # 有前置条件
    NO_CONTAIN = 0  # 没有前置条件


class KeyWordsCheckRange(Enum):
    RANGE_FIRST = 1  # 首句
    RANGE_END = -1  # 末句
    RANGE_ALL = 0  # 所有句


class SpeedRuleType(Enum):
    SPEED_EXCEED = 0  # 超过
    SPEED_LITTLE = 1  # 小于


class DurationRuleType(Enum):
    SPEED_EXCEED = 1  # 超过
    SPEED_LITTLE = 0  # 小于


class RepeatCallTime(Enum):
    TIME_FIRST = 1  # 首呼
    TIME_NOT_FIRST = 0  # 非首呼


class RepeatCallSolve(Enum):
    SOLVE = 1  # 首呼
    UNSOLVED = 0  # 未解决


class CaseType(Enum):
    CASE_POSITIVE = 1  # 正例
    CASE_NEGTIVE = 0  # 反例