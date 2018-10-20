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

file_name = "../PacketGen/Home1.log"
log_data = pd.read_csv(file_name, index_col=0, parse_dates=True)

print(log_data.head())