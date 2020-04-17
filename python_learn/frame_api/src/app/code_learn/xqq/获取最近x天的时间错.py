# !/usr/bin/python
# -*- coding:utf-8 -*-
from datetime import datetime
from datetime import date, timedelta


def datetime2timestamp(datetime_v):
    # python3
    # if not isinstance(datetime_v, datetime):
    #     return None
    # return int(time.mktime(datetime_v.timetuple()))

    # python3
    if isinstance(datetime_v, datetime):
        return int(datetime.timestamp(datetime_v))
    elif isinstance(datetime_v, date):
        return int(datetime.timestamp(datetime.combine(datetime_v, datetime.min.time())))
    else:
        return None

print(datetime2timestamp('2020-03-25 00:00:00'))
# #
# #     return _shift_day_list
#
#
# def get_date_interval(day_shift):
#     _today = date.today()
#     _shift_day_list = []
#     for i in range(day_shift):
#         _shift_day = datetime2timestamp((_today - timedelta(days=i)))
#         # _shift_day = (_today - timedelta(days=i))
#         _shift_day_list.append(_shift_day)
#
#     return _shift_day_list
#
#
# print(get_date_interval(2))
#
# import pandas as pd
#
# # def get_date_list(start_time, end_time):
# #     start_time = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d')
# #     end_time = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d')
# #     print(start_time)
# #     print(end_time)
# #     print(pd.date_range(start=start_time, end=end_time))
# #     date_list = [x.strftime('%Y-%m-%d') for x in list(pd.date_range(start=start_time, end=end_time, freq='D'))]
# #     return date_list
# #
# # ### 可以测试
# # print(get_date_list(1585389600, 1585645200))
