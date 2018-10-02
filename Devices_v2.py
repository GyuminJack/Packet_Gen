from pprint import pprint
import numpy as np
from datetime import datetime, timedelta, time

#configuration
#1. home IP
#2. home Port range
#3. 기기리스트 - 템플릿
#4. 시작 날짜 - 마감 날짜
#5. 
def size_packet(level):
    size_list = [[10,1],[50,4],[250,4],[500,25],[1000,100],[5000,4]]
    size = np.round(np.random.normal(size_list[level][0],size_list[level][1]))
    return size

def make_function(srcip, srcport, dstip, dstport, udlist, time_list, packet_list):
    total_packet = []
    for i, ud in enumerate(udlist):
        if ud == "UP":
            line = [time_list[i]] + [srcip, srcport, dstip, dstport, size_packet(packet_list[i])]
        elif ud == "DN":
            line = [time_list[i]] + [dstip, dstport, srcip, srcport, size_packet(packet_list[i])]
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
    itertime_packet = []
    interval_criterion = {"hour":24 ,"min":60, "seconds":1}
    change_sec = interval1 * interval_criterion[interval2]
    time_gap = to_time-from_time
    execute_times = (time_gap / change_sec).seconds
    time = from_time
    import copy 
    j=0
    while time < to_time:
        time = time + timedelta(seconds = change_sec*1)
        for i, packet in enumerate(packet_list):
            packet_list[i][5] = size_packet(packet_level[i])
            print(packet_list)
        action = time_plus_packet(time, packet_list)
        src = np.random.randint(action[0][2][0], action[0][2][1])
        dst = np.random.randint(action[0][4][0], action[0][4][1])

        action[0][2], action[0][4] = src, dst
        action[1][2], action[1][4] = dst, src
        itertime_packet.append(action)
        j += 1
    return itertime_packet

if __name__ == "__main__":
    HomeIP = "192.168.0.1"
    HomePort_RANGE = [100,1044]
    
    SK_IP = "124.234.23.2"
    SK_PORT_RANGE = [300,400]
    udlist = ["UP","DN","UP","DN"]
    time_list = [1, 2, 3, 5]
    packet_list = [1, 1, 2, 3]


    news_request = make_function(HomeIP, HomePort_RANGE, SK_IP, SK_PORT_RANGE, udlist, time_list, packet_list)
    weather_request = make_function(HomeIP, HomePort_RANGE, SK_IP, SK_PORT_RANGE, udlist, time_list, packet_list)
    movie_request = make_function(HomeIP, HomePort_RANGE, SK_IP, SK_PORT_RANGE, udlist, time_list, packet_list)
    daily_news = time_plus_packet(datetime(2018,1,1,0,0,0), news_request)

    SK_nugu = news_request+weather_request+movie_request
    pprint(SK_nugu)
    # device1.start_time = data_gen_start
    # device1.finish_time = data_gen_finish
    # print(device1.make_packet())



