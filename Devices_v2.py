from pprint import pprint
import numpy as np
from datetime import datetime, timedelta, time

#configuration
#1. home IP
#2. home Port range
#3. 기기리스트 - 템플릿
#4. 시작 날짜 - 마감 날짜

SESSION_ID_RANGE = [i for i in range(65000)]

def size_packet(level):
    size_list = [[10,1],[50,4],[250,4],[500,25],[1000,100],[5000,4]]
    size = np.round(np.random.normal(size_list[level][0],size_list[level][1]))
    return size

def make_function(srcip, srcport, dstip, dstport, udlist, time_list, packet_list):
    global SESSION_ID_RANGE
    session_id = np.random.choice(SESSION_ID_RANGE)
    SESSION_ID_RANGE.remove(session_id)

    total_packet = []
    for i, ud in enumerate(udlist):
        if ud == "UP":
            line = [time_list[i]] + [srcip, srcport, dstip, dstport, size_packet(packet_list[i])] + [session_id]
        elif ud == "DN":
            line = [time_list[i]] + [dstip, dstport, srcip, srcport, size_packet(packet_list[i])] + [session_id]
        total_packet += [line]
    return total_packet

def time_plus_packet(active_time, packet_list):
    all_time = []
    packets = []
    for i, packet in enumerate(packet_list):
        time = (active_time + timedelta(seconds = packet[0])).strftime('%Y-%m-%d %H:%M:%S')
        packets += [[time] + packet[1:]]
    all_time += packets
    return all_time

def itertime_action(from_time, to_time, interval1, interval2, packet_list, packet_level):
    import copy 
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
        action = time_plus_packet(time, packet_list)
        src = np.random.randint(action[0][2][0], action[0][2][1])
        dst = np.random.randint(action[0][4][0], action[0][4][1])
        action[0][2], action[0][4] = src, dst
        action[1][2], action[1][4] = dst, src
        session_id = np.random.choice(SESSION_ID_RANGE)
        SESSION_ID_RANGE.remove(session_id)
        action[0][6], action[1][6] = session_id, session_id
        itertime_packet.append(action)
        j += 1
    return itertime_packet

