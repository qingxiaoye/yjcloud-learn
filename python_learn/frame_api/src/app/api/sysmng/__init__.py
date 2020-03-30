# -*- coding: utf-8 -*-

from flask import Blueprint

from app.api.sysmng import branch, user, token, role


def create_blueprint_sysmng():
    bp_sysmgr = Blueprint('sysmng', __name__)
    branch.api.register(bp_sysmgr)
    user.api.register(bp_sysmgr)
    token.api.register(bp_sysmgr)
    role.api.register(bp_sysmgr)
    return bp_sysmgr
