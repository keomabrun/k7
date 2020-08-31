"""
This script plots the PDR over time per channel.

Usage example:
  $ python pdr_time_per_channel.py grenoble 2017.06.20-16.22.15
"""

import os
import argparse
import logging

import matplotlib.pyplot as plt
import matplotlib.dates as md
import pandas as pd

import k7

# ============================== defines ======================================

OUT_PATH = "../results"

# ============================== main =========================================

def main(args):
    # load the dataset
    header, df = k7.read(args.dataset)
    df.fillna(-1, inplace=True)
    logging.info("Dataset loaded.")

    color_list = ["blue", "red"]
    plt.rcParams.update({'font.size': 14})

    for link, df_link in df.groupby(["src", "dst"]):
        fig_num = len(df.channel.unique())
        fig, axs = plt.subplots(fig_num, 1, sharex=True)
        axs2 = {}
        fig.set_size_inches(7, 5)
        xfmt = md.DateFormatter('%y-%m-%d')
        index = fig_num - 1

        for freq, df_freq in df_link.groupby("channel"):
            # plot PDR
            axs[index].plot(df_freq.index, df_freq.pdr/100, '-', zorder=2, markersize=1.2,
                            color=color_list[freq%len(color_list)])

            # y axis
            axs[index].set_yticks([])
            axs[index].set_ylim(-0.2, 1.2)
            axs[index].set_ylabel(freq, rotation=0)
            axs[index].yaxis.set_label_coords(-0.03, -0.02)

            # y axix right
            ratio_available = int(100 * len(df_freq[df_freq.pdr > 0.5]) /
                                  float(len(df_freq.pdr)))
            axs2[index] = axs[index].twinx()
            axs2[index].set_yticks([])
            axs2[index].set_ylabel('{0}%'.format(ratio_available), rotation=0)
            axs2[index].yaxis.set_label_coords(1.06, 1)

            # x axis
            axs[index].xaxis_date()
            axs[index].xaxis.set_major_formatter(xfmt)
            plt.gcf().autofmt_xdate()
            axs[index].set_xticks(axs[index].get_xticks()[::2])  # divide number of ticks by 2

            # misc
            axs[index].grid(color='gray', linewidth=0.3, axis='y')

            # plot day/night background color
            for day, df_day in df.groupby(pd.Grouper(freq="1d")):
                day_start = day + pd.DateOffset(hours=9)
                day_stop = day + pd.DateOffset(hours=18)
                axs[index].fill_between(
                    [max(day_start, df.index.min()), min(day_stop,df.index.max())],
                    0, 30, color='#d5dbdb', alpha=0.5, zorder=1)

        index -= 1

    plt.xlabel('Time')
    fig.text(0.06, 0.85, 'PDR (%) per IEEE802.15.4 Channel', ha='center', rotation='vertical')

    path = "{0}/{1}".format(OUT_PATH, header['site'])
    if not os.path.exists(path):
        os.makedirs(path)
    plt.savefig("{0}/pdr_time_per_channel_{1}_{2}.png".format(path, header['site'], link),
                format='png', bbox_inches='tight', pad_inches=0)
    plt.clf()

if __name__ == "__main__":
    # parsing user arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", help="The path to the dataset", type=str)
    args = parser.parse_args()

    main(args)
