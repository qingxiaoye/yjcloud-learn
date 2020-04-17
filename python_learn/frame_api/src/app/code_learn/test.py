# !/usr/bin/python
# -*- coding:utf-8 -*-
from datetime import datetime
from datetime import date, timedelta

import  pandas as pd
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
# def get_date_list(start_time, end_time):
#     start_time = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d')
#     print(start_time)
#     print(end_time)
#     end_time = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d')
#     date_list = [datetime2timestamp(x) for x in list(pd.date_range(start=start_time, end=end_time, freq='D'))]
#     return date_list
#
# print(get_date_list(1585497600,1585584000))
#
# print('-'*10)
# x =[1577462400, 1577462400, 1577548800, 1577548800, 1577635200, 1577635200, 1577721600, 1577808000, 1577894400, 1577980800]
# x=list(set(x))
# x.sort()
# print(x)
# x=[1577462400, 1577548800, 1577635200, 1582646400, 1585065600, 1585152000, 1585238400, 1585324800, 1585411200, 1585497600, 1585584000]
#
# for i in x:
#     print(datetime.fromtimestamp(i))


def get_hour_list(start_time, end_time):
    start_time = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H')
    end_time = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H')


    date_list = [datetime2timestamp(x) for x in list(pd.date_range(start=start_time, end=end_time, freq='H'))]
    return  date_list

# print(get_date_list(1575129600,1575139600))
print('-----------------------')
x=[1576857600, 1576944000, 1577030400, 1577116800, 1577203200, 1577289600, 1577376000, 1577462400, 1577548800, 1577635200, 1577721600]
for i in x:
    print(datetime.fromtimestamp(i))