# -*- coding: utf-8 -*-
import time
from flask_executor import Executor
from sqlalchemy.ext.declarative import declared_attr
from app.libs.error_code import NotFound, AuthFailed
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery
from sqlalchemy import inspect, Column, Integer, SmallInteger, orm
from contextlib import contextmanager


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


class Query(BaseQuery):
    def filter_by(self, with_deleted=False, **kwargs):
        if not with_deleted:
            if 'is_deleted' not in kwargs.keys():
                kwargs['is_deleted'] = 0
        return super(Query, self).filter_by(**kwargs)

    def get_or_404(self, ident):
        rv = self.get(ident)
        if not rv:
            raise NotFound()
        return rv

    def first_or_404(self):
        rv = self.first()
        if not rv:
            raise NotFound()
        return rv

    def first_or_4010(self, msg='权限认证失败', error_code=4010):
        rv = self.first()
        if not rv:
            raise AuthFailed(msg=msg, error_code=error_code)
        return rv


db_v1 = SQLAlchemy(query_class=Query)


class WebBase(db_v1.Model):
    __bind_key__ = 'al_web'
    __abstract__ = True
    _the_prefix = 'al_'

    create_time = Column(Integer)
    is_deleted = Column(SmallInteger, default=0)

    @declared_attr
    def __tablename__(cls):
        return cls._the_prefix + cls.__incomplete_tablename__

    def __init__(self):
        self.create_time = int(time.time())

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def create_datetime(self):
        if self.create_time:
            return datetime.fromtimestamp(self.create_time)
        else:
            return None

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    def delete(self):
        self.is_deleted = 1

    def keys(self):
        return self.fields

    def hide(self, *keys):
        for key in keys:
            self.fields.remove(key)
        return self

    def append(self, *keys):
        for key in keys:
            self.fields.append(key)
        return self


class Base(db_v1.Model):
    __abstract__ = True
    # create_time = Column(Integer)
    is_deleted = Column(SmallInteger, default=0)

    def __init__(self):
        self.create_time = int(time.time())

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def create_datetime(self):
        if self.create_time:
            return datetime.fromtimestamp(self.create_time)
        else:
            return None

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    def delete(self):
        self.is_deleted = 1

    def keys(self):
        return self.fields

    def hide(self, *keys):
        for key in keys:
            self.fields.remove(key)
        return self

    def append(self, *keys):
        for key in keys:
            self.fields.append(key)
        return self


class MixinJSONSerializer:
    @orm.reconstructor
    def init_on_load(self):
        self._fields = []
        # self._include = []
        self._exclude = []

        self._set_fields()
        self.__prune_fields()

    def _set_fields(self):
        pass

    def __prune_fields(self):
        columns = inspect(self.__class__).columns
        if not self._fields:
            all_columns = set(columns.keys())
            self._fields = list(all_columns - set(self._exclude))

    def hide(self, *args):
        for key in args:
            self._fields.remove(key)
        return self

    def keys(self):
        return self._fields

    def __getitem__(self, key):
        return getattr(self, key)


asynchronous_executor = Executor(name='asynchronous')
transfor_executor = Executor(name='transfer')
