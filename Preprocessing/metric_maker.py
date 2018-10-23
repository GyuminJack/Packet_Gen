### Using Metric
# timestamp - time of day / day of week / holiday_flag
# Mac_address - device_type / model_version
# internal port 
# external ip - country code
# external port
# direction flag
# protocol
# packet 

import pandas as pd
import datetime
file_name = "../PacketGen/Home1.log"
log_data = pd.read_csv(file_name, index_col=0, parse_dates=True)

def extract_date(str_date):
    _date = datetime.datetime(str_date)
    day_of_week = _date.weekday()
    if day_of_week >= 5:
        holiday_flag = 1
    else:
        holiday_flag = 0
    return day_of_week, holiday_flag

def extract_country(str_IP):
    pass

def direction_flag():
    pass

