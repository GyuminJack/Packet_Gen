from Devices_v2 import *
import json
import re
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
IP_range = [i for i in range(1,256)]
home_Port_range = [i for i in range(1,65535)]

class Home():
    def __init__(self, HOME_NAME, IP, PORT_RANGE):
        self.Home_name = HOME_NAME
        self.IP = IP
        global IP_range
        self.PORT_RANGE = PORT_RANGE

    # 개별 Device들의 설정정보를 불러오고 IP / Port 설정
    def device_setting(self, device_list):
        try:
            with open('DeviceConfig.1.json','r') as f:
                config = json.load(f)
        except:
            print("DeviceConfig error")
        self.all_device_dict = config
        self.selected_device_dict = {}
        for k in self.all_device_dict:
            if k in device_list:
                self.selected_device_dict[k] = copy.deepcopy(self.all_device_dict[k])
                selected_device_ip = int(np.random.choice(IP_range))
                self.selected_device_dict[k]["Device IP"] = self.IP + "." + str(selected_device_ip)
                self.selected_device_dict[k]["Device Portrange"] = [0,65535]
                IP_range.remove(selected_device_ip)

    # 개별 User를 불러오고 해당 유저의 패턴을 생성
    def user_setting(self,costum_user_list):
        def make_user_list():
            try:
                with open('UserConfig_1.json','r') as f:
                    self.user_config = json.load(f)
            except:
                print("UserConfig error")
            all_user_dict = self.user_config
            all_user = []
            for k in all_user_dict:
                if k in costum_user_list:
                    user_config = user_type()
                    for _dayend in all_user_dict[k]:
                        action_root = all_user_dict[k][_dayend]
                        for key in action_root:
                            action_start = action_root[key]['start_time']
                            action_finish = action_root[key]['finish_time']
                            action_max_trial = action_root[key]['max_trial']
                            try:
                                action_stream_time = action_root[key]['max_stream_time']
                            except:
                                action_stream_time = 0
                            action = key
                            user_config.action_add(action_start, action_finish, action, action_max_trial, action_stream_time, _dayend)
                    all_user.append(user_config)
            return all_user
        self.user_list = make_user_list()

    # 유저정보와 기기정보를 합하여 패킷을 생성
    def packet_generate(self, from_date, to_date):
        self.from_date = from_date
        self.to_date = to_date
        self.time_gap = to_date - from_date
        # make all day routine
        print("User pattern Making start")
        user_action_making = []
        for i, user in enumerate(self.user_list):
            # print(user)
            weekday_user_pattern = []
            weekend_user_pattern = []
            for _action_list in user.time_action:
                if _action_list[-1] == 'weekday':
                    weekday_user_pattern.append(_action_list)
                else:
                    weekend_user_pattern.append(_action_list)

            action_time = self.from_date
            while action_time <= self.to_date:
                action_de = action_time.weekday()
                if action_de < 5:
                    for s_hour, s_min, f_hour, f_min, action, trial, max_stream_time, _  in weekday_user_pattern:
                        action_time = datetime(action_time.year, action_time.month,
                                                action_time.day, s_hour, s_min)
                        finish_time = datetime(action_time.year, action_time.month,
                                                action_time.day, f_hour, f_min)                                                
                        user_action_making.append([action_time, finish_time, action, trial, max_stream_time])
                    action_time += timedelta(days=1)
                else:
                    for s_hour, s_min, f_hour, f_min, action, trial, max_stream_time, _   in weekend_user_pattern:
                        action_time = datetime(action_time.year, action_time.month,
                                                action_time.day, s_hour, s_min)
                        finish_time = datetime(action_time.year, action_time.month,
                                                action_time.day, f_hour, f_min)    
                        user_action_making.append([action_time, finish_time, action, trial, max_stream_time])
                    action_time += timedelta(days=1)
        all_user_pattern = user_action_making
        print("User pattern Making finish")

        # Device의 기능별 기본 단위 패킷을 생성
        print("Device standard packet Making start")
        device_packet_dict = {}
        in_home_device_set = self.selected_device_dict
        all_packet_list = []
        print("Common / Streaming Task Start")

        def device_make_packet(max_stream_time):
            for device_name in self.selected_device_dict:
                Device_IP = self.selected_device_dict[device_name]["Device IP"]
                Device_Portrange = self.selected_device_dict[device_name]["Device Portrange"]
                Device_port = int(np.random.choice(Device_Portrange))
                for function_name in self.selected_device_dict[device_name]:
                    if function_name not in ['Device IP','Device Portrange']:
                        if self.selected_device_dict[device_name][function_name]["Task"] == "Common":
                            standard_packet_list = [] 
                            try:
                                for i, each_session in enumerate(self.selected_device_dict[device_name][function_name]['Sessions']['Routine']):
                                    fs = self.selected_device_dict[device_name][function_name]['Sessions'][each_session]
                                    srcport = np.random.randint(self.PORT_RANGE[0],self.PORT_RANGE[1],size = 1000)
                                    dstport = np.random.randint(fs['PortRange'][0],fs['PortRange'][1],size = 1000)
                                    new_task = make_function(device_name, Device_IP, srcport[i], 
                                                        # Common Task의 IP세팅이 C class 라고 판단하는 부분
                                                        fs['Server']+str(np.random.randint(0,256)), 
                                                        dstport[i], fs['UPDN'], fs['time'], fs['packet'])
                                    standard_packet_list += new_task
                            except:
                                print("{} has no Routine".format[function_name])
                            device_packet_dict[function_name] = standard_packet_list

                        elif (self.selected_device_dict[device_name][function_name]["Task"] == "Streaming") and (max_stream_time>0):
                            standard_packet_list = []
                            try:
                                for i, each_session in enumerate(self.selected_device_dict[device_name][function_name]['Sessions']['Routine']):
                                    # 스트리밍 다운로드를 실행하기 전 패킷
                                    if each_session != "Streaming":
                                        fs = self.selected_device_dict[device_name][function_name]['Sessions'][each_session]
                                        srcport = np.random.randint(self.PORT_RANGE[0],self.PORT_RANGE[1],size = 1000)
                                        dstport = np.random.randint(fs['PortRange'][0],fs['PortRange'][1],size = 1000)
                                        new_task = make_function(device_name, Device_IP, srcport[i], 
                                                            # Streaming Task의 IP세팅이 C class 라고 판단하는 부분
                                                            fs['Server']+str(np.random.randint(0,256)), 
                                                            dstport[i], fs['UPDN'], fs['time'], fs['packet'])
                                        standard_packet_list += new_task
                                    # 스트리밍 다운로드를 하는 패킷
                                    elif each_session == 'Streaming':
                                        
                                        stream_packet_list = []
                                        fs = self.selected_device_dict[device_name][function_name]['Sessions'][each_session]
                                        #곡 종료 후 대기 상황
                                        fs['time'].append(1)
                                        fs['UPDN'].append("UP")
                                        fs['packet'].append(0)
                                        srcport = list(np.random.randint(self.PORT_RANGE[0],self.PORT_RANGE[1],size = 1))[0]
                                        dstport = list(np.random.randint(fs['PortRange'][0],fs['PortRange'][1],size = 1))[0]
                                        song_play_seconds = int(np.random.normal(fs['Song_play_minutes']*60,25))
                                        max_playing_seconds = int(np.random.normal(max_stream_time*60,10))
                                        
                                        N_of_playing = int(max_playing_seconds/song_play_seconds)
                                        song_play_time_list = [int(j) for j in np.random.normal(song_play_seconds,25,size = N_of_playing)]

                                        all_playing = 0
                                        for k, song_time in enumerate(song_play_time_list):
                                            all_playing += song_time
                                            if all_playing > max_playing_seconds:
                                                song_play_time_list = song_play_time_list[:k+1]
                                                break

                                        # 특정 서버에서 작업이 된다면 D-class로 수정 필요
                                        ip_last = str(np.random.randint(0,256)) 

                                        for song_play_time in song_play_time_list:                                           
                                            if song_play_time > 60:
                                                fs['time'][2] = song_play_time - (fs['time'][0]+fs['time'][1])
                                                new_task = make_function(device_name, Device_IP, srcport,
                                                                    # Streaming Task의 IP세팅이 C class 라고 판단하는 부분
                                                                    fs['Server']+ip_last,
                                                                    dstport, fs['UPDN'], fs['time'], fs['packet'])
                                            stream_packet_list += new_task
                                        standard_packet_list += stream_packet_list
                            except:
                                pass
                            device_packet_dict[function_name] = standard_packet_list
                            # pprint(device_packet_dict['s_music_stream'])
            return device_packet_dict            
        
        for s_time, f_time, work, max_trials, max_stream_time in all_user_pattern:
            try:
                work = re.sub("[_]+[0-9]","",work)
            except:
                pass
            try:
                made_packet = time_plus_packet(s_time, f_time, device_make_packet(max_stream_time)[work], max_trials)
                all_packet_list.append(made_packet)
            except:
                pass
        print("Common / Streaming Task Finish")
        print("Repeatly Task Start")
        # 반복작업에 대한 패킷 생성 : itertime_action 메서드 사용
        for device_name in self.selected_device_dict:
            Device_IP = self.selected_device_dict[device_name]["Device IP"] 
            Device_Portrange = self.selected_device_dict[device_name]["Device Portrange"]
            Device_port = int(np.random.choice(Device_Portrange))
            for function_name in in_home_device_set[device_name]:
                if function_name not in ['Device IP','Device Portrange']:
                    if in_home_device_set[device_name][function_name]["Task"] == "Repeatly":
                        repeat_work = in_home_device_set[device_name][function_name]["Sessions"]
                        try:
                            for each_session in repeat_work["Routine"]:
                                session = repeat_work[each_session]
                                firmware_packet = make_function(device_name, Device_IP, Device_Portrange, 
                                                                #반복 작업의 경우 서버는 D class
                                                                session['Server'], session['PortRange'], 
                                                                session['UPDN'], session['time'], session['packet'])
                                interval_time = session['interval1']
                                interval_key = session['interval2']
                                firmware_packet = itertime_action(from_date, to_date,
                                                                interval_time, interval_key,
                                                                firmware_packet, session['packet'])
                                all_packet_list += firmware_packet
                        except:
                            print("error")
        print("Repeatly Task Finish")
        return all_packet_list
    
def home_set():
    Home_class_list = []
    Home_packet_dict = {}
    try:
        with open('HomeConfig.json','r') as f:
            home_config = json.load(f)
    except:
        print("HomeConfig error")
    for k1 in home_config:
        Home_name = k1
        print("-----------Start {}-----------".format(Home_name))
        IP = home_config[k1]['IP']
        #사실상 사용되지 않음.
        PortRange = [0,65536]
        for _date in ['from_date','to_date']:
            a,b,c,d,e,f = home_config[k1][_date].split(",")
            a,b,c,d,e,f = int(a),int(b),int(c),int(d),int(e),int(f)
            if _date == 'from_date':
                from_date = datetime(a,b,c,d,e,f)
            elif _date == 'to_date':
                to_date = datetime(a,b,c,d,e,f)
        Device_list = home_config[k1]['Devices']
        User_list = home_config[k1]['User_setting']
        make_home = Home(Home_name,IP,PortRange)
        make_home.device_setting(Device_list)
        make_home.user_setting(User_list)
        Home_class_list.append(make_home)
        Home_packet_dict[make_home.Home_name] = sum(make_home.packet_generate(from_date, to_date),[])
        print("-----------finish {}-----------".format(Home_name))
    return Home_class_list, Home_packet_dict



if __name__ == "__main__":
    import pandas as pd
    home_list, home_packet_dict = home_set()
    for each_home in home_list:
        home_name = each_home.Home_name
        df = pd.DataFrame(home_packet_dict[home_name], 
            columns = ['Time','SrcIP',"SrcPort","DstIP","DstPort","PacketSIZE", "Session_id","vendor"])
        df = df.sort_values(by = 'Time')
        df = df[df.PacketSIZE>0]
        df.to_csv("{}.log".format(home_name),index=False)
        
    
 
