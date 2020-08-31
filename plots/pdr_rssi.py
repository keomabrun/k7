"""
This script plots the PDR over average RSSI.
The PDR is calculated over all the channel for each link.
This plot is better known as the Waterfall plot.

Usage example:
  $ python pdr_rssi.py grenoble 2017.06.20-16.22.15
"""

import argparse
import DatasetHelper
import matplotlib.pyplot as plt
import os

plt.rcParams.update({'font.size': 14})
# ============================== defines ======================================

RAW_PATH = "../processed"
OUT_PATH = "../results"

# ============================== main =========================================

# parsing user arguments
parser = argparse.ArgumentParser()
parser.add_argument("dataset", help="The path to the dataset", type=str)
args = parser.parse_args()

# load the dataset
file_name = os.path.basename(args.dataset)
header, df = DatasetHelper.load_dataset(args.dataset)

#df_link = df.dropna().groupby(["src", "dst", "transaction_id"]).mean().reset_index()
df_link = df

# compute error bar
df_grouped = df_link.groupby(df_link["mean_rssi"].apply(lambda x: round(x)))
mean_index = [name for name, group in df_grouped if len(group) > 10]
mean_pdr = [group.pdr.mean() for name, group in df_grouped if len(group) > 10]
std_pdr = [group.pdr.std() for name, group in df_grouped if len(group) > 10]

# plot
plt.plot(df_link.mean_rssi, df_link.pdr, '+', zorder=0)
plt.errorbar(mean_index, mean_pdr, std_pdr)

plt.xlabel('RSSI average (dBm)')
plt.ylabel('PDR (%)')
plt.xlim([-95, -15])
plt.ylim([0, 1.1])
plt.tight_layout()
plt.grid(True)

plt.savefig("{0}/{1}/pdr_rssi_{2}.png".format(OUT_PATH, header['site'], file_name),
            format='png', bbox_inches='tight', pad_inches=0)
plt.show()

