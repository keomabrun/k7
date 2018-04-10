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
REQUIRED_DATA_FIELDS = [
    'datetime',
    'src',
    'dst',
    'channels',
    'mean_rssi',
    'pdr',
    'transaction_id'
]

__version__ = "0.0.4"

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
        raise Exception("Suported file extensions are: {0}".format(["k7.gz", "k7"]))

    # read data
    df = pd.read_csv(file_path,
                     parse_dates = ['datetime'],
                     index_col = [0],  # make datetime column as index
                     dtype={'channels': str},
                     skiprows=1,
                     )
    return header, df

def write(output_file_path, header, data):
    """
    Write the k7
    :param output_file_path:
    :param dict header:
    :param pandas.Dataframe data:
    :return:
    """
    with open(output_file_path, 'w') as f:
        # write header
        json.dump(header, f)
        f.write('\n')

        # write data
        data.to_csv(f)

def match(trace, source, destination, channel=None, transaction_id=None):
    """
    Find matching rows in the k7
    :param pandas.Dataframe trace:
    :param str source:
    :param str destination:
    :param int channel:
    :param int transaction_id:
    :return: None | pandas.core.series.Series
    """

    # channel
    if channel is None:
        channels = "11-26"
    else:
        channels = str(channel + 11)

    # transaction id
    if transaction_id is None:
        transaction_id = trace.transaction_id.min()

    # get rows
    series = trace[(trace.src == source) &
                   (trace.dst == destination) &
                   (trace.channels == channels) &
                   (trace.transaction_id == transaction_id)
            ]

    if len(series) >= 1:
        return series.iloc[0]  # return first element
    else:
        return None
    # elif len(series) > 1:
    #     log.warn("Multiple occurrences found for same transaction ID.")

def check(file_path):
    """
    Check if k7 format is respected
    :return:
    """

    header, df = read(file_path)

    for required_header in REQUIRED_HEADER_FIELDS:
        if required_header not in header:
            print "Header {0} missing".format(required_header)

if __name__ == "__main__":
    import argparse

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--check",
                        help="check the dataset format",
                        type=str,
                        dest='file_to_check',
                        )
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s ' + __version__)
    args = parser.parse_args()

    # run corresponding method
    if hasattr(args, "file_to_check"):
        check(args.file_to_check)
    else:
        print "Command {0} does not exits."
