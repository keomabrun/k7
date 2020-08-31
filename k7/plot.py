import os
import logging
import argparse

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md

import k7

# ========================= functions =========================================

def channel_available_hist(input_file):
    """
    This script plots histogram of the number of available channels per link.
    :param input_file:
    :return: None
    """

    # load the dataset

    header, df = k7.read(input_file)
    logging.info("Dataset loaded.")

    # filter bad links

    df_filtered = df[df.pdr > 50]
    df_filtered.fillna(0, inplace=True)

    # count number of channels available per links over time

    avail_count = []
    for link, df_link in df_filtered.groupby(["src", "dst"]):
        chan_list = df_link.groupby("transaction_id").channel.unique().str.len().tolist()
        avail_count += chan_list

    # plot data

    plt.hist(avail_count, bins=[i for i in range(0, 18)], density=True)

    # configure plot

    plt.rcParams.update({'font.size': 14})
    plt.xlabel('number of frequencies with PDR>50%')
    plt.ylabel('percentage of PDR measurements')
    plt.xlim([0, 17])
    plt.ylim([0, 1])
    plt.xticks([t for t in range(0, 17)])
    plt.grid(True)

    # save figure

    _save_fig(input_file, "channel_available_hist")

def pdr_hist(input_file):
    """
    This script plots the PDR distribution. The PDR is calculated per link, over all channels.
    :param input_file:
    :return:
    """

    # load the dataset

    header, df = k7.read(input_file)
    logging.info("Dataset loaded.")

    df_pdr = df.groupby([df.src, df.dst]).pdr.mean()

    # plot

    plt.hist(df.pdr.dropna(), bins=[i * 5 for i in range(0, 21)])

    # configure plot

    plt.rcParams.update({'font.size': 14})
    plt.xlabel('PDR (%)')
    plt.ylabel('number of PDR measurements')
    plt.xlim([0, 1])
    plt.tight_layout()
    plt.grid(True)

    # save figure

    _save_fig(input_file, "pdr_hist")

def pdr_per_channel(input_file):
    """
    This script plots the PDR per channel.
    :param input_file:
    :return:
    """
    # load the dataset

    header, df = k7.read(input_file)
    logging.info("Dataset loaded.")

    # plot data

    df_grouped = df.groupby(df.channel).pdr.mean()
    plt.bar([int(i) for i in df_grouped.index], df_grouped.values)

    # configure plot

    plt.rcParams.update({'font.size': 14})
    plt.xlabel('IEEE802.15.4 Channel')
    plt.ylabel('PDR (%)')
    plt.xlim([10, 27])
    plt.ylim([0.4, 1])
    plt.xticks([t for t in range(11, 27)])
    plt.tight_layout()
    plt.grid(True)

    # save figure

    _save_fig(input_file, "pdr_per_channel")

def pdr_rssi(input_file):
    """
    This script plots the PDR over the averaged RSSI.
    The PDR is calculated over all the channel for each link.
    This plot is better known as the Waterfall plot.
    :param input_file:
    :return:
    """

    # load the dataset

    header, df = k7.read(input_file)
    logging.info("Dataset loaded.")

    # compute error bar

    df_grouped = df.groupby(df["mean_rssi"].apply(lambda x: round(x)))
    mean_index = [name for name, group in df_grouped if len(group) > 10]
    mean_pdr = [group.pdr.mean() for name, group in df_grouped if len(group) > 10]
    std_pdr = [group.pdr.std() for name, group in df_grouped if len(group) > 10]

    # plot

    plt.plot(df.mean_rssi, df.pdr, '+', zorder=0)
    plt.errorbar(mean_index, mean_pdr, std_pdr)

    plt.xlabel('RSSI average (dBm)')
    plt.ylabel('PDR (%)')
    plt.xlim([-95, -15])
    plt.ylim([0, 1.1])
    plt.tight_layout()
    plt.grid(True)

    # save figure

    _save_fig(input_file, "pdr_rssi")

def pdr_per_channel_over_time(input_file):
    """
    This script plots the PDR over time per channel.
    :param input_file:
    :return:
    """

    # load the dataset

    header, df = k7.read(input_file)
    logging.info("Dataset loaded.")

    color_list = ["blue", "red"]
    for link, df_link in df.groupby(["src", "dst"]):
        fig_num = len(df.channel.unique())
        fig, axs = plt.subplots(fig_num, 1, sharex=True)
        axs2 = {}
        fig.set_size_inches(7, 5)
        xfmt = md.DateFormatter('%y-%m-%d')
        index = fig_num - 1

        for freq, df_freq in df_link.groupby("channel"):
            freq = int(freq)
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

    # save figure

    _save_fig(input_file, "pdr_per_channel_over_time")

# ========================= helpers ===========================================

def _save_fig(input_file, plot_suffix):
    output_file_name = "{0}_{1}.png".format(os.path.basename(input_file), plot_suffix)
    plt.savefig(os.path.join(os.path.dirname(input_file), output_file_name),
                format='png', bbox_inches='tight', pad_inches=0)

# ========================= main ==============================================

if __name__ == '__main__':

    # parsing user arguments

    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", help="The path to the dataset", type=str)
    args = parser.parse_args()

    # run the plotting methodes

    channel_available_hist(args.dataset)
    pdr_hist(args.dataset)
    pdr_per_channel(args.dataset)
    pdr_rssi(args.dataset)
    pdr_per_channel(args.dataset)
    pdr_per_channel_over_time(args.dataset)
