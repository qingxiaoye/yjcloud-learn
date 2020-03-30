# -*- coding: utf-8 -*-
import copy
import logging
from collections import defaultdict, deque

from flask import g, current_app, request
from sqlalchemy import desc, func, distinct, or_

from app.libs.builtin_extend import namedtuple_with_defaults, current_timestamp_sec, datetime2timestamp
from app.libs.error_code import Success, DeleteSuccess, ResultSuccess, CreateSuccess, EditSuccess, \
    PageResultSuccess, ParameterException
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v1
from app.validators.base import PageForm

from app.models.qi_qia_models import QiInfoUser, QiInfoBranch, QiInfoRole
from app.validators.forms_v1 import BranchAddForm, BranchSearchForm, BranchEditForm, IDForm

api = Redprint('branch')
logger = logging.getLogger(__name__)


@api.route('', methods=['POST'])
@auth.login_required
def branch_add():
    form = BranchAddForm().validate_for_api()
    branch_name = form.branch_name.data
    superior_id = form.superior_id.data
    if QiInfoBranch.query.filter_by(branch_name=branch_name, superior_id=superior_id).first():
        superior_name = QiInfoBranch.query.filter_by(id=superior_id).first().branch_name
        raise ParameterException(msg=superior_name + '已有' + branch_name + '，如要新建，请重新命名 ')
    branch = QiInfoBranch()
    placeholder_num = current_app.config['BUSI_BRANCH_CODE_PLACEHOLDER_NUM']
    branch_code_list = QiInfoBranch.query.with_entities(QiInfoBranch.branch_code).filter_by(with_deleted=True).all()
    branch_cnt = max([int(proj_code[-placeholder_num:]) for proj_code, in branch_code_list]) if len(
        branch_code_list) > 0 else 0
    branch_code = '{}{}'.format(current_app.config['BUSI_BRANCH_CODE_PREFIX'],
                                str(branch_cnt + 1).zfill(placeholder_num))
    with db_v1.auto_commit():
        form.populate_obj(branch)
        branch.insert_time = current_timestamp_sec()
        branch.is_deleted = 0
        branch.branch_code = branch_code
        branch.superior_id = form.superior_id.data
        branch.create_time = current_timestamp_sec()
        db_v1.session.add(branch)
    vm_keys_branch = (
        'id', 'create_time')
    vm = {}
    for v_key in vm_keys_branch:
        vm[v_key] = getattr(branch, v_key, None)
    vm['create_time'] = vm['create_time']
    return CreateSuccess(msg='部门新增成功', data=vm)


@api.route('/del/<int:bid>', methods=['GET'])
@auth.login_required
def branch_del(bid):
    user = QiInfoUser.query.filter_by(bid=bid).all()
    if user:
        raise ParameterException(msg='该部门中有用户，无法删除部门，请修改该部门中的用户所属部门后，再进行删除')

    with db_v1.auto_commit():
        # branch = QiInfoBranch.query.filter_by(id==bid).first_or_404()
        branch = QiInfoBranch.query.filter_by(id=bid).first_or_404()
        branch.delete()
        sups = QiInfoBranch.query.filter_by(superior_id=bid).all()
        for sup in sups:
            sup.delete()
    return DeleteSuccess(msg='部门删除成功')


@api.route('/list', methods=['POST'])
@auth.login_required
def branch_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())
    form = BranchSearchForm().validate_for_api()
    q = db_v1.session.query(QiInfoBranch).filter(QiInfoBranch.is_deleted == 0).order_by(
        desc(QiInfoBranch.create_time), QiInfoBranch.id)

    if form.branch_name.data:
        q = q.filter(QiInfoBranch.branch_name.like('%' + form.branch_name.data + "%"))
    rvs = pager(q, page=cur_page, per_page=per_page)
    vms = []
    for rv in rvs.items:
        vm = {}
        vm['id'] = rv.id
        vm['branch_name'] = rv.branch_name
        vm['branch_code'] = rv.branch_code
        vm['create_time'] = rv.create_time

        vms.append(vm)

    return PageResultSuccess(msg='部门列表', data=vms, page=rvs.page_view())


@api.route('/edit', methods=['POST'])
@auth.login_required
def branch_edit():
    bid = IDForm().validate_for_api().id.data
    form = BranchEditForm().validate_for_api()

    branch_name = form.branch_name.data
    superior_id = form.superior_id.data
    if QiInfoBranch.query.filter(QiInfoBranch.branch_name == branch_name,
                                 QiInfoBranch.superior_id == superior_id,
                                 QiInfoBranch.id != bid,
                                 ).first():
        superior_name = QiInfoBranch.query.filter_by(id=superior_id).first().branch_name
        raise ParameterException(msg=superior_name + '已有' + branch_name + '，如要修改，请重新命名 ')

    with db_v1.auto_commit():
        branch = QiInfoBranch.query.filter_by(id=bid).first_or_404()
        if form.branch_name.data:
            branch.branch_name = form.branch_name.data
        if form.superior_id.data:
            branch.superior_id = form.superior_id.data
    return EditSuccess(msg='部门修改成功')


@api.route('/get-sub/<bid>', methods=['GET'])
def branch_get_sub(bid):
    branch_all = QiInfoBranch.query.filter_by(QiInfoBranch.is_deleted == 0).all()
    branch_dict = {branch.id: branch for branch in branch_all}

    branch_id_pairs = [(branch.id, branch.superior_id) for branch in branch_all]
    branch_all_sub = _branch_sub_rel_reformer(branch_id_pairs, max_deep=10)

    vms = []
    for bid in branch_all_sub.get(int(bid), []):
        if branch_dict.get(bid):
            vms.append(dict(branch_dict[bid]))

    return ResultSuccess(msg='部门层级字典', data=vms)


def _branch_sub_rel_reformer(branch_id_pairs, max_deep=10):
    branch_sub_rel = defaultdict(set)
    for b_id, b_supid in branch_id_pairs:
        branch_sub_rel[b_supid].add(b_id)

    branch_all_sub_rel = defaultdict(set)
    for k, sub_ids in branch_sub_rel.items():
        all_sub_ids = set()
        id_stack = deque([k, ])
        deep_counter = 0
        deep_limit = max_deep - 1
        while len(id_stack) > 0:
            if deep_counter > deep_limit:
                break

            s_id = id_stack.popleft()
            for sub_rel_id in branch_sub_rel.get(s_id, set()):
                all_sub_ids.add(sub_rel_id)
                id_stack.append(sub_rel_id)

            deep_counter += 1
        branch_all_sub_rel[k] = all_sub_ids

    return {k: list(v) for k, v in branch_all_sub_rel.items()}


@api.route('/cascade-branch', methods=['GET'])
def branch_cascade():
    rvs = QiInfoBranch.query.filter_by(QiInfoBranch.is_deleted == 0).all()

    p_cascade_map = {}
    for rv in rvs:
        parent_id = rv['superior_id']
        p_cascade_item = p_cascade_map.get(parent_id, [])
        child = dict(
            id=rv['id'],
            name=rv['branch_name'],
            # level=rv['level']
        )
        p_cascade_item.append(child)
        p_cascade_map[parent_id] = p_cascade_item
    res = _branch_iter(p_cascade_map, 0)

    return ResultSuccess(msg='部门层级字典', data=res)


def _branch_iter(p_cascade_map, p_key):
    branch_list = p_cascade_map.pop(p_key, [])
    for branch in branch_list:
        id = branch['id']
        child_list = _branch_iter(p_cascade_map, id)
        if len(child_list) > 0:
            branch['childs'] = child_list
    return branch_list
