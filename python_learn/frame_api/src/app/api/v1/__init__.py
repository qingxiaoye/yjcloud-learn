# -*- coding: utf-8 -*-

from flask import Blueprint

from app.api.v1 import learn,know


def create_blueprint_v1():
    bp_v1 = Blueprint('v1', __name__)

    learn.api.register(bp_v1)
    know.api.register(bp_v1)
    return bp_v1
