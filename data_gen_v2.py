from Devices_v2 import *
import json
class user_type:
    def __init__(self):
        self.time_action = []
    def action_add(self,time_H,time_M,action,action_trial,day_end):
        mean_time = time_H*24 + time_M
        std = 5^2
        _g_sample = np.round(np.random.normal(0, std, 1))
        g_time_H = int((mean_time +_g_sample)/24)
        g_time_M = (mean_time +_g_sample) - 24*g_time_H
        self.time_action.append([g_time_H,g_time_M,action,action_trial,day_end])
    def time_action(self):
        return self.time_action

class Home():
    def __init__(self, HOME_NAME, IP, PORT_RANGE):
        self.Home_name = HOME_NAME
        self.IP = IP
        self.PORT_RANGE = PORT_RANGE

    # def date_setting(self, today_time):
    #     self.today_time = today_time

    def device_setting(self, device_list):
        with open('DeviceConfig.json','r') as f:
            config = json.load(f)
        self.all_device_dict = config
        self.selected_device_dict = {}
        for k in self.all_device_dict:
            if k in device_list:
                self.selected_device_dict[k] = self.all_device_dict[k]


    def user_setting(self,costum_user_list):
        def make_user_list():
            with open('UserConfig.json','r') as f:
                self.user_config = json.load(f)
            all_user_dict = self.user_config
            all_user = []
            for k in all_user_dict:
                if k in costum_user_list:
                    user_config = user_type()
                    for _dayend in all_user_dict[k]:
                        action_root = all_user_dict[k][_dayend]
                        for key in action_root:
                            action_H = action_root[key]['Hour']
                            action_M = action_root[key]['Min']
                            action_trial = action_root[key]['trial']
                            action = key
                            user_config.action_add(action_H, action_M, action, action_trial, _dayend)
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
            print(user)
            weekday_user_pattern = []
            weekend_user_pattern = []
            for _action_list in user.time_action:
                if _action_list[4] == 'weekday':
                    weekday_user_pattern.append(_action_list)
                else:
                    weekend_user_pattern.append(_action_list)

            action_time = self.from_date
            while action_time <= self.to_date:
                action_de = action_time.weekday()
                if action_de < 5:
                    for hour, min, action, trial, _  in weekday_user_pattern:
                        action_time = datetime(action_time.year, action_time.month,
                                                action_time.day, hour, min)
                        user_action_making.append([action_time, action, trial])
                    action_time += timedelta(days=1)
                else:
                    for hour, min, action, trial, _  in weekend_user_pattern:
                        action_time = datetime(action_time.year, action_time.month,
                                                action_time.day, hour, min)
                        user_action_making.append([action_time, action, trial])
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
        for time, work, C_trials in all_user_pattern:
            for device_name in self.selected_device_dict:
                for function_name in in_home_device_set[device_name]:
                    function = in_home_device_set[device_name][function_name]
                    srcport = np.random.randint(self.PORT_RANGE[0],self.PORT_RANGE[1],size = 1000)
                    dstport = np.random.randint(function['PortRange'][0],function['PortRange'][1],size = 1000)
                    #기본 단위의 패킷 생성
                    new_task = make_function(device_name,self.IP, srcport[i], 
                                                function['Server']+str(np.random.randint(0,256)), 
                                                dstport[i], 
                                                function['UPDN'], function['time'], function['packet'])       
                    device_packet_dict[function_name] = new_task
                    # pprint(device_packet_dict)
            try:
                made_packet = time_plus_packet(time, device_packet_dict[work], C_trials)
                all_packet_list.append(made_packet)
            except:
                pass

        # device firmware Check
        for device_name in self.selected_device_dict:
            for k in in_home_device_set[device_name]:
                if "interval1" in in_home_device_set[device_name][k]:
                    firmware_check = in_home_device_set[device_name][k]
                    firmware_packet = make_function(device_name, self.IP, self.PORT_RANGE, 
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
    with open('HomeConfig.json','r') as f:
        home_config = json.load(f)
    for k1 in home_config:
        Home_name = k1
        IP = home_config[k1]['IP']
        PortRange = home_config[k1]['PortRange']
        for _date in ['today','from_date','to_date']:
            a,b,c,d,e,f = home_config[k1][_date].split(",")
            a,b,c,d,e,f = int(a),int(b),int(c),int(d),int(e),int(f)
            if _date == 'today':
                today_time = datetime(a,b,c,d,e,f)
            elif _date == 'from_date':
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
    return Home_class_list, Home_packet_dict



if __name__ == "__main__":
    import pandas as pd
    home_list, home_packet_dict = home_set()
    for each_home in home_list:
        home_name = each_home.Home_name
        df = pd.DataFrame(home_packet_dict[home_name], columns = ['Time','SrcIP',"SrcPort","DstIP","DstPort","PacketSIZE", "Session_id","vendor"])
        df = df.sort_values(by = 'Time')
        df.to_csv("{}.log".format(home_name),index=False)

    
 
