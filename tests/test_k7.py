import os
import pandas as pd

from k7 import k7

INPUT_FILE = os.path.join("samples", "sample.k7")
OUTPUT_FILE = "output.k7"

def test_read():
    k7.read(INPUT_FILE)

def test_write():
    k7.write(OUTPUT_FILE, header={}, data=pd.DataFrame())
    os.remove(OUTPUT_FILE)

def test_check():
    k7.check(INPUT_FILE)

def test_match():
    header, trace = k7.read(INPUT_FILE)
    assert k7.match(trace, "d9-a5-68", "d5-25-53",  11) is not None
    assert k7.match(trace, "d9-a5-68", "d5-25-53", 999) is None
