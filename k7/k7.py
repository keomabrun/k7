"""
This module provides methods to parse and manipulate K7 files
"""

import json
import pandas as pd
import numpy as np
import gzip

import __version__

REQUIRED_HEADER_FIELDS = [
    'start_date',
    'stop_date',
    'location',
    'node_count',
    'transaction_count',
    'channels',
    'tx_ifdur',
]
REQUIRED_DATA_FIELDS = (
    'src',
    'dst',
    'channels',
    'mean_rssi',
    'pdr',
    'tx_count',
    'transaction_id'
)

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
    data = pd.read_csv(
        file_path,
        parse_dates = ['datetime'],
        index_col = [0],  # make datetime column as index
        skiprows = 1,
        converters = {'channels': lambda x: [int(c) for c in x.strip("[]").split(';')]}
    )

    return header, data

def write(output_file_path, header, data):
    """
    Write the k7
    :param output_file_path:
    :param dict header:
    :param pandas.Dataframe data:
    :return: None
    """

    # convert channel list to string
    data.channels = data.channels.apply(lambda x: channel_list_to_str(x))

    # write to file
    with open(output_file_path, 'w') as f:
        # write header
        json.dump(header, f)
        f.write('\n')

        # write data
        data.to_csv(f, columns=REQUIRED_DATA_FIELDS, index_label='datetime')

def match(trace, source, destination, channels=None, transaction_id=None):
    """
    Find matching rows in the k7
    :param pandas.Dataframe trace:
    :param int source:
    :param int destination:
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
    for index, row in trace.iterrows():
        if (
                row['src'] == source and
                row['dst'] == destination and
                row['transaction_id'] == transaction_id and
                set(channels) < set(row['channels'])
        ):
            return row

    return None

def fill(file_path):
    """
    Fill the file to match format
      - Add row with PDR and RSSI for each link if missing
      - Add row with missing channels
      - Add tx_count column if missing
    :return: None
    """

    header, df = read(file_path)
    missing_rows = []
    filled = False

    # fill missing links
    for link in get_missing_links(header, df):
        missing_rows.append(
            {
                "datetime": link['transaction_fist_date'],
                "src": link['src'],
                "dst": link['dst'],
                "channels": header['channels'],
                "mean_rssi": None,
                "pdr": 0,
                "tx_count": None,
                "transaction_id": link['transaction_id'],
            }
        )
        filled = True

    # fill missing channels
    for name, group in df.groupby(["src", "dst", "transaction_id"]):
        first_date = group.index.min()
        src, dst, t_id = name[0], name[1], name[2]

        # find missing channels in group
        missing_channels = get_missing_channels(header['channels'], group)

        # add missing channel rows to list
        for c in missing_channels:
            missing_rows.append(
                {
                    "datetime": first_date,
                    "src": src,
                    "dst": dst,
                    "channels": [c],
                    "mean_rssi": None,
                    "pdr": 0,
                    "tx_count": None,
                    "transaction_id": t_id,
                }
            )
        filled = True

    # add tx_count column if missing
    if "tx_count" not in df.columns:
        df["tx_count"] = None
        filled = True

    if filled:
        if missing_rows:
            # convert missing rows into dataframe
            df_missing = pd.DataFrame(missing_rows)
            df_missing.set_index("datetime", inplace=True)

            # Merge Dataframes
            df = pd.concat([df, df_missing])
            df.sort_index(inplace=True)

        write(file_path + ".filled" , header, df)

def check(file_path):
    """
    Check if k7 format is respected
    :return: None
    """

    header, df = read(file_path)

    # check missing header fields
    for required_header in REQUIRED_HEADER_FIELDS:
        if required_header not in header:
            print "Header {0} missing".format(required_header)

    # check missing column
    col_diff = set(REQUIRED_DATA_FIELDS) - set(df.columns)
    if col_diff:
        print "Wrong columns. Required columns are: {0}".format(REQUIRED_DATA_FIELDS)

    # check missing links
    expected_num_links = sum([x for x in range(header['node_count'])]) * 2
    for transaction_id, transaction_df in df.groupby(["transaction_id"]):
        link_df = transaction_df.groupby(["src", "dst"])
        if len(link_df) != expected_num_links:
            print "Missing links. Found {0}/{1} in transaction {2}".format(
                len(link_df),
                expected_num_links,
                transaction_id
            )

    # check missing channels
    for name, group in df.groupby(["src", "dst", "transaction_id"]):
        # find missing channels in group
        missing_channels = get_missing_channels(header['channels'], group)
        if missing_channels:
            print "Channel missing for transaction {0}: {1}"\
                  .format(name, missing_channels)

def normalize(file_path):
    """
    Normalize the given file:
      - The source and destination fields are replaced by integers
    :param file_path:
    :return: None
    """
    normalized = False

    # read file
    header, df = read(file_path)

    # normalize src and dst
    if df.src.dtype != np.int64:
        normalized = True
        node_ids = df.src.unique()
        for i in range(len(node_ids)):
            df.src = df.src.str.replace(node_ids[i], str(i))
            df.dst = df.dst.str.replace(node_ids[i], str(i))

    # normalize pdr: 0-100 to 0-1
    if df.pdr.max() > 1:
        normalized = True
        df.pdr = df.pdr / 100.0

    # save file
    if normalized:
        write("norm_" + file_path, header, df)

# ========================= helpers ===========================================

def get_missing_links(header, df):
    """ Find missing links in a dataframe
    :param dict header:
    :param pd.Dataframe df:
    :return: a list of dict
    :rtype: list
    """
    links = []
    for transaction_id, transaction_df in df.groupby(["transaction_id"]):
        for src in range(header['node_count']):
            for dst in range(header['node_count']):
                if src == dst:
                    continue
                if not ((transaction_df['src'] == src) & (transaction_df['dst'] == dst)).any():
                    links.append({
                        'transaction_fist_date': transaction_df.index[0],
                        'transaction_id': transaction_id,
                        'src': src,
                        'dst': dst
                    })
    return links

def get_missing_channels(required_channels, data):
    """ Find missing channels in a dataframe
    :param list required_channels:
    :param pandas.Dataframe data:
    :rtype: list
    """
    channels = []
    for channel in data.channels:
        channel_list = channel
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
    parser.add_argument("--norm",
                        help="normalize file",
                        type=str,
                        dest='file_to_normalize',
                        )
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s ' + __version__.__version__)
    args = parser.parse_args()

    # run corresponding method
    if args.file_to_check is not None:
        check(args.file_to_check)
    elif args.file_to_fill is not None:
        fill(args.file_to_fill)
    elif args.file_to_normalize is not None:
        normalize(args.file_to_normalize)
    else:
        print "Command {0} does not exits."
