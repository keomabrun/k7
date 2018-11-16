import os
import pandas as pd
import pytest

from k7 import k7

# =========================== defines =========================================

INPUT_FILES = [
    os.path.join("samples", "sample.k7"),
    os.path.join("samples", "sample.k7.gz"),
]
OUTPUT_FILE = "output.k7"

# ============================ tests ==========================================

@pytest.mark.parametrize("file_path", INPUT_FILES)
def test_read(file_path):
    k7.read(file_path)
    k7.read(file_path)

def test_write():
    header = {
        'start_date': "2018-01-11 16:33:07",
        'stop_date': "2018-01-12 00:05:24",
        'location': "grenoble",
        'channels': range(11, 27)
    }

    data = pd.DataFrame.from_dict(
        {
            "2018-01-11 16:33:07": {
                "src": 0,
                "dst": 1,
                "channel": 25,
                "mean_rssi": -91.0,
                "pdr": 0.92,
                "tx_count": 100,
            }
        },
        orient='index',
    )
    k7.write(OUTPUT_FILE, header=header, data=data)
    os.remove(OUTPUT_FILE)

@pytest.mark.parametrize("file_path", INPUT_FILES)
def test_check(file_path):
    k7.check(file_path)

@pytest.mark.parametrize("file_path", INPUT_FILES)
def test_match(file_path):
    header, trace = k7.read(file_path)
    assert k7.match(trace, 0, 4,  11) is not None
    assert k7.match(trace, 0, 1, 999) is None
