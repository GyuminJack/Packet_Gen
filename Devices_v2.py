from pprint import pprint
import numpy as np
from datetime import datetime, timedelta, time
import pandas as pd
import math
import copy 

#세션 아이디를 관리하기 위한 전역변수



#패킷의 사이즈를 리턴하는 함수
def size_packet(level):
    size_list = [[20,0],[40,0.5],[80,0],[150,0],[300,0],[1000,0],[3000000,0.5]]
    if level == 0:
        size = 0
    else:
        size = int(np.random.normal(size_list[level][0],size_list[level][1]))
    return size

#기본 단위 패킷을 생성
def make_function(vendor, function_name, srcip, srcport, dstip, dstport, udlist, protocol_list, time_list, packet_list):
    session_id = int(np.random.randint(0,100000,size=1))
    total_packet = []
    for i, ud in enumerate(udlist):
        if ud == "UP":
            line = [time_list[i]] + [srcip, srcport, dstip, dstport, protocol_list[i], size_packet(packet_list[i])] + [session_id] + [vendor] + [function_name]
        elif ud == "DN":
            line = [time_list[i]] + [dstip, dstport, srcip, srcport, protocol_list[i], size_packet(packet_list[i])] + [session_id] + [vendor] + [function_name]
        total_packet += [line]
    return total_packet

# 기본단위 패킷에 시간정보를 더함
def time_plus_packet(_start_time, _finish_time, packet_list, max_trials, network_byte_per_sec):
    during_time = 0 #기본 단위 패킷에 대한 총 시간
    for packet in packet_list:
        during_time += packet[0]

    # 시작 시간과 종료 시간이 다를 경우 max_trial만큼의 시작 시간을 추출
    if _finish_time != _start_time:
        time_gap = (_finish_time - _start_time).total_seconds()
        selected_time = list(np.random.uniform(0, time_gap, max_trials))
        selected_time.sort()
        # selected_time[0] = 0
    else:
        # 반복작업의 경우 시작시간과 종료시간 같음.
        # 해당 경우에는 0~59초 사이에 하나의 숫자만 선택
        selected_time = list(np.random.uniform(0,60,max_trials))

    # 처음 추출된 시작시간에 대해 총시간을 체크해 한번 더 걸러냄.
    second_select = []
    for i, item in enumerate(selected_time):
        if i == 0:
            second_select.append(item)
        elif (i >= 1) & (item - during_time > selected_time[i-1]):
            second_select.append(item)


    # 시작시간에 걸러진 시간들을 더함.
    new_time_list = pd.Series(second_select).apply(lambda x: (datetime(_start_time.year, _start_time.month
    ,_start_time.day, _start_time.hour, _start_time.minute, _start_time.second) + timedelta(seconds = x)))
    # new_time_list => 패킷을 생성할 시작 시간.
    # 패킷 생성.
    all_time = []
    packets = []

    # print(packet_list) 기본단위 패킷 입력됨.
    for i, in_time in enumerate(new_time_list):
        session_id = int(np.random.randint(0,100000,size=1))
        for packet in packet_list:
            working_time = packet[0]
            moving_time = packet[-4]/network_byte_per_sec
            packet[0] = packet[0] + float(np.random.uniform(0, packet[0]/10, 1))
            packet[-3] = session_id
            cost_time = packet[0]
            minimum_packet = 1460
            if packet[-4] > minimum_packet:
                moving_time = minimum_packet/network_byte_per_sec
                _trial = math.ceil(packet[-4] / minimum_packet)
                _divide_time = np.random.uniform(moving_time, moving_time*1.2, _trial) 
                _length_trial = [minimum_packet for _ in range(_trial-1)] + [packet[-4] - minimum_packet*(_trial-1)]
                in_time = in_time + timedelta(seconds = working_time)
                for i, divide_packet in enumerate(_length_trial):
                    plus_time = (in_time + timedelta(seconds = _divide_time[i])).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    packets += [[plus_time] + packet[1:-4] + [divide_packet] + packet[-3:]]
                    in_time = (in_time + timedelta(seconds = _divide_time[i]))
            else:
                plus_time = (in_time + timedelta(seconds = working_time + moving_time)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                packets += [[plus_time] + packet[1:-4] + [packet[-4]] + packet[-3:]]
                in_time = (in_time + timedelta(seconds =  working_time + moving_time))
    all_time += packets
    
    return all_time

# 반복작업(ex. firmware_check)에 대한 패킷 생성.
device_firmware_update_dict = {}
def itertime_action(from_time, to_time, interval1, interval2, packet_list, packet_level, device_name, fsname, Network_speed):

    global device_firmware_update_dict
    itertime_packet = []
    interval_criterion = {"hour":24*60 ,"min":60, "seconds":1}
    change_sec = interval1 * interval_criterion[interval2] #다음 시작
    time_gap = to_time-from_time
    execute_times = (time_gap / change_sec).seconds
    # 작업마다 세션아이디와 포트를 재설정하기 위해.
    if fsname != "Port_scan":
        ########################### 시작
        
        # firmware check를 위한 코드들 / 펌웨어 업데이트를 특정 시간에 진행하는 코드를 확인할 필요가 있음.
        j=0
        src = list(np.random.randint(packet_list[0][2][0],packet_list[0][2][1], size =100))
        dst = list(np.random.randint(packet_list[0][4][0],packet_list[0][4][1], size =100))
        while from_time < to_time:
            from_time = from_time + timedelta(seconds = change_sec*1)
            src_port = int(np.random.choice(src,size=1))
            dst_port = int(np.random.choice(dst,size=1))
            for i, packet in enumerate(packet_list):
                packet_list[i][6] = size_packet(packet_level[i])
                if i % 2 == 0 :
                    packet_list[i][2] = src_port
                    packet_list[i][4] = dst_port
                else:
                    packet_list[i][2] = dst_port
                    packet_list[i][4] = src_port
            action = time_plus_packet(from_time, from_time, packet_list, 1, Network_speed)

            # action[0][2], action[0][4] = src, dst
            # action[1][2], action[1][4] = dst, src
            session_id = int(np.random.randint(0,100000,size=1))
            for packets in action:
                packets[7] = session_id
            
            itertime_packet.append(action)
            if "firmware_check" in fsname:
                upgrade_list = []
                if np.random.normal(0,1) > 3.5:
                    DN_time = np.random.randint(1,10)
                    DN_size = int(np.random.normal(1000,0.1))
                    upgrade_datetime = action[1][0]
                    # upgrade_list.append(upgrade_datetime)
                    for i in range(DN_time):
                        download_action = copy.deepcopy(action[1])
                        download_datetime = datetime.strptime(download_action[0], '%Y-%m-%d %H:%M:%S.%f')
                        download_action[0] = (download_datetime + timedelta(seconds = i+1)).strftime('%Y-%m-%d %H:%M:%S.%f')
                        download_action[6] = DN_size
                        itertime_packet.append([download_action])
                    try:
                        device_firmware_update_dict[device_name].append(upgrade_datetime)
                    except:
                        device_firmware_update_dict[device_name] = []
                        device_firmware_update_dict[device_name].append(upgrade_datetime)
            j += 1
    elif fsname == 'Port_scan':
        port_list = packet_list[0][2]
        max_attack_trial = interval1
        changetime=[(to_time-from_time).total_seconds()][0]
        random_list = list(np.random.randint(0,int(changetime),size = max_attack_trial))
        random_list.sort()
        new_time_list = []
        for i in range(0,len(random_list)-1):
            if random_list[i+1] - random_list[i] > len(port_list):
                new_time_list.append(random_list[i])
        for new_time in new_time_list:
            try_thred = np.random.normal(0,1)
            if abs(try_thred)>1:
                A_time = from_time + timedelta(seconds = int(new_time))
                for j, _port in enumerate(port_list):
                    _time = A_time + timedelta(seconds = 1)
                    new_packet = copy.deepcopy(packet_list)
                    new_packet[0][2] = _port
                    ho_port = int(np.random.randint(new_packet[0][4][0],new_packet[0][4][1],size=1))
                    new_packet[0][4] = ho_port
                    action = time_plus_packet(_time, _time, new_packet, 1, Network_speed)
                    itertime_packet.append(action)
    return itertime_packet
