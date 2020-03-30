# -*- coding:utf-8 -*-
import urllib.request
import requests

import json


def warn_ding_talk(qc_time, call_id, paragraph_id, map_rule_name, url):
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    data = {
        "msgtype": "text",
        "text": {
            "content": "质检时间：{}".format(qc_time) + '\n' + "通话ID：{}".format(call_id) + '\n' +
                       "段落ID：{}".format(paragraph_id) + '\n' + "命中规则：{}".format(map_rule_name)
        },
        "at": {
            "atMobiles": [
                "18834151306",
                # "15735646017"
            ],
            "isAtAll": False  # @全体成员（在此可设置@特定某人）
        }
    }
    send_data = json.dumps(data)
    send_data = send_data.encode("utf-8")
    requests.post(url=url, data=send_data, headers=header)

# warn_ding_talk('2020-02-21 10:15:20', '12345', 'aaaaa', '模板一-关键词规则', 'https://oapi.dingtalk.com/robot/send?access_token=3f9ea23acb026a30c8e323090becbc5c6dfa4e3830ec8c914a2b1e3605955e6e')

def warn_message(qc_time, call_id, paragraph_id, map_rule_name, warning_message):
    pass


def warn_apps(qc_time, call_id, paragraph_id, map_rule_name, warning_apps):
    pass