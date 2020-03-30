# -*- coding: utf-8 -*-
import os

import werkzeug
from werkzeug.exceptions import HTTPException

from app import create_app
from app.libs.error import APIException
from app.libs.error_code import ServerError, PermissionForbidden
from app.libs.qpaginate.paginator import PageNotAnInteger, EmptyPage
# import sys
# sys.path.append('D:/pycharm_project/AI_Speech_QIA/src/app/libs/emotion_libs')

app = create_app(os.getenv('FLASK_CONFIG') or 'production', logging_cfg='./logging.yaml')


@app.errorhandler(Exception)
def framework_error(e):
    if isinstance(e, APIException):
        return e
    if isinstance(e, PageNotAnInteger):
        return APIException('分页参数错误，参数不是Integer类型', 400, 4001)
    if isinstance(e, EmptyPage):
        return APIException('分页参数错误，当前页没有数据', 400, 4001)
    if isinstance(e, HTTPException):
        code = e.code
        msg = '未定义Http异常: ' + str(e.description)
        error_code = 5008
        return APIException(msg, code, error_code)
    else:
        # TODO
        # Log处理
        if not app.config['DEBUG']:
            return ServerError()
        else:
            raise e


if __name__ == '__main__':

    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'), debug=app.config.get('DEBUG'))
