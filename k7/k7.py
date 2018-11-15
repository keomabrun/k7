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
    'channels',
    'interframe_duration',
]
REQUIRED_DATA_FIELDS = (
    'src',
    'dst',
    'channel',
    'mean_rssi',
    'pdr',
    'tx_count'
)

def read(file_path):
    """
    Read the k7
    :param str file_path:
    :return:
    :rtype: dict, pandas.Dataframe
    """

    # detect filetype
    is_gzip = False
    gzip_format = "\x1f\x8b\x08"
    with open(file_path) as f:
        file_start = f.read(len(gzip_format))
        if file_start == gzip_format:
            is_gzip = True

    # read header
    if is_gzip:
        with gzip.open(file_path, 'r') as f:
            header = json.loads(f.readline())
    else:
        with open(file_path, 'r') as f:
            header = json.loads(f.readline())

    # read data
    data = pd.read_csv(
        file_path,
        parse_dates = ['datetime'],
        index_col = [0],  # make datetime column as index
        skiprows = 1,
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
    # write to file
    with gzip.open(output_file_path, 'w') as f:
        # write header
        json.dump(header, f)
        f.write('\n')

        # write data
        data.to_csv(f, columns=REQUIRED_DATA_FIELDS, index_label='datetime')

def match(trace, source, destination, channel=None):
    """
    Find matching rows in the k7
    :param pandas.Dataframe trace:
    :param int source:
    :param int destination:
    :param int channel:
    :return: None | pandas.core.series.Series
    """

    # get rows
    for index, row in trace.iterrows():
        if (
                row['src'] == source and
                row['dst'] == destination and
                row['channel'] == channel
        ):
            return row

    return None

def check(file_path):
    """
    Check if k7 format is respected
    :return: None
    """

    header, df = read(file_path)

    # check missing header fields
    for required_header in REQUIRED_HEADER_FIELDS:
        if required_header not in header:
            print("Header {0} missing".format(required_header))

    # check missing column
    col_diff = set(REQUIRED_DATA_FIELDS) - set(df.columns)
    if col_diff:
        print("Wrong columns. Required columns are: {0}".format(REQUIRED_DATA_FIELDS))

def normalize(file_path):
    """
    Normalize the given file:
      - The source and destination fields are replaced by integers
    :param file_path:
    :return: None
    """

    # read file
    header, df = read(file_path)

    # normalize src and dst
    if df.src.dtype != np.int64:
        node_ids = list(set(df.src.unique()).union(set(df.dst.unique())))
        for i in range(len(node_ids)):
            df.src = df.src.str.replace(node_ids[i], str(i))
            df.dst = df.dst.str.replace(node_ids[i], str(i))

    # tx_count as column
    if 'tx_count' in header:
        df['tx_count'] = header['tx_count']
        del header["tx_count"]

    # normalize pdr: 0-100 to 0-1
    if df.pdr.max() > 1:
        df.pdr = df.pdr / 100.0

    # normalize JSON header
    if 'stop_date' not in header:
        header['stop_date'] = str(df.index.max())
    if 'channel_count' in header or 'channels' not in header:
        del header['channel_count']
        header['channels'] = [n+11 for n in range(16)]
    if 'site' in header:
        header['location'] = header['site']
        del header['site']
    if 'tx_ifdur' in header:
        header['interframe_duration'] = header['tx_ifdur']
        del header['tx_ifdur']

    # save file
    write(file_path + ".norm", header, df)

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
    elif args.file_to_normalize is not None:
        normalize(args.file_to_normalize)
    else:
        print("Command {0} does not exits.")
