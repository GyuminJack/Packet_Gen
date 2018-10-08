from pprint import pprint
import numpy as np
from datetime import datetime, timedelta, time
import pandas as pd
import math
import copy 

#세션 아이디를 관리하기 위한 전역변수
SESSION_ID_RANGE = [i for i in range(65001)]

#패킷의 사이즈를 리턴하는 함수
def size_packet(level):
    size_list = [[10,1],[50,4],[250,4],[500,25],[1000,100],[5000,4]]
    size = np.round(np.random.normal(size_list[level][0],size_list[level][1]))
    return size

#기본 단위 패킷을 생성
def make_function(vendor,srcip, srcport, dstip, dstport, udlist, time_list, packet_list):
    global SESSION_ID_RANGE
    session_id = int(np.random.choice(SESSION_ID_RANGE))
    SESSION_ID_RANGE.remove(session_id)

    total_packet = []
    for i, ud in enumerate(udlist):
        if ud == "UP":
            line = [time_list[i]] + [srcip, srcport, dstip, dstport, size_packet(packet_list[i])] + [session_id] + [vendor]
        elif ud == "DN":
            line = [time_list[i]] + [dstip, dstport, srcip, srcport, size_packet(packet_list[i])] + [session_id] + [vendor]
        total_packet += [line]
    return total_packet

# 기본단위 패킷에 시간정보를 더함
def time_plus_packet(_start_time, _finish_time, packet_list, max_trials):
    during_time = 0 #기본 단위 패킷에 대한 총 시간
    for packet in packet_list:
        during_time += packet[0]
    
    # 시작 시간과 종료 시간이 다를 경우 max_trial만큼의 시작 시간을 추출
    if _finish_time != _start_time:
        time_gap = (_finish_time - _start_time).total_seconds()
        selected_time = list(np.random.randint(0, time_gap, size = max_trials))
        selected_time.sort()
        # selected_time[0] = 0
    else:
        # 반복작업의 경우 시작시간과 종료시간 같음.
        # 해당 경우에는 0~59초 사이에 하나의 숫자만 선택
        selected_time = list(np.random.randint(0, 59, size = max_trials))
    

    # 처음 추출된 시작시간에 대해 총시간을 체크해 한번 더 걸러냄.
    second_select = []
    for i, item in enumerate(selected_time):
        if i == 0:
            second_select.append(item)
        elif (i >= 1) & (item - during_time > selected_time[i-1]):
            second_select.append(item)
    
    # 시작시간에 걸러진 시간들을 더함.
    new_time_list = pd.Series(second_select).apply(lambda x: datetime(_start_time.year, _start_time.month
    ,_start_time.day, _start_time.hour, _start_time.minute, _start_time.second) + timedelta(seconds = x))

    # 패킷 생성.
    all_time = []
    packets = []
    for i, in_time in enumerate(new_time_list):
        session_no = int(np.random.choice(SESSION_ID_RANGE))
        SESSION_ID_RANGE.remove(session_no)
        for packet in packet_list:
            packet[-2] = session_no
            cost_time = packet[0]
            _trial = math.ceil(cost_time)
            for _ in range(_trial):
                # 초단위로 패킷을 구분해서 생성.
                plus_time = (in_time + timedelta(seconds = 1)).strftime('%Y-%m-%d %H:%M:%S')
                each_packet = [[plus_time] + packet[1:-3] + [packet[-3]/_trial] + packet[-2:]]
                packets += each_packet 
                in_time = (in_time + timedelta(seconds = 1))

    all_time += packets
    return all_time

# 반복작업(ex. firmware_check)에 대한 패킷 생성.
def itertime_action(from_time, to_time, interval1, interval2, packet_list, packet_level):

    global SESSION_ID_RANGE
    
    itertime_packet = []
    interval_criterion = {"hour":24*60 ,"min":60, "seconds":1}
    change_sec = interval1 * interval_criterion[interval2]
    time_gap = to_time-from_time
    execute_times = (time_gap / change_sec).seconds
    time = from_time

    # 작업마다 세션아이디와 포트를 재설정하기 위해.
    j=0
    while time < to_time:
        time = time + timedelta(seconds = change_sec*1)
        for i, packet in enumerate(packet_list):
            packet_list[i][5] = size_packet(packet_level[i])
        action = time_plus_packet(time, time, packet_list, 1)
        src = int(np.random.randint(action[0][2][0], action[0][2][1], size=1))
        dst = int(np.random.randint(action[0][4][0], action[0][4][1], size=1))
        action[0][2], action[0][4] = src, dst
        action[1][2], action[1][4] = dst, src
        session_id = np.random.choice(SESSION_ID_RANGE)
        SESSION_ID_RANGE.remove(session_id)
        action[0][6], action[1][6] = session_id, session_id
        itertime_packet.append(action)
        if np.random.normal(0,1) > 2:
            DN_time = np.random.randint(1,15)
            DN_size = int(np.random.normal(1000,100))
            for i in range(DN_time):
                download_action = copy.deepcopy(action[1])
                download_datetime = datetime.strptime(download_action[0], '%Y-%m-%d %H:%M:%S')
                download_action[0] = (download_datetime + timedelta(seconds = i+1)).strftime('%Y-%m-%d %H:%M:%S')
                download_action[5] = DN_size
                itertime_packet.append([download_action])
        j += 1
    return itertime_packet

