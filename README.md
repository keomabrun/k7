# k7

[![Version](https://img.shields.io/pypi/v/k7.svg)](https://pypi.python.org/pypi/k7)
[![Licence](https://img.shields.io/pypi/l/k7.svg)](https://pypi.python.org/pypi/k7)
[![Build](https://travis-ci.org/keomabrun/k7.svg?branch=master)](https://travis-ci.org/keomabrun/k7)

![Cassette](https://raw.githubusercontent.com/keomabrun/k7/master/docs/static/cassette.png)

CCBY: Cassette by Alvaro Cabrera from the Noun Project

# Usage


### Check file format

```
python -m k7.k7 --check myfile.k7
```

# k7 format

```
{"location": "grenoble", "tx_length": 100, "start_date": "2018-01-11 16:32:22", "stop_date": "2018-01-13 16:21:30", "node_count": 44, "channels": [11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26], "interframe_duration": 100}
datetime,src,dst,channel,mean_rssi,pdr,tx_count
2018-01-11 16:33:07,18,19,11,-53.2,1.0
2018-01-11 16:33:07,17,14,11,-84.03,0.97
2018-01-11 16:33:07,23,27,11,-83.88,1.0
2018-01-11 16:33:30,16,14,11,-67.03,1.0
2018-01-11 16:33:30,22,49,11,-70.0,1.0
...
```

## Header

Each k7 starts with a one-line header. The header is the json dump of a dict. The header contains the dataset meta data.
Ex:
```
{"location": "grenoble", "tx_length": 100, "start_date": "2017-06-20 16:22:15", "stop_date": "2017-06-21 10:29:29", "node_count": 50, "channels": [11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26], "interframe_duration": 10}
```

## Data
| datetime            | src     | dst     | channel | mean_rssi | pdr         | tx_count |
|---------------------|---------|---------|---------|-----------|-------------|----------|
|  iso8601 string     | int     | int     | int     | float     | float (0-1) | int      |

### Standard example:

| datetime            | src     | dst     | channel | mean_rssi | pdr  | tx_count |
|---------------------|---------|---------|---------|-----------|------|----------|
| 2017-12-19 21:35:41 | 0       | 1       |  11     | -74.5     | 1.0  | 100      |

### The source or destination can be empty (i.e when measured on all the neighbors of the src):

| datetime            | src     | dst     | channel | mean_rssi | pdr  | tx_count | 
|---------------------|---------|---------|---------|-----------|------|----------|
| 2017-12-19 21:35:41 |         |         |  11     | -74.5     | 0.7  | 100      |

### Unknown channel:

| datetime            | src     | dst     | channel | mean_rssi | pdr  | tx_count |
|---------------------|---------|---------|---------|-----------|------|----------|
| 2017-12-19 21:35:41 | 1       | 2       |         | -79.5     | 1.0  | 100      |

When the channel value is empty, it means that the channel is unknown for that measurement.
