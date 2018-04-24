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
    }

    data = pd.DataFrame(
        [
            ["2018-01-11 16:33:07", 0, 1, [26], "-91.0", "0.92", "2"],
        ],
        columns=k7.REQUIRED_DATA_FIELDS
    )
    k7.write(OUTPUT_FILE, header=header, data=data)
    os.remove(OUTPUT_FILE)

@pytest.mark.parametrize("file_path", INPUT_FILES)
def test_check(file_path):
    k7.check(file_path)

@pytest.mark.parametrize("file_path", INPUT_FILES)
def test_match(file_path):
    header, trace = k7.read(file_path)
    assert k7.match(trace, 0, 1,  [11]) is not None
    assert k7.match(trace, 0, 1, [999]) is None
