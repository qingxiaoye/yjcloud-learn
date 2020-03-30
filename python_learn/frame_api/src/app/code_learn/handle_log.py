# !/usr/bin/python
# -*- coding:utf-8 -*-
import subprocess

import time

import codecs
import os

import comm
import db_models
import handle_client_log
import parse_log as parser
import Logging
import config
import save_to_mysql
from remote_mgr import RemoteControlMgr
from sqlalchemy_mgr import SqlalchemyMgr
from rsync_data import rsync_data
from datetime import datetime
from libs.cfg_utils import get_config_dict


def handle_logs(parser_start_time, parser_end_time):
    Logging.logger.debug("Handle log start.")
    try:
        config_items = config.ConfigInfo.get_instance().get_config_items()
        if config_items['SrcAsrLogDir'] == "":
            return
        engine_version = config_items['EngineVersion']
        if engine_version.split('.')[0] == '1':
            handle_logs_v1_x(parser_start_time, parser_end_time)
        elif engine_version.split('.')[0] == '2':
            handle_logs_v2_x(parser_start_time, parser_end_time)
        else:
            Logging.logger.error("EngineVersion in config.ini is unset.")
    except Exception as exp:
        Logging.logger.error("handle_logs: error message: %s", exp)
    finally:
        Logging.logger.debug("Handle log finished.")


# 处理1.x引擎，1.x引擎已知的包括1.12.6
def handle_logs_v1_x(parser_start_time, parser_end_time):
    try:
        config_items = config.ConfigInfo.get_instance().get_config_items()

        rsync_trace_logs = rsync_data(
            config_items['SrcAsrLogDir'],
            os.path.join(config_items['DstLogDir'], "trace-log"),
            comm.LogType.ASR_TRACE.name,
            parser_start_time,
            parser_end_time,
            prefix='speech-alisr-trace.log', isMd5=True)
        if rsync_trace_logs is None:
            Logging.logger.error("handle_logs_v1_x, rsync speech-alisr-trace logs is None.")
        else:
            Logging.logger.debug("handle_logs_v1_x, rsync speech-alisr-trace logs count is %s.", len(rsync_trace_logs))
            for trace_log in rsync_trace_logs:
                handle_trace_log_v1_x(trace_log)

        if config_items['ClientLogSwitch'] == 'on':
            rsync_diting_logs = rsync_data(
                config_items['SrcDitingLogDir'],
                os.path.join(config_items['DstLogDir'], "diting_log"),
                comm.LogType.DITING_LOG.name,
                prefix='diting.log',
                isMd5=True
            )
            if rsync_diting_logs is None:
                Logging.logger.error("handle_logs_v1_x, rsync diting logs is None.")
            else:
                Logging.logger.debug("handle_logs_v1_x, rsync diting logs count is %s.", len(rsync_diting_logs))
                for diting_log in rsync_diting_logs:
                    handle_diting_log_v1_x(diting_log)

            handle_client_log.handle_client_logs()
    except Exception as exp:
        Logging.logger.error("handle_logs_v1_x: error message: %s", exp)


def handle_trace_log_v1_x(trace_log):
    try:
        Logging.logger.debug("handle_trace_log_v1_x, Parsing speech-alisr-trace-log: %s", trace_log)
        info_dict_list = parser.parse_asr_trace(trace_log)
        if info_dict_list is None:
            Logging.logger.error("handle_trace_log_v1_x, The info from file: %s is None.", trace_log)
        return save_to_mysql.save_dic_to_mysql(info_dict_list, db_models.UtteranceAccess)
    except Exception as exp:
        Logging.logger.error("handle_trace_log_v1_x, error message: %s", exp)
        return False


def handle_diting_log_v1_x(diting_log):
    try:
        Logging.logger.debug("handle_diting_log_v1_x, Parsing diting-log: %s", diting_log)
        start_time = time.time()
        single_bulk = 500000  # 每次读取的行数
        finish_flag = False  # 读取结束标记
        total_line_cnt = 0  # 总行数
        blank_line_num = 0  # 空行数
        start_num = 0
        lines = []
        with codecs.open(diting_log, 'rb', encoding='utf-8') as f:
            while not finish_flag:
                for i in range(start_num, single_bulk + start_num):
                    line = f.readline()
                    if line:
                        if line in ['\n', '\r\n'] and line.strip() == "":
                            blank_line_num += 1
                            continue
                        else:
                            lines.append(line)
                    else:
                        finish_flag = True
                        break
                # 解析lines
                total_line_cnt += len(lines)
                handle_diting_lines_v1_x(diting_log, lines)
                if not finish_flag:
                    start_num += single_bulk
                    lines = []

        Logging.logger.debug("handle_diting_log_v1_x, : 总行数: %s, 空行数: %s, 解析耗时: %s",
                             str(total_line_cnt), str(blank_line_num), str(time.time() - start_time))
    except Exception as exp:
        Logging.logger.error("handle_diting_log_v1_x, error message: %s", exp)


def handle_diting_lines_v1_x(diting_log, lines):
    try:
        infos = parser.parser_diting(diting_log, lines)
        insert_info_dict_list = infos[0]
        if insert_info_dict_list is None:
            Logging.logger.info("handle_diting_lines_v1_x, The info from file: %s is nothing to insert.", diting_log)
        else:
            Logging.logger.debug("handle_diting_lines_v1_x, Parsing diting-log, create info count: %s",
                                 len(insert_info_dict_list))
            if not save_to_mysql.save_dic_to_mysql(insert_info_dict_list, db_models.NgDiting):
                return False
        update_info_dict_list = infos[1]
        if update_info_dict_list is None:
            Logging.logger.info("handle_diting_lines_v1_x, The info from file: %s is nothing to update.", diting_log)
        else:
            insert_list_tmp = []
            config_items = get_config_dict()
            DB_TABLE_PREFIX = config_items['MySQL']['db_table_prefix']
            diting_table_name = '{}ng_diting'.format(DB_TABLE_PREFIX)
            for info_dict in update_info_dict_list:
                query_sql = "select count(*) from {diting_table_name} where request_id='{request_id}' and uuid='{uuid}'".format(
                    diting_table_name=diting_table_name,
                    request_id=info_dict['request_id'],
                    uuid=info_dict['uuid'])
                result = SqlalchemyMgr.Instance().query_sql(query_sql)
                if result is None or int(result[0][0]) == 0:
                    insert_list_tmp.extend(info_dict)
                    save_to_mysql.save_dic_to_mysql(insert_list_tmp, db_models.NgDiting)
                    Logging.logger.error("handle_diting_lines_v1_x, Insert info to diting table, request_id = %s.",
                                         info_dict['request_id'])
                    continue
                else:
                    update_sql = "update {diting_table_name} set end_time='{end_time}', http_cost_time={http_cost_time} where request_id='{request_id}'".format(
                        diting_table_name=diting_table_name,
                        end_time=info_dict['end_time'],
                        http_cost_time=info_dict['http_cost_time'],
                        request_id=info_dict['request_id'])
                    if not SqlalchemyMgr.Instance().update_sql(update_sql):
                        return False
        return True
    except Exception as exp:
        Logging.logger.error("handle_diting_lines_v1_x, error message: %s", exp)
        return False


# 处理2.x引擎，2.x引擎已知的包括2.4、2.5、2.6
def handle_logs_v2_x(parser_start_time, parser_end_time,):
    try:
        config_items = config.ConfigInfo.get_instance().get_config_items()

        rsync_access_logs = rsync_data(
            os.path.join(config_items['SrcAsrLogDir'], "nls-cloud-asr"),
            os.path.join(config_items['DstLogDir'], "access-log"),
            comm.LogType.ASR_ACCESS.name,
            parser_start_time,
            parser_end_time,
            prefix='access.log',
            isMd5=True
        )
        if rsync_access_logs is None:
            Logging.logger.error("handle_logs_v2_x, rsync access logs is None.")
        else:
            Logging.logger.debug("handle_logs_v2_x, rsync access logs count is %s.", len(rsync_access_logs))
            for access_log in rsync_access_logs:
                handle_asr_access_log_v2_x(access_log)
        if config_items['ClientLogSwitch'] == 'on':
            Logging.logger.debug(os.path.join(config_items['SrcDitingLogDir'], "nls-cloud-realtime"))
            rsync_application_logs = rsync_data(
                os.path.join(config_items['SrcDitingLogDir'], "nls-cloud-realtime"),
                os.path.join(config_items['DstLogDir'], "application_log"),
                comm.LogType.REALTIME_APP.name,
                parser_start_time,
                parser_end_time,
                prefix='application.log',
                isMd5=True
            )
            if rsync_application_logs is None:
                Logging.logger.error("handle_logs_v2_x, rsync application logs is None.")
            else:
                Logging.logger.debug("handle_logs_v2_x, rsync application logs count is %s.",
                                     len(rsync_application_logs))
                for gzip_path in rsync_application_logs:
                    if gzip_path.endswith('.gz'):
                        (app_filepath, app_tempfilename) = os.path.split(gzip_path)
                        (app_shotname, app_extension) = os.path.splitext(app_tempfilename)
                        application_log = os.path.join(app_filepath, app_shotname)
                        gzip_cmd = "gzip -cd {log_dir} > {appl_log}".format(log_dir=gzip_path, appl_log=application_log)
                        cmd_result = subprocess.call([gzip_cmd], shell=True)
                        if cmd_result == 0:
                            handle_realtime_app_log_v2_x(application_log)
                        else:
                            Logging.logger.error("handle_logs_v2_x, gzip %s is Eorror.", gzip_path)
                    else:
                        app_file_time = os.path.getmtime(gzip_path)
                        app_file_date = datetime.fromtimestamp(app_file_time).strftime("%Y-%m-%d")
                        handle_realtime_app_log_v2_x(gzip_path, app_file_date)
            handle_client_log.handle_client_logs()
    except Exception as exp:
        Logging.logger.error("handle_logs_v2_x, error message: %s", exp)


def handle_asr_access_log_v2_x(access_log):
    try:
        Logging.logger.debug("handle_asr_access_log_v2_x, Parsing asr-access-log: %s", access_log)
        info_dict_list = parser.parse_asr_access(access_log)
        if info_dict_list is None:
            Logging.logger.error("handle_asr_access_log_v2_x, The info from file: %s is None.", access_log)
        return save_to_mysql.save_dic_to_mysql(info_dict_list, db_models.UtteranceAccess)
    except Exception as exp:
        Logging.logger.error("handle_asr_access_log_v2_x, error message: %s", exp)
        return False


def handle_realtime_app_log_v2_x(application_log, app_file_date=None):
    try:
        Logging.logger.debug("handle_realtime_app_log_v2_x, Parsing realtime-app-log: %s", application_log)
        start_time = time.time()
        single_bulk = 10000  # 每次读取的行数
        finish_flag = False  # 读取结束标记
        total_line_cnt = 0  # 总行数
        blank_line_num = 0  # 空行数
        start_num = 0
        lines = []
        with codecs.open(application_log, 'rb', encoding='utf-8') as f:
            while not finish_flag:
                for i in range(start_num, single_bulk + start_num):
                    line = f.readline()
                    if line:
                        if line in ['\n', '\r\n'] and line.strip() == "":
                            blank_line_num += 1
                            continue
                        else:
                            lines.append(line)
                    else:
                        finish_flag = True
                        break
                # 解析lines
                total_line_cnt += len(lines)

                if app_file_date:
                    handle_realtime_app_lines_v2_x(application_log, lines, app_file_date)
                else:
                    handle_realtime_app_lines_v2_x(application_log, lines)
                if not finish_flag:
                    start_num += single_bulk
                    lines = []

        Logging.logger.debug("handle_realtime_app_log_v2_x, : 总行数: %s, 空行数: %s, 解析耗时: %s",
                             str(total_line_cnt), str(blank_line_num), str(time.time() - start_time))
    except Exception as exp:
        Logging.logger.error("handle_realtime_app_log_v2_x, error message: %s", exp)


def handle_realtime_app_lines_v2_x(application_log, lines, app_file_date=None):
    try:
        if app_file_date:
            infos = parser.parser_application(application_log, lines, app_file_date)
        else:
            infos = parser.parser_application(application_log, lines)
        insert_info_dict_list = infos[0]
        if insert_info_dict_list is None:
            Logging.logger.info("handle_realtime_app_lines_v2_x, The info from file: %s is nothing to insert.",
                                application_log)
        else:
            Logging.logger.debug("handle_realtime_app_lines_v2_x, Parsing application-log, create info count: %s",
                                 len(insert_info_dict_list))
            if not save_to_mysql.save_dic_to_mysql(insert_info_dict_list, db_models.NgDiting):
                return False
        update_info_dict_list = infos[1]
        if update_info_dict_list is None:
            Logging.logger.info("handle_realtime_app_lines_v2_x, The info from file: %s is nothing to update.",
                                application_log)
        else:
            Logging.logger.debug("handle_realtime_app_lines_v2_x, Parsing application-log, update info count: %s",
                                 len(update_info_dict_list))
            insert_list_tmp = []
            config_items = get_config_dict()
            DB_TABLE_PREFIX = config_items['MySQL']['db_table_prefix']
            diting_table_name = '{}ng_diting'.format(DB_TABLE_PREFIX)
            for info_dict in update_info_dict_list:
                query_sql = "select count(*) from {diting_table_name} where request_id='{request_id}' " \
                            "and uuid='{uuid}'".format(
                    diting_table_name=diting_table_name,
                    request_id=info_dict['request_id'],
                    uuid=info_dict['uuid'])
                result = SqlalchemyMgr.Instance().query_sql(query_sql)
                if result is None or int(result[0][0]) == 0:
                    insert_list_tmp.extend(info_dict)
                    save_to_mysql.save_dic_to_mysql(insert_list_tmp, db_models.NgDiting)
                    Logging.logger.error(
                        "handle_realtime_app_lines_v2_x, Insert info to diting table, request_id = %s.",
                        info_dict['request_id'])
                    continue
                else:
                    update_sql = "update {diting_table_name} set end_time='{end_time}'," \
                                 " http_cost_time={http_cost_time} where request_id='{request_id}'".format(
                        diting_table_name= diting_table_name,
                        end_time=info_dict['end_time'],
                        http_cost_time=info_dict['http_cost_time'],
                        request_id=info_dict['request_id'])
                    if not SqlalchemyMgr.Instance().update_sql(update_sql):
                        return False
        return True
    except Exception as exp:
        Logging.logger.error("handle_realtime_app_lines_v2_x, error message: %s", exp)
        return False


def copy_parse_logs(src_dir, dst_dir, log_prefix, handle_mechod, file_type):
    if config.ConfigInfo.get_instance().get_config_items()['RemoteSwitch'] == 'on':
        copy_parse_remote_logs(src_dir, dst_dir, log_prefix, handle_mechod, file_type)
    else:
        copy_parse_local_logs(src_dir, dst_dir, log_prefix, handle_mechod, file_type)


def copy_parse_remote_logs(remote_dir, local_dir, log_prefix, handle_mechod, file_type):
    Logging.logger.debug("copy_parse_remote_logs: 拷贝解析远程服务器日志。")
    try:
        config_items = config.ConfigInfo.get_instance().get_config_items()
        remote_mgr = RemoteControlMgr.Instance()
        remote_mgr.Init(config_items['RemoteHost'], config_items['RemotePort'], config_items['RemoteUser'],
                        config_items['RemotePwd'])
        if not remote_mgr.connect():
            Logging.logger.debug("copy_parse_remote_logs: connect remote server failed.")
            return

        remote_file_list = remote_mgr.get_files_in_remote_dir(remote_dir, file_prefix=log_prefix)
        if remote_file_list is None or len(remote_file_list) == 0:
            Logging.logger.debug("copy_parse_remote_logs: Get 0 %s log to handle.", log_prefix)
            return
        for remote_file_info in remote_file_list:
            remote_file = remote_file_info.get('file', None)
            if remote_file is None:
                continue
            try:
                # 远程拷贝文件
                local_file = os.path.join(local_dir, remote_file[len(remote_dir):].lstrip('/'))
                Logging.logger.debug("copy_parse_remote_logs: copy remote file: %s to local file: %s.", remote_file,
                                     local_file)
                local_path = os.path.split(local_file)[0]
                if not os.path.exists(local_path):
                    os.makedirs(local_path)
                remote_mgr.sftp_get(remote_file, local_file)
                # 删除远程文件
                # cmd = 'rm -f {0}'.format(remote_file)
                # remote_mgr.send_command(cmd)
                # Logging.logger.debug("handle_audios:  execute remote command: %s.", cmd)
                # 解析本地文件，并保存到数据库
                save_log_result = handle_mechod(local_file)
                file_info_dict = dict(
                    create_time=int(time.time()),
                    is_deleted=0,
                    file_name=os.path.split(local_file)[1],
                    path=local_file,
                    origin_st_mtime=remote_file_info['st_mtime'],
                    st_size=remote_file_info['st_size'],
                    ng_version=config_items['EngineVersion'],
                    type=file_type
                )
                file_info_dict_list = list()
                file_info_dict_list.append(file_info_dict)
                if save_log_result:
                    save_file_result = save_to_mysql.save_dic_to_mysql(file_info_dict_list, db_models.NgBakFile)
                    if not save_file_result:
                        # 保存bak_file信息到文件
                        pass
                else:
                    # 保存utterance和bak_file到文件
                    pass

            except Exception as exp:
                Logging.logger.error("copy_parse_remote_logs: 处理文件 %s 时报错：%s", remote_file, exp.message)
        remote_mgr.close()
    except Exception as exp:
        Logging.logger.error("copy_parse_remote_logs: error message: %s.", exp.message)


def copy_parse_local_logs(src_dir, dst_dir, log_prefix, handle_mechod, file_type):
    Logging.logger.debug("copy_parse_local_logs: 拷贝解析本地服务器日志。")
    try:
        config_items = config.ConfigInfo.get_instance().get_config_items()
        handle_file_list = comm.get_files_in_local_dir(src_dir, file_prefix=log_prefix)
        if handle_file_list is None or len(handle_file_list) == 0:
            Logging.logger.debug("copy_parse_local_logs: Get 0 %s log to handle.", log_prefix)
            return
        for handle_file_info in handle_file_list:
            src_file = handle_file_info.get('file', None)
            if src_file is None:
                continue
            try:
                # 拷贝文件
                dst_file = os.path.join(dst_dir, src_file[len(src_dir):].lstrip('/'))
                Logging.logger.debug("copy_parse_local_logs: copy file: %s to file: %s.", src_file, dst_file)
                dst_path = os.path.split(dst_file)[0]
                if not os.path.exists(dst_path):
                    os.makedirs(dst_path)
                comm.copy_file(src_file, dst_file, is_replace=True)
                # 删除文件
                # os.remove(src_file)
                # 解析本地文件，并保存到数据库
                save_log_result = handle_mechod(dst_file)
                file_info_dict = dict(
                    create_time=int(time.time()),
                    is_deleted=0,
                    file_name=os.path.split(dst_file)[1],
                    path=dst_file,
                    origin_st_mtime=handle_file_info['st_mtime'],
                    st_size=handle_file_info['st_size'],
                    ng_version=config_items['EngineVersion'],
                    type=file_type
                )
                file_info_dict_list = list()
                file_info_dict_list.append(file_info_dict)
                if save_log_result:
                    save_file_result = save_to_mysql.save_dic_to_mysql(file_info_dict_list, db_models.NgBakFile)
                    if not save_file_result:
                        # 保存bak_file信息到文件
                        pass
                else:
                    # 保存utterance和bak_file到文件
                    pass

            except Exception as exp:
                Logging.logger.error("copy_parse_local_logs: 处理文件 %s 时报错：%s", src_file, exp.message)
    except Exception as exp:
        Logging.logger.error("copy_parse_local_logs: error message: %s.", exp.message)
