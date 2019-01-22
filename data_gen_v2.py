from Devices_v2 import *
import json
import pandas as pd
import re
import os
import mac_address_maker
import traceback
import random
#ip change
import ipaddress

def change_to_ip(_ip):
    new_list = [str(ip) for ip in ipaddress.IPv4Network(_ip)]
    selected_ip = random.choice(new_list)
    return selected_ip

# 각 user를 define 하기 위한 class
class user_type:
    def __init__(self):
        self.time_action = []
    def action_add(self,start_time,finish_time,action,max_trial, max_stream_time, day_end):
        start_hour, start_min = int(str(start_time)[:-2]), int(str(start_time)[-2:])
        finish_hour, finish_min = int(str(finish_time)[:-2]), int(str(finish_time)[-2:])
        min_to_start = start_hour*60 + start_min
        min_to_finish = finish_hour*60 + finish_min
        select_time = int(np.random.randint(min_to_start, min_to_finish, size = 1))
        g_time_H = int(select_time/60)
        g_time_M = (select_time) - 60*g_time_H
        self.time_action.append([g_time_H,g_time_M, finish_hour, finish_min, action,max_trial,max_stream_time,day_end])
    def time_action(self):
        return self.time_action

# Home 객체를 생성
# c 클래스 이하 3자리를 겹치지 않게 하기 위한 메모리
IP_list = []
mac_list = []
home_Port_range = [i for i in range(1,65535)]

class Home():
    def __init__(self, HOME_NAME, IP, PORT_RANGE, Network_speed):
        global IP_range
        global mac_list
        self.Home_name = HOME_NAME
        self.IP = IP
        self.Network_speed = Network_speed
        self.PORT_RANGE = PORT_RANGE
        self.Mac_Address_list = mac_address_maker.mac_address_maker(300)
    # 개별 Device들의 설정정보를 불러오고 IP / Port 설정
    def device_setting(self, device_list):
        try:
            with open('./Config/DeviceConfig.json','r') as f:
                self.all_device_dict = json.load(f)
        except:
            print("DeviceConfig error")
        self.selected_device_dict = {}
        for k in self.all_device_dict:
            if k in device_list:
                self.selected_device_dict[k] = copy.deepcopy(self.all_device_dict[k])
                self.selected_device_dict[k]["Device IP"] = change_to_ip(self.IP)
                while self.selected_device_dict[k]["Device IP"] in IP_list:
                    self.selected_device_dict[k]["Device IP"] = change_to_ip(self.IP)
                IP_list.append(self.selected_device_dict[k]["Device IP"])
                selected_device_ip = int(int(self.selected_device_dict[k]["Device IP"].split(".")[3]))
                self.selected_device_dict[k]["MAC_Addr"] = self.Mac_Address_list[selected_device_ip]
                mac_list.append(self.selected_device_dict[k]["MAC_Addr"])
                self.selected_device_dict[k]["Device_PortRange"] = [0,65535]
                

    # 개별 User를 불러오고 해당 유저의 패턴을 생성
    def user_setting(self,custom_user_list):
        try:
            with open('./Config/UserConfig.json','r') as f:
                all_user_dict = json.load(f)
        except:
            print("UserConfig error")
        in_home_user = []
        for each_user in all_user_dict:
            if each_user in custom_user_list:
                each_user_config = user_type()
                for _dayend in all_user_dict[each_user]:
                    action_root = all_user_dict[each_user][_dayend]
                    for key in action_root:
                        action = key
                        action_start = action_root[key]['start_time']
                        action_finish = action_root[key]['finish_time']
                        action_max_trial = action_root[key]['max_trial']
                        try:
                            action_stream_time = action_root[key]['max_stream_time']
                        except:
                            action_stream_time = 0
                        each_user_config.action_add(action_start, action_finish, action, action_max_trial, action_stream_time, _dayend)
                in_home_user.append(each_user_config)
        self.user_list = in_home_user
        # print(self.user_list) / 결과 : [<__main__.user_type object at 0x0000021D6981BC50>] user들의 객체를 관리
        # self.user_list[0] = home.user_type객체 세부 메서드 time_action으로 정보를 가져오고 해당 내용에 맞게 패킷을 생성함.
    
    # 유저정보와 기기정보를 합하여 패킷을 생성
    def packet_generate(self, from_date, to_date):
        self.from_date = from_date
        self.to_date = to_date
        self.time_gap = to_date - from_date
        # make all day routine
        print("User pattern Making start")
        all_user_pattern = []
        # 개별 유저의 행동 패턴 생성
        for i, user in enumerate(self.user_list):
            # 주중 주말 구분
            weekday_user_pattern = [] # 주중
            weekend_user_pattern = [] # 주말
            for _action_list in user.time_action:
                if _action_list[-1] == 'weekday':
                    weekday_user_pattern.append(_action_list)
                else:
                    weekend_user_pattern.append(_action_list)
            # 주중과 주말의 패턴을 구분해서 리스트의 형태로 flatten 시킴.
            action_time = self.from_date
            while action_time <= self.to_date:
                action_de = action_time.weekday()
                if action_de < 5:
                    for s_hour, s_min, f_hour, f_min, action, trial, max_stream_time, _  in weekday_user_pattern:
                        action_time = datetime(action_time.year, action_time.month,
                                                action_time.day, s_hour, s_min)
                        finish_time = datetime(action_time.year, action_time.month,
                                                action_time.day, f_hour, f_min)                                                
                        all_user_pattern.append([action_time, finish_time, action, trial, max_stream_time])
                    action_time += timedelta(days=1)
                else:
                    for s_hour, s_min, f_hour, f_min, action, trial, max_stream_time, _   in weekend_user_pattern:
                        action_time = datetime(action_time.year, action_time.month,
                                                action_time.day, s_hour, s_min)
                        finish_time = datetime(action_time.year, action_time.month,
                                                action_time.day, f_hour, f_min)    
                        all_user_pattern.append([action_time, finish_time, action, trial, max_stream_time])
                    action_time += timedelta(days=1)
        # all_user_pattern : home에 입력된 user들의 주어진 기간에 대한 모든 행동의 리스트
        print("User pattern Making finish")

        # Device의 기능별 기본 단위 패킷을 생성
        print("Device standard packet Making start")
        device_packet_dict = {}
        in_home_device_set = self.selected_device_dict
        all_packet_list = []
        print("Common / Streaming Task Start")
        

        # 패킷 생성 메인 함수.
        def device_make_packet(max_stream_time): # max_stream_time의 경우 스트리밍 서비스를 구현하기 위해 받음.
            for device_name in in_home_device_set: # 개별 device에 대해서 세부 패킷을 제너레이팅
                Device_Mac = in_home_device_set[device_name]["MAC_Addr"]
                Device_Server_PortRange = in_home_device_set[device_name]["Device_PortRange"]
                Device_port = int(np.random.choice(Device_Server_PortRange))
                for function_name in in_home_device_set[device_name]:
                    if function_name not in ['Device IP','Device_PortRange','MAC_Addr']:
                        # Common, DDOS : 주어진 시간에 정해진 동작을 단일 처리.
                        # Streaming : 주어진 시간에 업로드와 다운로드를 지속적으로 반복.
                        if in_home_device_set[device_name][function_name]["Task"] in ["Common","DDOS"]:
                            # DDOS packet 만드는 구간
                            if in_home_device_set[device_name][function_name]["Task"] == "DDOS":
                                try_thred = np.random.normal(0,1)
                                try:
                                    standard_packet_list = []
                                    if abs(try_thred) > 4:
                                        for i, each_session in enumerate(in_home_device_set[device_name][function_name]['Session']['Stage']):
                                            fs = in_home_device_set[device_name][function_name]['Session'][each_session]
                                            attack_server_ip = change_to_ip(fs['Attack_Server'])
                                            attack_server_port = np.random.choice(range(fs['Attack_PortRange'][0],fs['Attack_PortRange'][1]),size = 1)[0]
                                            attack_client_port_range = list(range(fs["Client_PortRange"][0],fs["Client_PortRange"][1]))
                                            random.shuffle(attack_client_port_range)
                                            time_change = [float(np.random.uniform(i,i*1.2,1)) for i in fs['working_time']]
                                            for each_port in attack_client_port_range:
                                                standard_packet_list += make_function(device_name, function_name, Device_Mac, each_port, 
                                                                attack_server_ip, attack_server_port, fs['UPDN'], fs['Protocol'],time_change, fs['packet'])
                                except:
                                    print("{} has no stage".format[function_name])
                                device_packet_dict[function_name] = standard_packet_list

                            # Common packet 만드는 구간
                            elif in_home_device_set[device_name][function_name]["Task"] == "Common":
                                standard_packet_list = []
                                try:
                                    for i, each_session in enumerate(in_home_device_set[device_name][function_name]['Session']['Stage']):
                                        fs = in_home_device_set[device_name][function_name]['Session'][each_session]
                                        try:
                                            # 클라이언트가 특정 포트로 통신을 받아야 되는 경우 사용.
                                            # 홈 카메라의 경우 9010번 포트로만 통신을 함.(일종의 서버로 사용되기 때문)
                                            srcport = np.random.choice(range(fs["Client_specific_port"][0],fs["Client_specific_port"][1]),size=10)
                                        except:
                                            # 클라이언트 포트 중 특정 포트가 선택되지 않을 경우 클라이언트 쪽에서 아무 포트나 사용함.
                                            # self.PORT_RANGE -> 홈에 디폴트로 설정된 port range [0,65535]
                                            srcport = np.random.choice(range(self.PORT_RANGE[0],self.PORT_RANGE[1]),size = 1000)

                                        dst_ip = change_to_ip(fs['Server'])
                                        dstport = np.random.choice(range(fs['Server_PortRange'][0],fs['Server_PortRange'][1]),size = 1000)
                                        time_change = [float(np.random.uniform(i,i*1.2,1)) for i in fs['working_time']]
                                        standard_packet_list += make_function(device_name, function_name, Device_Mac, srcport[i], 
                                                            dst_ip, dstport[i], fs['UPDN'], fs['Protocol'],time_change, fs['packet'])
                                except:
                                    print("{} has no stage".format[function_name])
                                device_packet_dict[function_name] = standard_packet_list

                        # Streaming 패킷 생성 부분
                        # max_stream_time -> 스트리밍 서비스 구현시 최대 재생시간을 조정해야 다운로드 받고 대기하는 시간 계산가능
                        elif (in_home_device_set[device_name][function_name]["Task"] == "Streaming") and (max_stream_time>0):
                            standard_packet_list = []
                            try:
                                for i, each_session in enumerate(in_home_device_set[device_name][function_name]['Session']['Stage']):
                                    # 'Stage'안에 스트리밍 서비스의 세션 커넥트 과정이 설명되어있음. 그 순서대로 패킷을 생성 
                                    # 스트리밍 다운로드를 실행하기 전 패킷
                                    if each_session != "Streaming":
                                        fs = in_home_device_set[device_name][function_name]['Session'][each_session]
                                        try:
                                            srcport = np.random.choice(range(fs["Client_specific_port"][0],fs["Client_specific_port"][1]),size=1)[0] # 특정 포트 선택
                                        except:
                                            srcport = np.random.choice(range(self.PORT_RANGE[0],self.PORT_RANGE[1]),size = 1)[0] # 아무거나 선택
                                        dst_ip = change_to_ip(fs['Server'])
                                        dstport = np.random.choice(range(fs['Server_PortRange'][0],fs['Server_PortRange'][1]),size = 1)[0]
                                        
                                        new_task = make_function(device_name, function_name ,Device_Mac, srcport, 
                                                            dst_ip, dstport, fs['UPDN'],fs['Protocol'], fs['working_time'], fs['packet'])
                                        standard_packet_list += new_task
                                    # 스트리밍 다운로드를 하는 패킷
                                    elif each_session == 'Streaming':
                                        stream_packet_list = []
                                        fs = in_home_device_set[device_name][function_name]['Session'][each_session]
                                        # 곡 종료 후 대기 상황을 만들어 주기 위해 config에 일시적으로 추가하는 패킷 -> 마지막에 패킷크기가 0인것은 삭제되므로 
                                        # 이때 만들어 진 패킷은 삭제됨.
                                        fs['working_time'].append(1)
                                        fs['UPDN'].append("UP")
                                        fs['Protocol'].append("TCP")
                                        fs['packet'].append(0)
                                        try:
                                            srcport = np.random.choice(range(fs["Client_specific_port"][0],fs["Client_specific_port"][1]),size=1)[0]
                                        except:    
                                            srcport = np.random.choice(range(self.PORT_RANGE[0],self.PORT_RANGE[1]),size = 1)[0]
                                        
                                        dstport = np.random.choice(range(fs['Server_PortRange'][0],fs['Server_PortRange'][1]),size = 1)[0]
                                        # 평균 곡 재생시간 설정. - 난수 생성
                                        song_play_seconds = int(fs['standard_trial_time_min']*60) + int(random.uniform(-10, 70))
                                        # 총 재생시간 설정
                                        max_playing_seconds = int(max_stream_time*60) + int(random.uniform(-0.1*max_stream_time*60,0.1*max_stream_time*60))
                                        # 총 재생시간 대비 재생 가는 곡 수 계산
                                        N_of_playing = int(max_playing_seconds/song_play_seconds)
                                        # 개별 곡에 대한 재생시간 저장
                                        song_play_time_list = []
                                        for _ in range(N_of_playing):
                                            if fs['standard_trial_time_min'] == 1:
                                                _s_time = 60
                                            else:
                                                _s_time = np.random.normal(song_play_seconds,0.3)
                                            song_play_time_list.append(int(_s_time))
                                        #개별 곡의 재생시간들의 합이 총 재생 시간을 넘지 않도록 song_play_time_list에 저장
                                        all_playing = 0
                                        for k, song_time in enumerate(song_play_time_list):
                                            all_playing += song_time
                                            if all_playing >= max_playing_seconds:
                                                song_play_time_list = song_play_time_list[:k+1]
                                                break
                                        
                                        dst_ip = change_to_ip(fs['Server'])
                                        # print(song_play_time_list)

                                        for song_play_time in song_play_time_list:                                           
                                            if song_play_time >= 60:
                                                fs['working_time'][2] = song_play_time - (fs['working_time'][0]+fs['working_time'][1])
                                                new_task = make_function(device_name, function_name, Device_Mac, srcport,
                                                                    dst_ip, dstport, fs['UPDN'], fs['Protocol'],fs['working_time'], fs['packet'])

                                            stream_packet_list += new_task
                                        fs['working_time'].pop()
                                        fs['UPDN'].pop()
                                        fs['Protocol'].pop()
                                        fs['packet'].pop()
                                        standard_packet_list += stream_packet_list
                            except:
                                traceback.print_exc()
                            device_packet_dict[function_name] = standard_packet_list
            return device_packet_dict            
        
        # 사용자 정의에 의한 패킷 제너레이팅
        for s_time, f_time, work, max_trials, max_stream_time in all_user_pattern:
            try:
                work = re.sub("[_]+[0-9]","",work) # 중복 작업을 위한 뒷부분에 숫자 붙인 버전.
                # device_make_packet(max_stream_time)[work] -> 개별 작업에 대한 기본 패킷 단위
                made_packet = time_plus_packet(s_time, f_time, device_make_packet(max_stream_time)[work], max_trials, self.Network_speed)
                all_packet_list.append(made_packet)
            except:
                traceback.print_exc()

        print("Common / Streaming Task Finish")
        print("Repeatedly Task Start")
        
        # 사용자가 정의하지 않고 반복하는 패킷 생성 ex)펌웨어 업데이트 확인.
        # 반복작업에 대한 패킷 생성 : itertime_action 메서드 사용
        for device_name in in_home_device_set:
            Device_MAC = in_home_device_set[device_name]["MAC_Addr"] 
            Device_Server_PortRange = in_home_device_set[device_name]["Device_PortRange"]
            Device_port = int(np.random.choice(Device_Server_PortRange))
            for function_name in in_home_device_set[device_name]:
                if function_name not in ['Device IP','Device_PortRange',"MAC_Addr"]:
                    if in_home_device_set[device_name][function_name]["Task"] == "Repeatedly":
                        repeat_work = in_home_device_set[device_name][function_name]["Session"]
                        try:
                            for each_session in repeat_work["Stage"]:
                                fs = repeat_work[each_session]
                                dst_ip = change_to_ip(fs['Server'])
                                firmware_packet = make_function(device_name, function_name, Device_MAC, Device_Server_PortRange, 
                                                                dst_ip, fs['Server_PortRange'], 
                                                                fs['UPDN'], fs['Protocol'], fs['working_time'], fs['packet'])
                                interval_time = fs['interval1']
                                interval_key = fs['interval2']
                                all_packet_list += itertime_action(from_date, to_date,
                                                                interval_time, interval_key,
                                                                firmware_packet, fs['packet'], device_name, function_name, self.Network_speed)
                        except:
                            traceback.print_exc()
                            print("error")
                    elif in_home_device_set[device_name][function_name]["Task"] == "Port_scan":
                        repeat_work = in_home_device_set[device_name][function_name]["Session"]
                        try:
                            for each_session in repeat_work["Stage"]:
                                fs = repeat_work[each_session]
                                dst_ip = change_to_ip(fs['Attack_Server'])
                                client_port_range = np.random.choice(range(fs['Client_PortRange'][0],fs['Client_PortRange'][1]),size = fs['Attack_number'])
                                port_packet = make_function(device_name, function_name,  dst_ip, fs['Attack_PortRange'], 
                                            Device_MAC, client_port_range, fs['UPDN'], fs['Protocol'], fs['working_time'], fs['packet'])
                                attack_trial = fs['max_attack_trial']
                                all_packet_list += itertime_action(from_date, to_date, 
                                                                attack_trial, "seconds",
                                                                port_packet, fs['packet'], device_name, "Port_scan", self.Network_speed)
                        except:
                            traceback.print_exc()
        print("Repeatedly Task Finish")

        flattened_packet_list = []
        #flatten the list
        for x in all_packet_list:
            for y in x:
                flattened_packet_list.append(y)

        return flattened_packet_list
    
def home_set():
    Home_class_list = []
    Home_packet_dict = {}
    Home_date_list = []
    try:
        with open('./Config/HomeConfig.json','r') as f:
            home_config = json.load(f)
    except:
        print("HomeConfig error")
    for k1 in home_config:
        Home_name = k1
        print("-----------Start {}-----------".format(Home_name))
        IP = home_config[k1]['IP']
        PORT_RANGE = [0,65536]
        for _date in ['from_date','to_date']:
            a,b,c,d,e,f = home_config[k1][_date].split(",")
            a,b,c,d,e,f = int(a),int(b),int(c),int(d),int(e),int(f)
            if _date == 'from_date':
                from_date = datetime(a,b,c,d,e,f)
            elif _date == 'to_date':
                to_date = datetime(a,b,c,d,e,f)
        Home_date_list.append([from_date, to_date])
        Device_list = home_config[k1]['Devices']
        User_list = home_config[k1]['User_setting']
        Network_speed = home_config[k1]['Network_speed_per_sec']
        # packet make
        make_home = Home(Home_name, IP, PORT_RANGE, Network_speed)
        make_home.device_setting(Device_list)
        make_home.user_setting(User_list)
        Home_class_list.append(make_home)
        Home_packet_dict[make_home.Home_name] = make_home.packet_generate(from_date, to_date)

        print("-----------finish {}-----------".format(Home_name))
        print("기기 IP : ",IP_list) # 개별 기기들의 ip
        print("기기 MAC : ",mac_list) # 개별 기기들의 mac
        print("기기 업데이트 이력 : ",device_firmware_update_dict) # firmware update 기록
    return Home_class_list, Home_packet_dict, Home_date_list


if __name__ == "__main__":
    outdir = './PacketGen'
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    # Read Configurations
    # 개별 home에 대한 패킷 생성
    home_list, home_packet_dict, Home_date_list = home_set() 
    # 저장을 위한 후처리
    for i, each_home in enumerate(home_list):
        home_name = each_home.Home_name
        df = pd.DataFrame(home_packet_dict[home_name], 
            columns = ['Time','SrcIP',"SrcPort","DstIP","DstPort","Protocol","PacketSIZE", "Session_id","vendor","service_name"])
        df = df.sort_values(by = 'Time')
        from_date = Home_date_list[i][0]
        to_date = Home_date_list[i][1]
        df = df[pd.to_datetime(df['Time'])<=to_date]
        def update_version(_list):
            input_Time = _list[0]
            vendor = _list[1]
            try:
                update_time = pd.Series(device_firmware_update_dict[vendor])
                new = update_time[update_time<input_Time]
            except:
                new = []
            if len(new) >= 1:
                version = new.index.values.max()
            else:
                version = 0
            return version
        df['version'] = df[['Time','vendor']].apply(update_version, axis = 1)
        df = df[df.PacketSIZE>0]
        df['PacketSIZE'] = df['PacketSIZE'].apply(math.ceil)
        outname = "{}.log".format(home_name)
        fullname = os.path.join(outdir, outname)   
        df.to_csv(fullname,index=False)
    
        
    
