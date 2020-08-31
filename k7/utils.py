from k7 import k7
import pandas as pd
import numpy as np

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

def get_pdr(df_link, dtsh):
    rx_count = len(df_link)
    tx_count = dtsh["tx_count"]

    dbm_values = np.array(df_link["rssi"], dtype=float)
    average_mw = sum(np.power(10, dbm_values / 10)) / len(dbm_values)
    average_dbm = 10 * np.log10(average_mw)

    return pd.Series({
        "datetime": df_link.datetime.iloc[0],
        "transaction_id": df_link['transctr'].iloc[0],
        "pdr": rx_count / float(tx_count),
        "mean_rssi": round(average_dbm, 2),
    })

# ========================= converters ========================================

def mercator_to_k7(file_path):
    """
    This script converts a mercator dataset into a K7 dataset

    Input CSV format:
    datetime,src,dst,channel,rssi,crc,expected,transaction_id,pkctr

    Ouput CSV format:
    JSON Header
    datetime,src,dst,channel,mean_rssi,pdr

    """
    pass

def smip_to_k7():
    pass