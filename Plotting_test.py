import pandas as pd
import sys

if __name__ == "__main__":
    try:
        file_name = sys.argv[1]
        out_name = sys.argv[2]
        resample_sec = int(sys.argv[3])
        data = pd.read_csv("{}".format(file_name), index_col=0, parse_dates=True)
        fig = data["PacketSIZE"].resample("{}S".format(resample_sec)).sum().plot.line()
        fig1 = fig.get_figure()
        fig1.savefig("{}.png".format(out_name))
        print("Success")
    except:
        print("Usage : python Plotting_test.py {file_name} {out_name} {resample_sec}")

    