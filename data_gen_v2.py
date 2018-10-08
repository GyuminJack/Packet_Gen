from Devices_v2 import *
import json
class user_type:
    def __init__(self):
        self.time_action = []
    def action_add(self,start_time,finish_time,action,max_trial,day_end):
        start_hour, start_min = int(str(start_time)[:-2]), int(str(start_time)[-2:])
        finish_hour, finish_min = int(str(finish_time)[:-2]), int(str(finish_time)[-2:])
        min_to_start = start_hour*60 + start_min
        min_to_finish = finish_hour*60 + finish_min
        select_time = int(np.random.randint(min_to_start, min_to_finish, size = 1))
        g_time_H = int(select_time/60)
        g_time_M = (select_time) - 60*g_time_H
        self.time_action.append([g_time_H,g_time_M, finish_hour, finish_min, action,max_trial,day_end])
    def time_action(self):
        return self.time_action
#c 클래스 이하 3자리를 겹치지 않게 하기 위한 메모리
IP_range = [i for i in range(1,256)]
home_Port_range = [i for i in range(1,65535)]
class Home():
    def __init__(self, HOME_NAME, IP, PORT_RANGE):
        self.Home_name = HOME_NAME
        self.IP = IP
        global IP_range
        self.PORT_RANGE = PORT_RANGE

    def device_setting(self, device_list):
        try:
            with open('DeviceConfig.json','r') as f:
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
                # 집에서 사용 되는 포트는 어떻게 규정할 것인지..
                self.selected_device_dict[k]["Device Portrange"] = [0,65535]
                IP_range.remove(selected_device_ip)
    #userconfig_setting
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
                            action = key
                            user_config.action_add(action_start, action_finish, action, action_max_trial, _dayend)
                    all_user.append(user_config)
            return all_user
        self.user_list = make_user_list()

    def packet_generate(self, from_date, to_date):
        self.from_date = from_date
        self.to_date = to_date
        self.time_gap = to_date - from_date
        # make all day routine
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
                    for s_hour, s_min, f_hour, f_min, action, trial, _  in weekday_user_pattern:
                        action_time = datetime(action_time.year, action_time.month,
                                                action_time.day, s_hour, s_min)
                        finish_time = datetime(action_time.year, action_time.month,
                                                action_time.day, f_hour, f_min)                                                
                        user_action_making.append([action_time, finish_time, action, trial])
                    action_time += timedelta(days=1)
                else:
                    for s_hour, s_min, f_hour, f_min, action, trial, _   in weekend_user_pattern:
                        action_time = datetime(action_time.year, action_time.month,
                                                action_time.day, s_hour, s_min)
                        finish_time = datetime(action_time.year, action_time.month,
                                                action_time.day, f_hour, f_min)    
                        user_action_making.append([action_time, finish_time, action, trial])
                    action_time += timedelta(days=1)

            # action_time = self.from_date
            # for _action_list in user.time_action:
            #     if action_time.weekday() < 5:
            #         user_pattern = weekday_user_pattern
            #         for hour, min, action, _  in user_pattern:
            #             action_time = datetime(action_time.year, action_time.month,
            #                                     action_time.day, hour, min)
            #             while action_time < self.to_date:
            #                 user_action_making.append([action_time,action])
            #                 action_time += timedelta(days=1)
            #     elif action_time.weekday() >= 5:
            #         user_pattern = weekend_user_pattern
            #         for hour, min, action, _  in user_pattern:
            #             action_time = datetime(action_time.year, action_time.month,
            #                                     action_time.day, hour, min)
            #             while action_time < self.to_date:
            #                 user_action_making.append([action_time,action])
            #                 action_time += timedelta(days=1)

        all_user_pattern = user_action_making


        # device에서 실행 시키기.
        device_packet_dict = {}
        in_home_device_set = self.selected_device_dict
        all_packet_list = []
        import re
        for s_time, f_time, work, max_trials in all_user_pattern:
            try:
                work = re.sub("[_]+[0-9]","",work)
            except:
                pass

            for device_name in self.selected_device_dict:
                Device_IP = self.selected_device_dict[device_name]["Device IP"]
                Device_Portrange = self.selected_device_dict[device_name]["Device Portrange"]
                Device_port = int(np.random.choice(Device_Portrange))

                for function_name in in_home_device_set[device_name]:
                    if function_name not in ['Device IP','Device Portrange']:
                        function = in_home_device_set[device_name][function_name]
                        srcport = np.random.randint(self.PORT_RANGE[0],self.PORT_RANGE[1],size = 1000)
                        dstport = np.random.randint(function['PortRange'][0],function['PortRange'][1],size = 1000)
                        #기본 단위의 패킷 생성
                        new_task = make_function(device_name, Device_IP, srcport[i], 
                                                    function['Server']+str(np.random.randint(0,256)), 
                                                    dstport[i], 
                                                    function['UPDN'], function['time'], function['packet'])
                        device_packet_dict[function_name] = new_task
                    # pprint(device_packet_dict)
            try:
                made_packet = time_plus_packet(s_time, f_time, device_packet_dict[work], max_trials)
                all_packet_list.append(made_packet)
            except:
                pass

        # device firmware Check
        for device_name in self.selected_device_dict:
            Device_IP = self.selected_device_dict[device_name]["Device IP"] 
            Device_Portrange = self.selected_device_dict[device_name]["Device Portrange"]
            Device_port = int(np.random.choice(Device_Portrange))
            for k in in_home_device_set[device_name]:
                if "interval1" in in_home_device_set[device_name][k]:
                    firmware_check = in_home_device_set[device_name][k]
                    firmware_packet = make_function(device_name, Device_IP, Device_Portrange, 
                                                    firmware_check['Server'], 
                                                    firmware_check['PortRange'], 
                                                    firmware_check['UPDN'], firmware_check['time'], firmware_check['packet'])
                    interval_time = firmware_check['interval1']
                    interval_key = firmware_check['interval2']
                    firmware_packet = itertime_action(from_date, to_date,
                                                    interval_time, interval_key,
                                                    firmware_packet, firmware_check['packet'])
                    all_packet_list += firmware_packet
        # pprint(device_packet_dict)
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
        IP = home_config[k1]['IP']
        PortRange = home_config[k1]['PortRange']
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
        print("finish {}".format(Home_name))
    return Home_class_list, Home_packet_dict



if __name__ == "__main__":
    import pandas as pd
    home_list, home_packet_dict = home_set()
    for each_home in home_list:
        home_name = each_home.Home_name
        df = pd.DataFrame(home_packet_dict[home_name], 
            columns = ['Time','SrcIP',"SrcPort","DstIP","DstPort","PacketSIZE", "Session_id","vendor"])
        df = df.sort_values(by = 'Time')
        df.to_csv("{}.log".format(home_name),index=False)
        
    
 
