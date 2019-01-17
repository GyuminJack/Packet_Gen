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

def user_setting():
    def make_user_list():
        try:
            with open('./Config/UserConfig.json','r') as f:
                user_config = json.load(f)
        except:
            print("UserConfig error")
        all_user_dict = user_config
        all_user = []
        for k in all_user_dict:
            if k in custom_user_list:
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
    user_list = make_user_list()
    return user_list

if __name__ == "__main__":
    print(user_setting())