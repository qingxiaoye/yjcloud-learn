# -*- coding: utf-8 -*-
import yaml
from flask_cors import CORS
from flask_socketio import SocketIO

from .app import Flask
from .configure import config
from .libs import path_utils


import logging
import logging.config
import os
import codecs


def register_blueprints(app):
    from app.api.v1 import create_blueprint_v1
    app.register_blueprint(create_blueprint_v1(), url_prefix='/v1')
    from app.api.sysmng import create_blueprint_sysmng
    # app.register_blueprint(create_blueprint_sysmng())
    app.register_blueprint(create_blueprint_sysmng(), url_prefix='/v1')


def register_plugin(app):
    from .models.base import db_v1
    db_v1.init_app(app)
    # with app.app_context():
    #     db.create_all()

    # 跨域处理
    CORS(app, supports_credentials=True)
    socketio.init_app(app=app, async_mode=None)

    from .models.base import asynchronous_executor, transfor_executor
    asynchronous_executor.init_app(app)
    transfor_executor.init_app(app)


def create_app(config_name, logging_cfg=None):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    if logging_cfg:
        if logging_cfg[0] != '/':
            logging_cfg = os.path.abspath(os.path.join(path_utils.get_cfg_dir(), logging_cfg))
    if not logging_cfg or not os.path.exists(logging_cfg):
        # raise IOError('日志配置文件不存在：{}'.format(logging_cfg_arg))
        logging_cfg = app.config['LOGGING_CONFIG_PATH']
        logging_cfg = os.path.abspath(os.path.join(app.root_path, '{}'.format(logging_cfg)))
    with codecs.open(logging_cfg, 'r', encoding='utf-8') as f:
        logging_cfg_dict = yaml.safe_load(f.read())
        handlers = logging_cfg_dict.get('handlers')
        if handlers:
            for handle_k, handler in handlers.items():
                if not handler.get('filename'):
                    continue
                log_filename = os.path.basename(handler['filename'])
                log_dir = os.path.dirname(handler['filename'])
                if log_dir[0] != '/':
                    log_dir = os.path.join(path_utils.get_project_dir(), log_dir)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                logging_cfg_dict['handlers'][handle_k]['filename'] = os.path.join(log_dir, log_filename)
        # print logging_cfg_dict
    logging.config.dictConfig(logging_cfg_dict)

    register_blueprints(app)
    register_plugin(app)

    return app


socketio = SocketIO()
