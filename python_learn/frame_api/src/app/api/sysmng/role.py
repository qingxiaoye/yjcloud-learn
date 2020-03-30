# -*- coding: utf-8 -*-
import logging

import time

from flask import jsonify, request, g

from app.libs.enums import ChoicesExItemEnum
from app.libs.builtin_extend import namedtuple_with_defaults
# from app.libs.enums import ChoicesExItemEnum, ChoicesExTypeEnum
from app.libs.error_code import Success, DeleteSuccess, ResultSuccess, ServerError, PageResultSuccess
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v1
from app.models.qi_qia_models import QiInfoRole, QiInfoUser
from app.validators.base import PageForm

api = Redprint('role')
logger = logging.getLogger(__name__)


# @api.route('/<int:rid>', methods=['GET'])
# @auth.login_required
# def role_get(rid):
#     role = Role.query.filter_by(id=rid).first_or_404()
#     return ResultSuccess(data=role)


# @api.route('', methods=['GET'])
# @auth.login_required
# def role_get_all():
#     role_objs = Role.query.filter_by().all()
#     return ResultSuccess(msg='角色全部信息', data=role_objs)


# RoleViewListItemFields = ('id', 'rname', 'rdesc')
# RoleViewListItem = namedtuple_with_defaults('RoleViewListItem', RoleViewListItemFields,
#                                             default_values=(None,) * len(RoleViewListItemFields))



# @api.route('/<rcode>', methods=['GET'])
# @auth.login_required
# def role_get_by_rcode(rcode):
#     role = QiInfoRole.query.filter_by(rcode=rcode).first_or_404()
#     return jsonify(role)
#
#
# @api.route('/set-perms', methods=['POST'])
# def role_set_permission():
#     form = RolePermissionMapForm().validate_for_api()
#
#     # drop掉非法id
#     pid_list = Permission.query.with_entities(Permission.id).filter(Permission.id.in_(form.pid_list.data)).all()
#
#     current_t = int(time.time())  # 不是用add方法，初始化时current_time并没有调用父类Base的__init__方法
#     r_p_map_list = []
#     for pid, in pid_list:
#         r_p_map = RolePermissionMap()
#         r_p_map.rid = form.rid.data
#         r_p_map.pid = pid
#         r_p_map.create_time = current_t
#         r_p_map_list.append(r_p_map)
#     with db_v2.auto_commit():
#         # RolePermissionMap.query.filter_by(rid=form.rid.data, with_deleted=True).delete()    # 批量删除
#         RolePermissionMap.query.filter_by(rid=form.rid.data).update({'is_deleted': 1})      # 批量伪删除
#         db_v2.session.bulk_save_objects(r_p_map_list)  # 批量添加
#
#     # RolePermissionMap.query.filter_by(rid=form.rid.data)
#     return Success(msg='角色关联权限成功')


@api.route('/choices-name', methods=['GET'])
@auth.login_required
def role_choices_name():
    # uid = g.user.uid
    q = db_v1.session.query(QiInfoRole.id, QiInfoRole.rname).filter(
        QiInfoRole.is_deleted == 0
    )
    rvs = q.all()
    vms = []
    for id, rname in rvs:
        vm = dict(
            k=id,
            v=rname
        )
        vms.append(vm)
    return ResultSuccess(msg='角色名称字典', data=vms)


# @api.route('/choices-code', methods=['GET'])
# @auth.login_required
# def role_choices_code():
#     role_objs = Role.query.filter_by().all()
#     vms = []
#
#     for role in role_objs:
#         vms.append({'k': role.id, 'v': role.rcode})
#
#     return ResultSuccess(msg='角色编码字典', data=vms)


@api.route('/choices', methods=['GET'])
@auth.login_required
def role_choices():
    uid = g.user.uid
    q = QiInfoRole.query.filter_by().order_by(QiInfoRole.id)
    # 权限约束
    cur_role = QiInfoRole.query.filter(QiInfoRole.id == QiInfoUser.rid,
                                       QiInfoUser.id == uid,
                                       QiInfoUser.is_deleted == 0).first()
    if cur_role.rgroup == ChoicesExItemEnum.NEITHER.value:
        return ResultSuccess(msg='角色信息字典', data=[])
    if not cur_role.rgroup == 0:
        q = q.filter(QiInfoRole.rgroup == cur_role.rgroup, QiInfoRole.rlevel >= cur_role.rlevel)

    role_objs = q.all()
    vms = []
    for role in role_objs:
        vms.append({'k': role.id, 'v': {'rcode': role.rcode, 'rname': role.rname}})
    # 下拉框扩展
    # choice_type = int(request.args.get('choice_type', 0) if not request.args.get('choice_type') == 'undefined' else 0)
    # if choice_type == ChoicesExTypeEnum.TYPE_NEITHER.value:
    #     vms.append(dict(k=ChoicesExItemEnum.NEITHER.value, v={'rcode': '-', 'rname': '无'}))
    # elif choice_type == ChoicesExTypeEnum.TYPE_ALL.value:
    #     vms.insert(0, dict(k=ChoicesExItemEnum.ALL.value, v={'rcode': '-', 'rname': '全部角色'}))
    # elif choice_type == ChoicesExTypeEnum.TYPE_NEITHER_ALL.value:
    #
    #     vms.insert(0, dict(k=ChoicesExItemEnum.ALL.value, v={'rcode': '-', 'rname': '全部角色'}))
    #     vms.append(dict(k=ChoicesExItemEnum.NEITHER.value, v={'rcode': '-', 'rname': '无'}))
    return ResultSuccess(msg='角色信息字典', data=vms)
