"""
This script plots the PDR per channel.

Usage example:
  $ python pdr_per_channel.py grenoble 2017.06.20-16.22.14
"""

import os
import argparse
import logging

import matplotlib.pyplot as plt
import k7

# ============================== logging ======================================

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# ============================== defines ======================================

OUT_PATH = "../results"

# ============================== main =========================================

# parsing user arguments
parser = argparse.ArgumentParser()
parser.add_argument("dataset", help="The path to the dataset", type=str)
args = parser.parse_args()

# load the dataset
file_name = os.path.basename(args.dataset)
header, df = k7.read(args.dataset)
logging.info("Dataset loaded.")

df_grouped = df.groupby(df.channel).pdr.mean()
plt.bar([int(i) for i in df_grouped.index], df_grouped.values)

# plot
plt.rcParams.update({'font.size': 14})
plt.xlabel('IEEE802.15.4 Channel')
plt.ylabel('PDR (%)')
plt.xlim([10, 27])
plt.ylim([0.4, 1.1])
plt.xticks([t for t in range(11,27)])
plt.tight_layout()
plt.grid(True)

path = "{0}/{1}".format(OUT_PATH, header['site'])
if not os.path.exists(path):
    os.makedirs(path)
plt.savefig("{0}/pdr_per_channel_{1}.png".format(path, header['site']),
            format='png', bbox_inches='tight', pad_inches=0)
plt.show()
