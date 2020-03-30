# -*- coding: utf-8 -*-
import logging

from flask import g, request
from sqlalchemy import desc, func, distinct, or_, and_

from app.libs.builtin_extend import namedtuple_with_defaults, current_timestamp_sec, datetime2timestamp
from app.libs.error_code import Success, DeleteSuccess, ResultSuccess, CreateSuccess, EditSuccess, \
    PageResultSuccess, ParameterException
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v1
from app.validators.base import PageForm

from app.models.qi_qia_models import QiInfoUser, QiInfoBranch, QiInfoRole
from app.validators.forms_v1 import UserAddForm, UserSearchForm, UserEditForm, PasswordEditForm, IDForm

api = Redprint('user')
logger = logging.getLogger(__name__)


@api.route('', methods=['POST'])
@auth.login_required
def user_add():
    form = UserAddForm().validate_for_api()
    Role = QiInfoRole.query.filter_by(id=form.rid.data).first_or_404()
    role_code = Role.rcode

    if role_code == 'diremanager' and form.bid.data:
        raise ParameterException(msg='主管人员请不要填写部门')
    if (role_code != 'diremanager' and role_code != 'systemadmin') and form.bid.data is None:
        raise ParameterException(msg='请选择部门')
    if role_code == 'agentoperator' and form.agent_id.data is None:
        raise ParameterException(msg='坐席人员请填写工号')
    if role_code != 'agentoperator' and form.agent_id.data:
        raise ParameterException(msg='非坐席人员，请不要填写工号')
    user = QiInfoUser()

    with db_v1.auto_commit():
        form.populate_obj(user)
        user.insert_time = current_timestamp_sec()
        user.ac_type = 100
        user.ac_status = 100
        user.password = form.password.data
        user.is_deleted = 0
        user.create_time = current_timestamp_sec()
        db_v1.session.add(user)
    vm_keys_user = ('id', 'create_time')
    vm = {}
    for v_key in vm_keys_user:
        vm[v_key] = getattr(user, v_key, None)
    return CreateSuccess(msg='用户新增成功', data=vm)


@api.route('/del/<int:uid>', methods=['GET'])
@auth.login_required
def user_super_del(uid):
    with db_v1.auto_commit():
        user = QiInfoUser.query.filter_by(id=uid).first_or_404()
        user.delete()
        db_v1.session.add(user)
    return DeleteSuccess(msg='用户删除成功')


@api.route('/list', methods=['POST'])
@auth.login_required
def user_super_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    form = UserSearchForm().validate_for_api()
    q = db_v1.session.query(
        QiInfoUser,
        QiInfoRole.rname.label('rname'),
        QiInfoBranch.branch_name.label('branch_name'),
        QiInfoBranch.is_deleted.label('branch_is_deleted')

    ).filter(QiInfoUser.rid == QiInfoRole.id,
             QiInfoUser.is_deleted == 0,
             QiInfoRole.is_deleted == 0,
             ).join(QiInfoBranch,
                    and_(QiInfoUser.bid == QiInfoBranch.id,
                         QiInfoBranch.is_deleted == 0, ),
                    isouter=True
                    ).order_by(desc(QiInfoUser.create_time), QiInfoUser.id)
    if form.account.data:
        q = q.filter(QiInfoUser.account.like('%' + form.account.data + "%"))
    if form.agent_id.data:
        q = q.filter(QiInfoUser.agent_id.like('%' + form.agent_id.data + "%"))
    if form.rid.data:
        q = q.filter(QiInfoRole.id == form.rid.data)
    if form.bid.data:
        q = q.filter(QiInfoBranch.id == form.bid.data)
    rvs = pager(q, page=cur_page, per_page=per_page)
    vm_keys_user = ['id', 'account', 'nickname', 'agent_id', 'rid']
    vms = []
    for rv in rvs.items:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        vm = {}
        for v_key in vm_keys_user:
            vm[v_key] = getattr(rv_dict['QiInfoUser'], v_key, None)
        vm['branch_name'] = rv_dict['branch_name']
        vm['rname'] = rv_dict['rname']

        vms.append(vm)
    return PageResultSuccess(msg='用户列表', data=vms, page=rvs.page_view())


@api.route('/edit', methods=['POST'])
@auth.login_required
def user_super_edit():
    uid = IDForm().validate_for_api().id.data
    form = UserEditForm().validate_for_api()
    account = QiInfoUser.query.filter_by(id=uid).first()

    Role = QiInfoRole.query.filter_by(id=form.rid.data).first_or_404()
    role_code = Role.rcode
    if form.account.data and form.account.data != account.account:
        raise ParameterException(msg='请不要修改用户账户')
    if QiInfoUser.query.filter(
            QiInfoUser.nickname == form.nickname.data,
            QiInfoUser.id != uid,
            QiInfoUser.is_deleted == 0).first():
        raise ParameterException(msg='该用户昵称已存在，请重新命名 ')
    if form.agent_id.data and role_code == 'agentoperator':
        if QiInfoUser.query.filter(
                QiInfoUser.agent_id == form.agent_id.data,
                QiInfoUser.id != uid,
                QiInfoUser.is_deleted == 0).first():
            raise ParameterException(msg='该坐席已存在，请重新命名 ')
    if role_code == 'diremanager' and form.bid.data:
        raise ParameterException(msg='主管人员请不要填写部门')
    if role_code != 'diremanager' and form.bid.data is None:
        raise ParameterException(msg='请选择部门')
    if role_code == 'agentoperator' and (form.agent_id.data is None or len(form.agent_id.data) == 0):
        raise ParameterException(msg='坐席人员请填写工号')
    if role_code != 'agentoperator' and form.agent_id.data:
        raise ParameterException(msg='非坐席人员，请不要填写工号')
    with db_v1.auto_commit():
        user = QiInfoUser.query.filter_by(id=uid).first_or_404()
        if form.nickname.data:
            user.nickname = form.nickname.data
        if form.password.data:
            user.password = form.password.data
        if form.telephone.data:
            user.telephone = form.telephone.data
        if form.rid.data:
            user.rid = form.rid.data
        if form.agent_id.data:
            user.agent_id = form.agent_id.data
        if form.bid.data:
            user.rid = form.bid.data
    return EditSuccess(msg='用户修改成功')


@api.route('/reset-pwd/<int:uid>', methods=['GET'])
@auth.login_required
def user_super_reset_pwd(uid):
    with db_v1.auto_commit():
        user = QiInfoUser.query.filter_by(id == uid).first_or_404()
        user.password = '123456'
    return Success(msg='密码重设成功')


@api.route('/change-pwd', methods=['POST'])
@auth.login_required
def user_change_pwd():
    uid = IDForm().validate_for_api().id.data
    form = PasswordEditForm().validate_for_api()
    account = QiInfoUser.query.filter_by(id=uid).first_or_404()
    identity = QiInfoUser.verify(account['account'], form.old_password.data)
    if form.new_password.data != form.confirm_password.data:
        raise ParameterException(msg='新旧密码不一样，请重新确认')
    if identity:
        with db_v1.auto_commit():
            user = QiInfoUser.query.filter_by(id=uid).first_or_404()
            user.password = form.new_password.data

    return Success(msg='修改密码成功')


@api.route('', methods=['GET'])
@auth.login_required
def user_get():
    cur_user, cur_role, cur_branch = _get_user_full_info()

    vm = {}
    vm['create_time'] = cur_user.create_time
    vm['id'] = cur_user.id
    vm['nickname'] = cur_user.nickname
    vm['rid'] = cur_role.id
    vm['rname'] = cur_role.rname
    vm['rcode'] = cur_role.rcode
    vm['bid'] = cur_branch.id
    vm['branch_name'] = cur_branch.branch_name
    vm['branch_code'] = cur_branch.branch_code

    return ResultSuccess(msg='个人用户信息', data=vm)  # 都有id，注意merge顺序


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
