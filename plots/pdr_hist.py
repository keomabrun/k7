"""
This script plots the PDR distribution. The PDR is calculated per link, over all channels.

Usage example:
  $ python pdr_hist.py grenoble 2017.06.20-16.22.14
"""

import argparse
import DatasetHelper
import matplotlib.pyplot as plt
import os

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
df, header = DatasetHelper.load_dataset(args.dataset)
print df.head()

df_pdr = df.groupby([df.src, df.dst, df.transaction_id]).pdr.mean()

# plot
plt.hist(df.pdr.dropna(), bins=[i*5 for i in range(0, 21)])

plt.rcParams.update({'font.size': 14})
plt.xlabel('PDR (%)')
plt.ylabel('number of PDR measurements')
plt.xlim([0, 1])
plt.tight_layout()
plt.grid(True)

path = "{0}/{1}".format(OUT_PATH, header['site'])
if not os.path.exists(path):
    os.makedirs(path)
plt.savefig("{0}/pdr_hist_{1}.png".format(path, header['site']),
            format='png', bbox_inches='tight', pad_inches=0)
plt.show()