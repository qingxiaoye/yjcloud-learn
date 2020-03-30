# -*- coding: utf-8 -*-
import collections
import hashlib
import socket
import subprocess
import uuid

import errno
import os
import re
import scandir
import time
from datetime import datetime


def get_uuid_by_upload(name, timestamp_int):
    guid = uuid.uuid5(uuid.NAMESPACE_DNS, str(timestamp_int))
    return str(uuid.uuid5(guid, str(name))).replace('-', '')


def get_uuid():
    guid = uuid.uuid4()
    return str(guid).replace('-', '')


def current_timestamp_sec():
    return int(time.time())


def current_datetime_sec():
    return datetime.now().strftime("%Y-%m-%d %H-%M-%S")


def current_timestamp_ms():
    return int(round(time.time() * 1000))


def namedtuple_with_defaults(typename, field_names, default_values=()):
    """
    可以带初始值的namedtuple

    Wrapper for Python 2.6 to 3.6

    :param typename:
    :param field_names:
    :param default_values:
    :return:
    """
    T = collections.namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, collections.Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result

    return timed


def datetime2timestamp(datetime_v):
    if not isinstance(datetime_v, datetime):
        return None
    return int(time.mktime(datetime_v.timetuple()))


# def crc64(string):
#     import libscrc
#     crc64 = libscrc.iso('测试')
#     print crc64
#     crc64 = libscrc.ecma182('测试')
#     print crc64
#     pass


# def mysql_crc64(string):
#     """
#     用于优化便签的索引，mysql自身已有crc32函数，但如果表较大索引出现碰撞的可能变大，为了有一定的扩展性，
#     在mysql数据库扩展了crc64函数，define如下：
#     >>>
#         DELIMITER $$
#
#         -- DROP FUNCTION IF EXISTS crc64 $$
#         CREATE FUNCTION crc64(data LONGTEXT CHARSET utf8) RETURNS BIGINT UNSIGNED
#         DETERMINISTIC
#         NO SQL
#         SQL SECURITY INVOKER
#         COMMENT 'Return a 64 bit CRC of given input, as unsigned big integer'
#
#         BEGIN
#           RETURN CONV(LEFT(MD5(data), 16), 16, 10);
#         END $$
#
#         DELIMITER ;
#     >>>
#     本函数也跟mysql定义的函数相一致
#
#     :param string:
#     :return:
#     """
#     if isinstance(string, unicode):
#         string = string.encode('utf8')
#
#     m2 = hashlib.md5()
#     m2.update(string)
#     return int('0x%s' % m2.hexdigest()[0:16], 16)


# print mysql_crc64('测试')
# 15782521353076526960

def get_decorators(function):
    # print function
    # If we have no func_closure, it means we are not wrapping any other functions.
    f_c = getattr(function, 'func_closure', None)
    if not f_c:
        return [function]
    decorators = []
    # Otherwise, we want to collect all of the recursive results for every closure we have.
    for closure in function.func_closure:
        decorators.extend(get_decorators(closure.cell_contents))
    return [function] + decorators


def get_callable_cells(function):
    callables = []
    # Under some circumstances, I wound up with an object that has the name `view_func`:
    # this is the view function I need to access.
    if not hasattr(function, 'func_closure'):
        if hasattr(function, 'view_func'):
            return get_callable_cells(function.view_func)
    # If we have no more function we are wrapping
    if not function.func_closure:
        return [function]
    for closure in function.func_closure:
        contents = closure.cell_contents
        # Class-based views have a dispatch method
        if hasattr(contents, 'dispatch'):
            callables.extend(get_callable_cells(contents.dispatch.__func__))
            if hasattr(contents, 'get'):
                callables.extend(get_callable_cells(contents.get.__func__))
        callables.extend(get_callable_cells(contents))
    return [function] + callables


def magnitude_base(unit, base=1000):
    unit = str(unit).strip().lower()
    multipliers = {
        'kilo': base,
        'mega': base ** 2,
        'giga': base ** 3,
        'tera': base ** 4,
        'peta': base ** 5,
        'exa': base ** 6,
        'zeta': base ** 7,
        'yotta': base ** 8,
        'k': base,
        'm': base ** 2,
        'g': base ** 3,
        't': base ** 4,
        'p': base ** 5,
        'e': base ** 6,
        'z': base ** 7,
        'y': base ** 8,
    }

    return multipliers[unit]


def magnitude_converter(quantity_str, base=1000):
    multipliers = {
        'kilo': base,
        'mega': base ** 2,
        'giga': base ** 3,
        'tera': base ** 4,
        'peta': base ** 5,
        'exa': base ** 6,
        'zeta': base ** 7,
        'yotta': base ** 8,
        'k': base,
        'm': base ** 2,
        'g': base ** 3,
        't': base ** 4,
        'p': base ** 5,
        'e': base ** 6,
        'z': base ** 7,
        'y': base ** 8,
    }

    sre = re.compile(r"(\d+)\s?({})".format("|".join(x for x in multipliers.keys())), re.IGNORECASE)

    def subfunc(m):
        return str(int(m.group(1)) * multipliers[m.group(2).lower()])

    return sre.sub(subfunc, quantity_str)


def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def exist_remote_file(file_path):
    """
    得curl工具存在

    :param file_path:
    :return:
    """
    command = 'curl --output /dev/null --silent --head --fail {}'.format(file_path)

    import subprocess as sp
    return_code = sp.call(command, shell=True)
    return return_code == 0


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def get_size_walk(root_path):
    """ 较慢，如果不用du，则使用scandir库，可以提高遍历性能 """
    if not os.path.exists(root_path):
        return None

    if os.path.isfile(root_path):
        if os.path.islink(root_path):
            return 0
        else:
            return os.path.getsize(root_path)

    if os.path.isdir(root_path):
        total_size = 0

        for dirpath, dirnames, filenames in os.walk(root_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        return total_size

    return None


def get_size_du(root_path):
    """ 只能用于linux环境 """
    # TODO du跟另外两种方法的结果有点出入
    return subprocess.check_output(['d', '-sb', root_path]).split()[0].decode('utf-8')


def get_size_scandir(root_path):
    if not os.path.exists(root_path):
        return None

    if os.path.isfile(root_path):
        if os.path.islink(root_path):
            return 0
        else:
            return scandir.stat(root_path).st_size

    if os.path.isdir(root_path):
        total_size = 0

        for dirpath, dirnames, filenames in scandir.walk(root_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    # total_size += os.path.getsize(fp)
                    total_size += scandir.stat(fp).st_size
        return total_size
    return None


# def symlink_force(target, link_name):
#     try:
#         os.symlink(target, link_name)
#     except OSError, e:
#         if e.errno == errno.EEXIST:
#             os.remove(link_name)
#             os.symlink(target, link_name)
#         else:
#             raise e


def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


def safe_cast_int(num_str, default=0):
    try:
        res = int(num_str)
        return res
    except:
        return default


def safe_cast_float(num_str, default=0.):
    try:
        res = float(num_str)
        return res
    except:
        return default


"""
ms转化为s
"""


def msec2time(num_str, default='00:00:00'):
    try:
        second = int(num_str)
        m, s = divmod(second / 1000, 60)
        h, m = divmod(m, 60)
        time = "%02d:%02d:%02d" % (h, m, s)
        return time
    except:
        return default
