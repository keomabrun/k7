import os
import pandas as pd
import pytest
import json

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
    k7.write(OUTPUT_FILE, header={}, data=pd.DataFrame())
    os.remove(OUTPUT_FILE)

@pytest.mark.parametrize("file_path", INPUT_FILES)
def test_check(file_path):
    k7.check(file_path)

@pytest.mark.parametrize("file_path", INPUT_FILES)
def test_match(file_path):
    header, trace = k7.read(file_path)
    assert k7.match(trace, "d9-a5-68", "d5-25-53",  11) is not None
    assert k7.match(trace, "d9-a5-68", "d5-25-53", 999) is None
