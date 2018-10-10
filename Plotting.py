import pandas as pd
import sys

if __name__ == "__main__":
    try:
        file_name = sys.argv[1]
        out_name = sys.argv[2]
        resample_sec = int(sys.argv[3])
        data = pd.read_csv("./PacketGen/{}".format(file_name), index_col=0, parse_dates=True)
        fig1 = data["PacketSIZE"].resample("{}S".format(resample_sec)).sum().plot.line()
        fig1 = fig1.get_figure()
        fig1.savefig("./PacketGen/{}_all_packet.png".format(out_name))


        grouper = data.groupby(['vendor',pd.Grouper(freq = '{}S'.format(resample_sec))])['PacketSIZE'].sum()
        df1 = grouper.unstack(level=0)
        df1[df1.isna()]=0
        fig2 = df1.plot(kind='line',style=['r:','b:','y-'], linewidth=1.0)
        fig2 = fig2.get_figure()
        fig2.savefig("./PacketGen/{}_by_vendor.png".format(out_name))
        print("Success")
    except:
        print("Usage : python Plotting_test.py {file_name} {out_name} {resample_sec}")

    