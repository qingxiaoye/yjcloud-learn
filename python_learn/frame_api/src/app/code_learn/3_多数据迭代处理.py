# !/usr/bin/python
# -*- coding:utf-8 -*-

list1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
single_bulk = 6  # 每次读取的行数
finish_flag = False  # 读取结束标记
total_line_cnt = 0  # 总行数
start_num = 0
datas = []

audio_files_list = ['/home/user/xiaoqq/qia/audio/test/test1.wav',
                    '/home/user/xiaoqq/qia/audio/test/test2.wav',
                    '/home/user/xiaoqq/qia/audio/test/test3.wav',
                    '/home/user/xiaoqq/qia/audio/test/test4.wav',
                    '/home/user/xiaoqq/qia/audio/test/test5.wav',
                    ]
single_bulk = 2  # 每次读取的行数
finish_flag = False  # 读取结束标记
total_line_cnt = 0  # 总行数
start_num = 0
audio_files_bulk = []

while not finish_flag:
    end_num = start_num + single_bulk

    for i in range(start_num, end_num):

        if end_num <= len(audio_files_list):
            end_num = start_num + single_bulk
            audio_files_bulk = audio_files_list[start_num:end_num]
        elif (start_num <= len(audio_files_list)) and (end_num >= len(audio_files_list)):
            audio_files_bulk = audio_files_list[start_num:]
        else:
            finish_flag = True
            break
    print(audio_files_bulk)
    if not finish_flag:
        start_num += single_bulk
        audio_files_bulk = []
