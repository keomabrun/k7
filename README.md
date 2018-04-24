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

### File file with missing lines

A k7 file should contain i

```
python -m k7.k7 --fill myfile.k7
```

This will create a fille called `fill_myfile.k7` that contains the missing lines.

# k7 format

```
{"location": "grenoble", "tx_length": 100, "start_date": "2018-01-11 16:32:22", "stop_date": "2018-01-13 16:21:30", "node_count": 44, "channel_count": 16, "transaction_count": 10, "tx_ifdur": 100}
datetime,src,dst,channels,mean_rssi,pdr,tx_count,transaction_id
2018-01-11 16:33:07,05-43-32-ff-03-d9-a5-68,05-43-32-ff-02-d5-25-53,[11],-53.2,1.0,0
2018-01-11 16:33:07,05-43-32-ff-03-d9-a5-68,05-43-32-ff-03-db-b2-76,[11],-84.03,0.97,0
2018-01-11 16:33:07,05-43-32-ff-03-d9-a5-68,05-43-32-ff-03-d7-93-78,[11],-83.88,1.0,0
2018-01-11 16:33:30,05-43-32-ff-03-d6-95-84,05-43-32-ff-03-da-a9-72,[11],-67.03,1.0,0
2018-01-11 16:33:30,05-43-32-ff-03-d6-95-84,05-43-32-ff-03-da-c0-81,[11],-70.0,1.0,0
...
```

## Header

Each k7 starts with a one-line header. The header is the json dump of a dict. The header contains the dataset meta data.
Ex:
```
{"location": "grenoble", "tx_length": 100, "start_date": "2017-06-20 16:22:15", "stop_date": "2017-06-21 10:29:29", "tx_count": 100, "node_count": 50, "channel_count": 16, "transaction_count": 10, "tx_ifdur": 10}
```

## Data
| datetime            | src         | dst         | channels | mean_rssi | pdr         | tx_count | transaction_id |
|---------------------|-------------|-------------|----------|-----------|-------------|----------|----------------|
|  iso8601 string     | string      | string      | list     | float     | float (0-1) | int      | int            |

### Standard example:

| datetime            | src         | dst         | channels | mean_rssi | pdr  | tx_count | transaction_id |
|---------------------|-------------|-------------|----------|-----------|------|----------|----------------|
| 2017-12-19 21:35:41 | d7-94-75    | d7-94-79    | [11]     | -74.5     | 1.0  | int      | 1              |

### The source or destination can be empty (i.e when measured on all the neighbors of the src):

| datetime            | src         | dst         | channels | mean_rssi | pdr  | tx_count | transaction_id |
|---------------------|-------------|-------------|----------|-----------|------|----------|----------------|
| 2017-12-19 21:35:41 | d7-94-75    | d7-94-79    | [11]     | -74.5     | 0.7  | int      | 1              |

### Multiple channels:

| datetime            | src         | dst         | channels | mean_rssi | pdr  | tx_count | transaction_id |
|---------------------|-------------|-------------|----------|-----------|------|----------|----------------|
| 2017-12-19 21:35:41 | d7-94-75    | d7-94-79    | [11;12]  | -79.5     | 1.0  | int      | 2              |

When the channel list contains more than one element, it means that the PDR and RSSI value are calculated (averaged) over multiple channels.