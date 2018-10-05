from pprint import pprint
import numpy as np
from datetime import datetime, timedelta, time
import math
import copy 
#configuration
#1. home IP
#2. home Port range
#3. 기기리스트 - 템플릿
#4. 시작 날짜 - 마감 날짜

SESSION_ID_RANGE = [i for i in range(65001)]

def size_packet(level):
    size_list = [[10,1],[50,4],[250,4],[500,25],[1000,100],[5000,4]]
    size = np.round(np.random.normal(size_list[level][0],size_list[level][1]))
    return size

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

def time_plus_packet(start_time, finish_time, packet_list, max_trials):
    all_time = []
    packets = []
    time_gap = (finish_time - start_time).total_seconds()
    selected_plus_time = list(np.random.randint(0, time_gap+1, size = max_trials))
    selected_plus_time[0] = 0
    selected_plus_time.sort()
    last_time_list = [0 for _ in range(10)]
    last_time_list[0] = start_time - timedelta(seconds = 1)
    for i, s_time in enumerate(selected_plus_time):
        in_time = start_time + timedelta(seconds = s_time)
        print(last_time_list[i])
        if in_time > last_time_list[i]:
            for packet in packet_list:
                cost_time = packet[0]
                _trial = math.ceil(cost_time)
                for _ in range(_trial):
                    plus_time = (in_time + timedelta(seconds = 1)).strftime('%Y-%m-%d %H:%M:%S')
                    packets += [[plus_time] + packet[1:-3] + [packet[-3]/_trial] + packet[-2:]]
                    last_time = (in_time + timedelta(seconds = 1))
                last_time_list.append(last_time)


    ### 스타트와 피니시 타임을 전달 받고 해당 시간내에 두번 실행하는 경우 어떻게 설계?

    all_time += packets
    return all_time

def itertime_action(from_time, to_time, interval1, interval2, packet_list, packet_level):

    global SESSION_ID_RANGE
    
    itertime_packet = []
    interval_criterion = {"hour":24*60 ,"min":60, "seconds":1}
    change_sec = interval1 * interval_criterion[interval2]
    time_gap = to_time-from_time
    execute_times = (time_gap / change_sec).seconds
    time = from_time

    j=0
    while time < to_time:
        time = time + timedelta(seconds = change_sec*1)
        for i, packet in enumerate(packet_list):
            packet_list[i][5] = size_packet(packet_level[i])
        action = time_plus_packet(time,time, packet_list, 1)
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

