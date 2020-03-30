# coding: utf-8
from sqlalchemy import Column, DateTime, String, text, Date, DECIMAL
from sqlalchemy.dialects.mysql import INTEGER, SMALLINT, VARCHAR
# from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

from app.libs.error_code import AuthFailed
from app.models.base import Base, db_v1


# Base = declarative_base()
# metadata = Base.metadata


class QiCallDuration(Base):
    __tablename__ = 'qi_call_duration'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    call_start_time = Column(DateTime)
    call_id = Column(VARCHAR(64), nullable=False, unique=True)
    duration = Column(INTEGER(11), nullable=False)
    effective_duration = Column(INTEGER(11), nullable=False)
    silence_duration = Column(INTEGER(11), nullable=False)
    cust_effective = Column(INTEGER(11), nullable=False)
    agent_effective = Column(INTEGER(11), nullable=False)
    cust_silence = Column(INTEGER(11), nullable=False)
    agent_silence = Column(INTEGER(11), nullable=False)


class QiCommonRegion(Base):
    __tablename__ = 'qi_common_region'

    insert_time = Column(INTEGER(11), comment='数据插入的时间')
    is_deleted = Column(SMALLINT(6), server_default=text("'0'"), comment='伪删除标识：\\n0：正常，1：已删除')
    id = Column(INTEGER(11), primary_key=True, comment='区域ID')
    name = Column(String(50), nullable=False, index=True, comment='区域名称')
    parent_id = Column(INTEGER(11), nullable=False, index=True, server_default=text("'0'"), comment='区域父级ID：无父级为0')
    level = Column(SMALLINT(6), comment='区域级别：0：省级；1：市级；2：区级')


class QiInfoBranch(Base):
    __tablename__ = 'qi_info_branch'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    branch_name = Column(VARCHAR(24), nullable=False)
    branch_code = Column(VARCHAR(24))
    branch_desc = Column(VARCHAR(200))
    create_time = Column(INTEGER(11))
    superior_id = Column(INTEGER(11))

    subbranch_ids_all = []
    subbranch_ids_direct = []

    def keys(self):
        return ['id','branch_name','branch_code','branch_desc','create_time','superior_id',]


class QiInfoBusinessType(Base):
    __tablename__ = 'qi_info_business_type'

    id = Column(INTEGER(11), primary_key=True)
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    type_code = Column(String(50), nullable=False)
    type_name = Column(String(50), nullable=False)
    rule_desc = Column(String(500))


class QiInfoCallReasonType(Base):
    __tablename__ = 'qi_info_call_reason_type'

    id = Column(INTEGER(11), primary_key=True)
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    type_code = Column(String(50), nullable=False)
    type_name = Column(String(50), nullable=False)
    rule_desc = Column(String(500))


class QiInfoCase(Base):
    __tablename__ = 'qi_info_case'

    insert_time = Column(INTEGER(11), index=True)
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    call_id = Column(VARCHAR(64), nullable=False, unique=True)
    create_uid = Column(VARCHAR(255), nullable=False)
    create_time = Column(DateTime, nullable=False)
    case_type = Column(SMALLINT(6))
    business_type = Column(VARCHAR(64))
    case_desc = Column(VARCHAR(200))


class QiInfoDetailedkw(Base):
    __tablename__ = 'qi_info_detailedkw'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    rule_name = Column(VARCHAR(50))
    create_uid = Column(INTEGER(11), nullable=False)
    create_time = Column(DateTime, nullable=False)
    is_contains = Column(SMALLINT(6), nullable=False)
    keywords = Column(VARCHAR(255), nullable=False)
    rule_desc = Column(VARCHAR(500))


class QiInfoDetailedpcdt(Base):
    __tablename__ = 'qi_info_detailedpcdt'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    rule_name = Column(VARCHAR(50))
    create_uid = Column(INTEGER(11), nullable=False)
    create_time = Column(DateTime, nullable=False)
    keywords = Column(VARCHAR(500), nullable=False)
    rule_desc = Column(VARCHAR(500))


class QiInfoDuration(Base):
    __tablename__ = 'qi_info_duration'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    rule_name = Column(VARCHAR(50), nullable=False)
    create_uid = Column(VARCHAR(255), nullable=False)
    create_time = Column(DateTime, nullable=False)
    duration = Column(INTEGER(11), nullable=False)
    score = Column(INTEGER(11), nullable=False)
    rule_desc = Column(VARCHAR(500))
    rule_type = Column(SMALLINT(6), nullable=False)


class QiInfoEmotion(Base):
    __tablename__ = 'qi_info_emotion'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    rule_name = Column(VARCHAR(50), nullable=False)
    create_uid = Column(VARCHAR(255), nullable=False)
    create_time = Column(DateTime, nullable=False)
    role = Column(SMALLINT(6), nullable=False)
    score = Column(INTEGER(11), nullable=False)
    rule_desc = Column(VARCHAR(500))


class QiInfoInterruption(Base):
    __tablename__ = 'qi_info_interruption'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    rule_name = Column(VARCHAR(50), nullable=False)
    create_uid = Column(VARCHAR(255), nullable=False)
    create_time = Column(DateTime, nullable=False)
    cross_time = Column(INTEGER(11), nullable=False)
    out_rule = Column(INTEGER(11))
    score = Column(INTEGER(11), nullable=False)
    rule_desc = Column(VARCHAR(500))


class QiInfoKeyword(Base):
    __tablename__ = 'qi_info_keywords'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    rule_name = Column(VARCHAR(50), nullable=False)
    create_uid = Column(INTEGER(11), nullable=False)
    create_time = Column(DateTime, nullable=False)
    keywords_rule = Column(VARCHAR(50), nullable=False)
    is_precondition = Column(SMALLINT(6), nullable=False)
    precondition_id = Column(INTEGER(11))
    check_range = Column(SMALLINT(6))
    left_boundary = Column(SMALLINT(6))
    right_boundary = Column(SMALLINT(6))
    score = Column(INTEGER(11), nullable=False)
    rule_desc = Column(VARCHAR(500))


class QiInfoMapRule(Base):
    __tablename__ = 'qi_info_map_rule'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    template_id = Column(INTEGER(11), nullable=False)
    template_name = Column(VARCHAR(50), nullable=False)
    rule_type = Column(INTEGER(11), nullable=False)
    rule_type_name = Column(VARCHAR(50), nullable=False)
    rule_id = Column(INTEGER(11), nullable=False)
    rule_name = Column(VARCHAR(50), nullable=False)
    rule_score = Column(INTEGER(11), nullable=False)
    show_desc = Column(String(255), nullable=False)
    warning_id = Column(INTEGER(11), server_default=text("'0'"))


class QiInfoPermission(Base):
    __tablename__ = 'qi_info_permission'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    pname = Column(VARCHAR(24), nullable=False)
    pcategory = Column(SMALLINT(6), nullable=False)
    ptype = Column(SMALLINT(6), nullable=False)
    presource = Column(VARCHAR(200))
    create_time = Column(INTEGER(11))


class QiInfoPrecondition(Base):
    __tablename__ = 'qi_info_precondition'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    rule_name = Column(VARCHAR(50))
    create_uid = Column(INTEGER(11), nullable=False)
    create_time = Column(DateTime, nullable=False)
    map_precondition_id = Column(VARCHAR(50), nullable=False)
    role = Column(SMALLINT(6), nullable=False)
    rule_desc = Column(VARCHAR(500))


class QiInfoProject(Base):
    __tablename__ = 'qi_info_project'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    proj_code = Column(VARCHAR(24), nullable=False, unique=True)
    pro_name = Column(VARCHAR(255), nullable=False)
    create_uid = Column(VARCHAR(255), nullable=False)
    create_time = Column(DateTime, nullable=False)
    original_project = Column(VARCHAR(128), nullable=False)
    lm_id = Column(String(255))
    qi_template = Column(INTEGER(11), nullable=False)
    proj_desc = Column(String(500))


class QiInfoRecording(Base):
    __tablename__ = 'qi_info_recording'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    recording_id = Column(String(64))
    call_id = Column(VARCHAR(64), unique=True)
    original_call_id = Column(VARCHAR(64))
    file_name = Column(VARCHAR(255))
    path = Column(VARCHAR(255))
    url = Column(String(255))
    track = Column(SMALLINT(6), index=True, comment='0：双声道；1-单声道')


class QiInfoRole(Base):
    __tablename__ = 'qi_info_role'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    rname = Column(VARCHAR(24), nullable=False)
    rcode = Column(VARCHAR(24), nullable=False)
    rdesc = Column(String(200))
    create_time = Column(INTEGER(11))
    rgroup = Column(SMALLINT(6), server_default=text("'-1'"))
    rlevel = Column(SMALLINT(6), server_default=text("'100'"))


class QiInfoRpMap(Base):
    __tablename__ = 'qi_info_rp_map'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    rid = Column(INTEGER(11), nullable=False)
    pid = Column(INTEGER(11), nullable=False)


class QiInfoRtype(Base):
    __tablename__ = 'qi_info_rtype'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    rule_name = Column(VARCHAR(50), nullable=False)
    rule_type = Column(SMALLINT(6), nullable=False)
    create_time = Column(DateTime, nullable=False)
    rule_desc = Column(VARCHAR(500))


class QiInfoSilence(Base):
    __tablename__ = 'qi_info_silence'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    rule_name = Column(VARCHAR(50), nullable=False)
    create_uid = Column(VARCHAR(255), nullable=False)
    create_time = Column(DateTime, nullable=False)
    quiet_time = Column(INTEGER(11), nullable=False)
    score = Column(INTEGER(11), nullable=False)
    rule_desc = Column(VARCHAR(500))


class QiInfoSpeed(Base):
    __tablename__ = 'qi_info_speed'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    rule_name = Column(VARCHAR(50), nullable=False)
    create_uid = Column(VARCHAR(255), nullable=False)
    create_time = Column(DateTime, nullable=False)
    rule_type = Column(SMALLINT(6), nullable=False)
    speed_counts = Column(INTEGER(11), nullable=False)
    out_rule = Column(INTEGER(11), nullable=False, server_default=text("'0'"))
    score = Column(INTEGER(11), nullable=False)
    rule_desc = Column(VARCHAR(500))


class QiInfoTabooWord(Base):
    __tablename__ = 'qi_info_taboo_words'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    rule_name = Column(VARCHAR(50), nullable=False)
    create_uid = Column(VARCHAR(255), nullable=False)
    create_time = Column(DateTime, nullable=False)
    score = Column(INTEGER(11), nullable=False)
    rule_desc = Column(VARCHAR(500))


class QiInfoTeam(Base):
    __tablename__ = 'qi_info_team'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    branch_id = Column(INTEGER(11), nullable=False)
    team_name = Column(VARCHAR(24), nullable=False)
    team_code = Column(VARCHAR(24))
    team_desc = Column(VARCHAR(200))
    create_time = Column(INTEGER(11))


class QiInfoTemplate(Base):
    __tablename__ = 'qi_info_template'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    template_name = Column(VARCHAR(50), nullable=False)
    create_uid = Column(VARCHAR(255), nullable=False)
    create_time = Column(DateTime, nullable=False)
    base_score = Column(INTEGER(11), nullable=False)
    template_desc = Column(VARCHAR(500))


class QiInfoTraffic(Base):
    __tablename__ = 'qi_info_traffic'

    insert_time = Column(INTEGER(11), server_default=text("'0'"))
    is_deleted = Column(SMALLINT(6), server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    call_id = Column(VARCHAR(64), unique=True)
    original_project = Column(VARCHAR(128), index=True)
    traffic_record_number = Column(VARCHAR(64))
    agent_id = Column(VARCHAR(64))
    extension_number = Column(VARCHAR(16))
    call_direction = Column(SMALLINT(6))
    calling_number = Column(VARCHAR(16))
    called_number = Column(VARCHAR(16))
    call_start_time = Column(DateTime)
    duration = Column(INTEGER(11))
    satisfaction = Column(INTEGER(11))
    file_status = Column(SMALLINT(6), index=True, server_default=text("'0'"))
    hit_status = Column(SMALLINT(6))
    review_status = Column(SMALLINT(6))
    appeal_status = Column(SMALLINT(6))


class QiInfoUser(Base):
    __tablename__ = 'qi_info_user'

    insert_time = Column(INTEGER(11), index=True)
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    account = Column(VARCHAR(24), nullable=False, unique=True)
    _password = Column('password', VARCHAR(100))
    nickname = Column(VARCHAR(24), nullable=False)
    telephone = Column(String(20))
    ac_type = Column(SMALLINT(6), nullable=False)
    ac_status = Column(SMALLINT(6), nullable=False)
    create_time = Column(INTEGER(11))
    bid = Column(INTEGER(11))
    rid = Column(INTEGER(11), nullable=False)
    agent_id = Column(VARCHAR(64))

    def keys(self):
        return ['id', 'account', 'nickname', 'telephone', 'ac_type', 'ac_status', 'create_time', 'rid']

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    @staticmethod
    def verify(account, password):
        user, role = db_v1.session.query(QiInfoUser, QiInfoRole).filter_by(account=account,
                                                                           rid=QiInfoRole.id).first_or_4010(
            msg='认证用户不存在',
            error_code=4011)
        if not user.check_password(password):
            raise AuthFailed(msg='认证密码不正确', error_code=4012)
        return {'uid': user.id, 'nickname': user.nickname, 'ac_type': user.ac_type, 'scope': role.rcode}

    def check_password(self, raw):
        if not self._password:
            return False
        return check_password_hash(self._password, raw)


class QiInfoWarning(Base):
    __tablename__ = 'qi_info_warning'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    create_uid = Column(VARCHAR(255), nullable=False)
    create_time = Column(DateTime, nullable=False)
    warning_name = Column(VARCHAR(64), nullable=False)
    hit_rules = Column(VARCHAR(1000))
    hit_rules_id = Column(VARCHAR(1000))
    message = Column(VARCHAR(255))
    ding_talk = Column(VARCHAR(1024))
    apps = Column(VARCHAR(1024))
    warning_desc = Column(VARCHAR(200))


class QiLabelParagraph(Base):
    __tablename__ = 'qi_label_paragraph'

    insert_time = Column(INTEGER(11))
    call_id = Column(String(50))
    is_deleted = Column(SMALLINT(6), server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    paragraph_id = Column(VARCHAR(50), index=True)
    task_id = Column(VARCHAR(50), index=True)
    order_number = Column(INTEGER(11))
    start_time = Column(INTEGER(8))
    end_time = Column(INTEGER(8))
    duration = Column(INTEGER(11))
    text = Column(String(1024))
    role = Column(SMALLINT(6), index=True)


class QiLabelSentence(Base):
    __tablename__ = 'qi_label_sentence'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), server_default=text("'0'"))
    call_id = Column(String(50))
    id = Column(INTEGER(11), primary_key=True)
    task_id = Column(VARCHAR(50), index=True)
    start_time = Column(INTEGER(8))
    end_time = Column(INTEGER(8))
    text = Column(String(1024))
    role = Column(SMALLINT(6))
    channel_id = Column(SMALLINT(6))
    paragraph_id = Column(String(50), index=True)


class QiPreprocessingRecording(Base):
    __tablename__ = 'qi_preprocessing_recording'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    file_name = Column(VARCHAR(255), nullable=False)
    path = Column(VARCHAR(255), nullable=False)
    url = Column(String(255), nullable=False)
    call_id = Column(VARCHAR(64), nullable=False, unique=True)
    task_id = Column(VARCHAR(50), nullable=False)


class QiResultsAppeal(Base):
    __tablename__ = 'qi_results_appeal'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    call_id = Column(VARCHAR(64), nullable=False)
    appeal_time = Column(DateTime, nullable=False)
    appeal_uid = Column(INTEGER(11), nullable=False)
    appeal_id = Column(INTEGER(11), nullable=False, index=True)
    appeal_reason = Column(VARCHAR(500), nullable=False)
    appeal_result = Column(INTEGER(11), nullable=False)
    conduct_time = Column(DateTime)
    conduct_uid = Column(INTEGER(11))
    pre_score = Column(INTEGER(11), nullable=False)
    current_scores = Column(INTEGER(11))


class QiResultsBusinessAnalysis(Base):
    __tablename__ = 'qi_results_business_analysis'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    call_id = Column(VARCHAR(64), nullable=False, unique=True)
    business_type = Column(String(50), nullable=False)
    call_reason_type = Column(String(50), nullable=False)


class QiResultsBusinessTrend(Base):
    __tablename__ = 'qi_results_business_trends'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    start_time = Column(Date, nullable=False)
    end_time = Column(Date, nullable=False)
    analysis_cycle_type = Column(SMALLINT(6), nullable=False)
    business_type = Column(String(50), nullable=False)
    call_count_percent = Column(INTEGER(11), nullable=False)
    average_score = Column(DECIMAL(5, 2), nullable=False)
    average_duration = Column(INTEGER(11), nullable=False)


class QiResultsDetail(Base):
    __tablename__ = 'qi_results_deatails'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    call_id = Column(VARCHAR(64), nullable=False)
    paragraph_id = Column(VARCHAR(50))
    detail_rule_id = Column(INTEGER(11), nullable=False, index=True)
    qc_time = Column(DateTime, nullable=False)
    hit_status = Column(SMALLINT(6), nullable=False, server_default=text("'1'"))
    type = Column(SMALLINT(6))
    review_status = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    hit_location = Column(String(128))


class QiResultsHotword(Base):
    __tablename__ = 'qi_results_hotwords'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    start_time = Column(Date, nullable=False)
    end_time = Column(Date, nullable=False)
    analysis_cycle_type = Column(SMALLINT(6), nullable=False)
    hot_word = Column(String(256), nullable=False)
    call_count = Column(INTEGER(11), nullable=False)
    word_frequency = Column(DECIMAL(10, 7), nullable=False)


class QiResultsRepeatCall(Base):
    __tablename__ = 'qi_results_repeat_calls'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    call_id = Column(VARCHAR(64), nullable=False, unique=True)
    call_start_time = Column(INTEGER(11))
    repeat_id = Column(INTEGER(11), nullable=False)
    type_code = Column(String(50))
    type_name = Column(String(50))
    agent_id = Column(String(64), nullable=False)
    nickname = Column(String(24), nullable=False)
    branch_name = Column(String(24), nullable=False)
    branch_code = Column(String(24), nullable=False)
    is_first_call = Column(SMALLINT(6), nullable=False)
    is_solved = Column(SMALLINT(6), nullable=False)


class QiResultsReview(Base):
    __tablename__ = 'qi_results_review'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    call_id = Column(VARCHAR(64), nullable=False)
    create_time = Column(DateTime, nullable=False)
    results_id = Column(String(64))
    pre_score = Column(INTEGER(11), nullable=False)
    current_score = Column(INTEGER(11))
    review_opinion = Column(String(500), nullable=False)
    review_uid = Column(INTEGER(11), nullable=False)


class QiScoreCall(Base):
    __tablename__ = 'qi_score_call'

    insert_time = Column(INTEGER(11))
    is_deleted = Column(SMALLINT(6), nullable=False, server_default=text("'0'"))
    id = Column(INTEGER(11), primary_key=True)
    call_id = Column(VARCHAR(64), nullable=False)
    qc_time = Column(DateTime, nullable=False, index=True)
    hit_rules = Column(String(1000))
    qc_score = Column(INTEGER(11), nullable=False, index=True)

    def keys(self):
        return ['insert_time','is_deleted','id','call_id','qc_time','hit_rules','qc_score',]