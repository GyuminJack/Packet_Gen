import pandas as pd
import numpy as np
import random
import string
# macfile = "Mac_address_vendor.txt"

# mac_list = []
# with open(macfile,'rt',encoding='UTF8') as f:
#     for line in f.readlines():
#         if "(hex)" in line:
#             line = line.replace("\t","").replace("\n","")
#             base_mac = line[0:8]
#             maker = line[16:]
#             mac_list.append([base_mac,maker])
def mac_address_maker(N):
	data = pd.read_csv("MacAddr_vendor_list.txt", index_col = 0)
	data.columns = ["Mac","vendor"]
	making_number = N
	a_l = []
	for i in range(1000):
		a = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2))
		a_l.append(a)
	random_number_list = list(np.random.randint(0,1000,size=making_number))
	random_mac = list(set([data.Mac[random_number_list[i]]+"-"+"-".join(np.random.choice(a_l,3)) for i in range(making_number)]))
	return random_mac
