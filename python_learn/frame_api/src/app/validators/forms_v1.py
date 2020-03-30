# -*- coding: utf-8 -*-
import os

from wtforms import StringField, IntegerField, FieldList, FormField, DateTimeField, DecimalField
from wtforms import ValidationError
from wtforms.validators import DataRequired, length, Email, Regexp, Required

# from app.libs.enums import ClientTypeEnum, LabelTaskStatusEnum
# from app.models.v2.web.label import LabelProject, LabelTask
# from app.models.v2.web.sysmgr import User, Role, Permission
from app.models.qi_qia_models import QiInfoMapRule, QiInfoWarning, QiInfoTemplate, QiInfoProject, QiInfoBranch, \
    QiInfoRole, QiInfoUser
from app.validators.base import BaseForm as Form


# 公共Form
class IDForm(Form):
    """ 用于id检查 """
    id = IntegerField(validators=[DataRequired()])


class TokenForm(Form):
    token = StringField()


class QiaResultSearchForm(Form):
    call_id = StringField()
    call_time_left = IntegerField()
    call_time_right = IntegerField()
    agent_id = StringField()
    review_status = IntegerField()
    appeal_status = IntegerField()
    proj_code = StringField()  # 是、否
    branch_code = StringField()
    score_min = IntegerField()
    score_max = IntegerField()
    rule_type = StringField()
    call_duration_min = IntegerField()
    call_duration_max = IntegerField()


class ReviewList(Form):
    call_id = StringField()


class ReviewOpinionSubmit(Form):
    call_id = StringField()
    update_id = StringField()
    score = IntegerField()
    review_uid = IntegerField()
    review_opinion = StringField()


class AppealSubmit(Form):
    call_id = StringField()
    hit_id = IntegerField()
    appeal_uid = IntegerField()
    appeal_reason = StringField()
    score = IntegerField()


class AppealDeal(Form):
    call_id = StringField()
    appeal_id = IntegerField()
    hit_id = IntegerField()
    appeal_result = IntegerField()
    conduct_uid = IntegerField()


class AppealRecall(Form):
    call_id = StringField()
    appeal_id = IntegerField()


class AddCase(Form):
    call_id = StringField()
    case_type = IntegerField()
    case_desc = StringField()
    create_uid = IntegerField()


class EmotionRule(Form):
    rule_name = StringField()
    rule_type = StringField()
    rule_desc = StringField()
    score = IntegerField()
    role = IntegerField()


# class TabooRule(Form):
#     rule_name = StringField()
#     rule_desc = StringField()
#     score = IntegerField()


class InterruptionRule(Form):
    rule_name = StringField()
    rule_type = StringField()
    rule_desc = StringField()
    score = IntegerField()
    cross_time = IntegerField()
    out_rule = IntegerField()


class SpeedRule(Form):
    rule_name = StringField()
    rule_type = StringField()
    rule_desc = StringField()
    score = IntegerField()
    min_counts = IntegerField()
    max_counts = IntegerField()
    out_rule = IntegerField()


class DurationRule(Form):
    rule_name = StringField()
    rule_type = StringField()
    rule_desc = StringField()
    score = IntegerField()
    duration_type = IntegerField()
    out_rule = IntegerField()


class SilenceRule(Form):
    rule_name = StringField()
    rule_type = StringField()
    rule_desc = StringField()
    score = IntegerField()
    slience_duration = IntegerField()


class Precondition(Form):
    role = IntegerField()
    is_contains = IntegerField()
    words = StringField()


class Keywords(Form):
    is_contains = IntegerField()
    words = StringField()


class KeywordsRule(Form):
    rule_name = StringField()
    rule_type = StringField()
    rule_desc = StringField()
    score = IntegerField()
    is_precondition = IntegerField()
    check_range = IntegerField()
    left_boundary = IntegerField()
    right_boundary = IntegerField()
    precondition = FieldList(FormField(Precondition))
    keywords = FieldList(FormField(Keywords))


class NewTemplate(Form):
    template_name = StringField(validators=[DataRequired(message='质检模板名称：不允许为空')])
    create_uid = IntegerField()
    base_score = IntegerField(validators=[DataRequired(message='模板起始分值：不允许为空')])
    template_desc = StringField()
    emotion_rule = FieldList(StringField())
    taboo_rule = FieldList(StringField())
    interruption_rule = FieldList(StringField())
    speed_rule = FieldList(StringField())
    duration_rule = FieldList(StringField())
    silence_rule = FieldList(StringField())
    keywords_rule = FieldList(StringField())


class TemplateEditList(Form):
    template_id = IntegerField()


class TemplateEdit(Form):
    template_id = IntegerField()  # 关系表中template_id
    map_rule_id = StringField()  # 关系表ID
    template_name = StringField(validators=[DataRequired(message='质检模板名称：不允许为空')])
    create_uid = IntegerField()
    base_score = IntegerField(validators=[DataRequired(message='模板起始分值：不允许为空')])
    template_desc = StringField()
    emotion_rule = FieldList(StringField())
    taboo_rule = FieldList(StringField())
    interruption_rule = FieldList(StringField())
    speed_rule = FieldList(StringField())
    duration_rule = FieldList(StringField())
    silence_rule = FieldList(StringField())
    keywords_rule = FieldList(StringField())


class QcFunc(Form):
    call_datas = FieldList(StringField())


class LoginForm(Form):
    account = StringField(validators=[DataRequired(message='账号：不允许为空'), length(min=2, max=24)])
    password = StringField(
        validators=[DataRequired(), Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}', message='密码：只允许6位至22位字母数字以及_*&$#@')])


class UserAddForm(Form):
    account = StringField(validators=[DataRequired(), length(min=2, max=24)])
    password = StringField(validators=[DataRequired(), Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}')])
    nickname = StringField(validators=[DataRequired(), length(max=24)])
    telephone = StringField()
    rid = IntegerField(validators=[DataRequired(message='角色类型：不允许为空')])
    agent_id = StringField()
    bid = IntegerField()

    def validate_account(self, value):
        if QiInfoUser.query.filter_by(accout=value.data).first():
            raise ValidationError(message=u"该用户账号已经存在，请重新命名")

    def validate_nickname(self, value):
        if QiInfoUser.query.filter_by(nickname=value.data).first():
            raise ValidationError(message=u"该用户昵称已存在，请重新命名")

    def validate_agent_id(self, value):
        if value.data:
            if QiInfoUser.query.filter_by(agent_id=value.data).first():
                raise ValidationError(message=u"该坐席已存在，请重新命名")

    def validate_bid(self, value):
        if value.data:
            if not QiInfoBranch.query.filter_by(id=value.data).first():
                raise ValidationError(message=u"非法部门ID")


class PasswordForm(Form):
    secret = StringField(validators=[DataRequired(message='密码：不允许为空'),
                                     Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}', message='密码：只允许6位至22位字母数字以及_*&$#@')])


class UserSearchForm(Form):
    account = StringField()
    agent_id = StringField()
    bid = IntegerField()
    rid = IntegerField()


class UserEditForm(Form):
    account = StringField()
    password = StringField(validators=[DataRequired(), Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}')])
    nickname = StringField(validators=[DataRequired(), length(max=24)])
    telephone = StringField()
    rid = IntegerField(validators=[DataRequired(message='角色类型：不允许为空')])
    agent_id = StringField()
    bid = IntegerField()

    def validate_rid(self, value):
        if not QiInfoRole.query.filter_by(id=value.data).first():
            raise ValidationError(message=u"非法角色ID")

    def validate_bid(self, value):
        if value.data:
            if not QiInfoBranch.query.filter_by(id=value.data).first():
                raise ValidationError(message=u"非法部门ID")


class PasswordEditForm(Form):
    old_password = StringField(validators=[DataRequired(message='密码：不允许为空'),
                                           Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}',
                                                  message='密码：只允许6位至22位字母数字以及_*&$#@')])
    new_password = StringField(validators=[DataRequired(message='密码：不允许为空'),
                                           Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}',
                                                  message='密码：只允许6位至22位字母数字以及_*&$#@')])
    confirm_password = StringField(validators=[DataRequired(message='密码：不允许为空'),
                                               Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}',
                                                      message='密码：只允许6位至22位字母数字以及_*&$#@')])


class BranchAddForm(Form):
    branch_name = StringField(validators=[DataRequired(message='部门名称：请在2到24位字符中间'), length(min=2, max=24)])
    superior_id = IntegerField(validators=[DataRequired(message='上级部门：不允许为空')])

    def validate_superior_id(self, value):
        print(QiInfoBranch.query.filter_by(id=value.data))
        if not QiInfoBranch.query.filter_by(id=value.data).first():
            raise ValidationError(message=u"非法上级部门ID")


class BranchSearchForm(Form):
    branch_name = StringField()


class BranchEditForm(Form):
    branch_name = StringField(validators=[DataRequired(message='部门名称：请在2到24位字符中间'), length(min=2, max=24)])
    superior_id = IntegerField(validators=[DataRequired(message='上级部门：不允许为空')])

    def validate_superior_id(self, value):
        if not QiInfoBranch.query.filter_by(id=value.data).first():
            raise ValidationError(message=u"非法上级部门ID")


class QiProjectForm(Form):
    pro_name = StringField(validators=[DataRequired(message='项目名称：不允许为空')])
    original_project = StringField(validators=[DataRequired(message='原厂项目标识：不允许为空')])
    qi_template = IntegerField(validators=[DataRequired(message='质检模板：不允许为空')])
    lm_id = StringField()
    proj_desc = StringField(length(max=100))

    def validate_pro_name(self, value):
        if QiInfoProject.query.filter_by(pro_name=value.data).first():
            raise ValidationError(message=u"该项目名称已存在，如要新建，请修改项目名称")

    def validate_original_project(self, value):
        if QiInfoProject.query.filter_by(original_project=value.data).first():
            raise ValidationError(message=u"该原厂项目已存在，如要新建，请删除原有项目")

    def validate_qi_template(self, value):
        if not QiInfoTemplate.query.filter_by(id=value.data).first():
            raise ValidationError(message=u"该质检模板不存在")


class QiProjectEditForm(Form):
    pro_name = StringField(validators=[DataRequired(message='项目名称：不允许为空')])
    original_project = StringField(validators=[DataRequired(message='原厂项目标识：不允许为空')])
    qi_template = IntegerField(validators=[DataRequired(message='质检模板：不允许为空')])
    lm_id = StringField()
    proj_desc = StringField(length(max=5))

    def validate_qi_template(self, value):
        if not QiInfoTemplate.query.filter_by(id=value.data).first():
            raise ValidationError(message=u"该质检模板不存在")


class QiProjectSearchForm(Form):
    pro_name = StringField()
    proj_code = StringField()


class QiCallForm(Form):
    call_id = StringField()
    call_time_left = IntegerField()
    call_time_right = IntegerField()
    agent_id = StringField()
    file_status = IntegerField()
    proj_code = StringField()
    branch_code = StringField()
    score_min = IntegerField()
    score_max = IntegerField()
    column_name = StringField()
    column_order = StringField()
    rule_type = StringField()
    key_word = StringField()


class QiCallSearchForm(Form):
    create_time_left = IntegerField()
    create_time_right = IntegerField()
    nickname = StringField()


class QiCaseEditForm(Form):
    case_type = IntegerField()
    case_desc = StringField()
    hit_rules = StringField()


class QiaWarningForm(Form):
    warning_name = StringField(validators=[DataRequired(message='预警名称：不允许为空')])
    warning_desc = StringField()
    hit_rules = FieldList(IntegerField(), validators=[DataRequired(message='质检模板：不允许为空')])
    # message
    # ding_talk
    # apps至少配置一类
    message = FieldList(StringField(), max_entries=10)
    ding_talk = FieldList(StringField(), max_entries=3)
    apps = FieldList(StringField(), max_entries=3)

    def validate_warning_name(self, value):
        if QiInfoWarning.query.filter_by(warning_name=value.data).first():
            raise ValidationError(message=u"该预警名称已存在，如要新建，请删除原有预警")

    def validate_hit_rules(self, value):
        if value.data:
            for hit_rule in value.data:
                if QiInfoMapRule.query.filter(QiInfoMapRule.is_deleted == 0,
                                              QiInfoMapRule.id == hit_rule,
                                              QiInfoMapRule.warning_id != 0, ).first():
                    raise ValidationError(message=u"该质检规则对应的预警已存在，如要新建，请删除原有预警")


class QiWarningEditForm(Form):
    warning_name = StringField(validators=[DataRequired(message='预警名称：不允许为空')])
    warning_desc = StringField()
    hit_rules = FieldList(IntegerField(), validators=[DataRequired(message='质检模板：不允许为空')])
    message = FieldList(StringField(), max_entries=10)
    ding_talk = FieldList(StringField(), max_entries=3)
    apps = FieldList(StringField(), max_entries=3)

    def validate_warning_name(self, value):
        wid = IDForm().validate_for_api().id.data
        if QiInfoWarning.query.filter(QiInfoWarning.warning_name == value.data,
                                      QiInfoWarning.id != wid).first():
            raise ValidationError(message=u"该预警名称已存在，如要新建，请删除原有预警")

    def validate_hit_rules(self, value):
        wid = IDForm().validate_for_api().id.data
        if value.data:
            for hit_rule in value.data:
                if QiInfoMapRule.query.filter(QiInfoMapRule.is_deleted == 0,
                                              QiInfoMapRule.id == hit_rule,
                                              QiInfoMapRule.warning_id != 0,
                                              QiInfoMapRule.warning_id != wid, ).first():
                    raise ValidationError(message=u"该质检规则对应的预警已存在，如要新建，请删除原有预警")


class StatQiSituationForm(Form):
    call_time_left = IntegerField()
    call_time_right = IntegerField()


class StatQiScoreForm(Form):
    call_time_left = IntegerField()
    call_time_right = IntegerField()
    branch_id = IntegerField()
    agent_id = StringField()
    period = StringField()


class StatQiScoreBranchForm(Form):
    call_time_left = IntegerField()
    call_time_right = IntegerField()
    branch_code = StringField()
    branch_name = StringField()


class StatQiScoreAgentForm(Form):
    call_time_left = IntegerField()
    call_time_right = IntegerField()
    branch_code = StringField()
    branch_name = StringField()
    agent_id = StringField()


class StatQiRuleForm(Form):
    call_time_left = IntegerField()
    call_time_right = IntegerField()
    period = StringField()
    rule_type = IntegerField()
    column_order = StringField()
    column_name = StringField()


class StatOpDurationForm(Form):
    call_time_left = IntegerField()
    call_time_right = IntegerField()
    topn = IntegerField()
    column_order = StringField()
    column_name = StringField()


class StatOpSilenceForm(Form):
    call_time_left = IntegerField()
    call_time_right = IntegerField()
    period = StringField()
    topn = IntegerField()


class StatOpRepeatForm(Form):
    call_time_left = IntegerField()
    call_time_right = IntegerField()
    type_name = StringField()
    branch_id = IntegerField()
    branch_code = StringField()
    agent_id = StringField()


class StatOpReasonForm(Form):
    call_time_left = IntegerField()
    call_time_right = IntegerField()
    reason_id = IntegerField()
    period = IntegerField()


class StatOpBusinessForm(Form):
    recent_period = IntegerField(validators=[DataRequired(message=u'最近时间：不允许为空')])


class StatOpHotForm(Form):
    recent_period = IntegerField(validators=[DataRequired(message=u'最近时间：不允许为空')])
