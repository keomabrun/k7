"""
This module provides methods to parse and manipulate K7 files
"""

import json
import pandas as pd
import gzip

REQUIRED_HEADER_FIELDS = [
    'start_date',
    'stop_date',
    'location',
]
REQUIRED_DATA_FIELDS = (
    'datetime',
    'src',
    'dst',
    'channels',
    'mean_rssi',
    'pdr',
    'transaction_id'
)

__version__ = "0.0.5"

def read(file_path):
    """
    Read the k7
    :param str file_path:
    :return:
    :rtype: dict, pandas.Dataframe
    """
    # read header
    if file_path.endswith('k7.gz'):
        with gzip.open(file_path, 'r') as f:
            header = json.loads(f.readline())
    elif file_path.endswith('k7'):
        with open(file_path, 'r') as f:
            header = json.loads(f.readline())
    else:
        raise Exception("Supported file extensions are: {0}".format(["k7.gz", "k7"]))

    # read data
    df = pd.read_csv(
        file_path,
        parse_dates = ['datetime'],
        index_col = [0],  # make datetime column as index
        skiprows = 1
    )
    return header, df

def write(output_file_path, header, data):
    """
    Write the k7
    :param output_file_path:
    :param dict header:
    :param pandas.Dataframe data:
    :return: None
    """

    # convert channel list to string
    #data.channels = data.channels.apply(lambda x: channel_list_to_str(x))

    # write to file
    with open(output_file_path, 'w') as f:
        # write header
        json.dump(header, f)
        f.write('\n')

        # write data
        data.to_csv(f)

def match(trace, source, destination, channels=None, transaction_id=None):
    """
    Find matching rows in the k7
    :param pandas.Dataframe trace:
    :param str source:
    :param str destination:
    :param list channels:
    :param int transaction_id:
    :return: None | pandas.core.series.Series
    """

    # channel
    if channels is None:
        channels = [c for c in range(11, 27)]

    # transaction id
    if transaction_id is None:
        transaction_id = trace.transaction_id.min()

    # get rows
    series = trace[
        (trace.src == source) &
        (trace.dst == destination) &
        (trace.channels == channel_list_to_str(channels)) &
        (trace.transaction_id == transaction_id)
    ]

    if len(series) >= 1:
        return series.iloc[0]  # return first element
    else:
        return None

def fill(file_path):
    """
    Add lines with PDR and RSSI for each link if missing
    :return: None
    """

    header, df = read(file_path)

    missing_rows = []
    for name, group in df.groupby(["src", "dst", "transaction_id"]):
        first_date = group.index.min()
        src, dst, t_id = name[0], name[1], name[2]

        # find missing channels in group
        missing_channels = get_missing_channels(header['channels'], group)

        # add missing row to list
        for c in missing_channels:
            missing_rows.append(
                {
                    "datetime": first_date,
                    "src": src,
                    "dst": dst,
                    "channels": [c],
                    "mean_rssi": None,
                    "pdr": 0,
                    "transaction_id": t_id,
                }
            )

    if missing_rows:
        # convert missing rows into dataframe
        df_missing = pd.DataFrame(missing_rows)
        df_missing.set_index("datetime", inplace=True)

        # Merge Dataframes
        df_result = pd.concat([df, df_missing])
        df_result.sort_index(inplace=True)

        write("filled_" + file_path, header, df_result)

def check(file_path):
    """
    Check if k7 format is respected
    :return: None
    """

    header, df = read(file_path)

    for required_header in REQUIRED_HEADER_FIELDS:
        if required_header not in header:
            print "Header {0} missing".format(required_header)

    max_num_links = sum([i for i in range(1, header['node_count'] + 1)])
    lines_per_transaction = len(header['channels']) * max_num_links
    for name, group in df.groupby(["src", "dst", "transaction_id"]):
        # find missing channels in group
        missing_channels = get_missing_channels(header['channels'], group)
        if missing_channels:
            print "Channel missing for transaction {0}: {1}"\
                  .format(name, missing_channels)

# ========================= helpers ===========================================

def get_missing_channels(required_channels, data):
    """ Find missing channels in a dataframe
    :param list required_channels:
    :param pandas.Dataframe data:
    :rtype: list
    """
    channels = []
    for channel_str in data.channels:
        channel_list = [int(c) for c in channel_str.strip("[]").split(';')]
        for channel in channel_list:
            if channel not in channels:
                channels.append(channel)
    return list(set(required_channels) - set(channels))

def channel_list_to_str(channel_list):
    """
    [11,12,13] --> "[11;12;13]"
    :param list channel_list:
    :return:
    :rtype: str
    """
    return '[' + ';'.join([str(c) for c in channel_list]) + ']'

# ========================= main ==============================================

if __name__ == "__main__":
    import argparse

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--check",
                        help="check the dataset format",
                        type=str,
                        dest='file_to_check',
                        )
    parser.add_argument("--fill",
                        help="add missing rows",
                        type=str,
                        dest='file_to_fill',
                        )
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s ' + __version__)
    args = parser.parse_args()

    # run corresponding method
    if args.file_to_check is not None:
        check(args.file_to_check)
    elif args.file_to_fill is not None:
        fill(args.file_to_fill)
    else:
        print "Command {0} does not exits."
