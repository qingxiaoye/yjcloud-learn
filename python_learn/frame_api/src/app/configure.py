# -*- coding:utf-8 -*-
import os


class Config:
    def __init__(self):
        pass

    DEBUG = True
    TESTING = False
    ENV = 'production'

    HOST = '127.0.0.1'
    PORT = 7710

    TOKEN_EXPIRATION = 30 * 24 * 3600
    ADMIN_TOKEN_EXPIRATION = 1800

    DEFAULT_LISTNUM_PER_PAGE = 20
    TAGGING_PER_PAGE = 1

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'damnitintheworld, evilofthisproject'
    SQLALCHEMY_ECHO = False

    SQLALCHEMY_DATABASE_URI = 'mysql+cymysql://root:yjyjs123@192.168.106.170:3306/yj_speech_qia?charset=utf8'
    # SQLALCHEMY_BINDS = {
    #     'al_web': 'mysql+cymysql://root:yjyjs123@192.168.106.170:3306/yj_autolearning_web?charset=utf8'
    # }

    # UTTERANCE_FILE_SERVER = 'http://115.236.44.181:5000'
    UTTERANCE_FILE_SERVER = 'http://192.168.106.170:5000'

    LOGGING_CONFIG_PATH = './app/logging.yaml'
    PLUGINS_CONFIG_PATH = './plugins.yaml'
    LOGGING_PATH = './logs'

    BUSI_QIROJECT_CODE_PREFIX = 'QPJ'
    BUSI_QIPROJECT_CODE_PLACEHOLDER_NUM = 4
    BUSI_BRANCH_CODE_PREFIX = 'QBC'
    BUSI_BRANCH_CODE_PLACEHOLDER_NUM = 4

    BUSI_BRANCH_SUBREL_MAXDEEP = 10

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True

    HOST = '127.0.0.1'
    PORT = 5000
    # HOST = '192.168.106.170'
    # PORT = '7720'

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'mysql+cymysql://root:yjyjs123@192.168.106.10:3306/yj_speech_qia?charset=utf8'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'mysql+cymysql://root:yjyjs123@192.168.106.170:3306/yj_speech_qia?charset=utf8'


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': Config
}
