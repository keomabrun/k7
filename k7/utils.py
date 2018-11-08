from k7 import k7
import pandas as pd
import numpy as np

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

def mercator_to_k7(file_path):
    """
    This script converts a mercator dataset into a K7 dataset

    Input CSV format:
    timestamp,mac,frequency,length,rssi,crc,expected,srcmac,transctr,pkctr,nbpackets,txpower,txifdur,txpksize,txfillbyte

    Ouput CSV format:
    JSON Header
    datetime,src,dst,channel,mean_rssi,pdr

    """
    k7.write(file_path + ".k7", header, data)

def smip_to_k7():
    pass