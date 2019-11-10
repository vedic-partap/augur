import pandas as pd
import os
import numpy as np
import subprocess
from collections import defaultdict

"""
Function to form events.txt and times.txt from .csv input file

=============
Input : filename and threshold

Ouptut :
=============

"""


def extractor(path, minl=50):
    data = pd.read_csv(path + '/testpackets.csv')
    event_time_stamps = {}
    for row in range(data.shape[0]):
        row = list(data.loc[row])
        if row[2] in event_time_stamps:
            event_time_stamps[row[2]].append((row[5], row[1]))
        else:
            event_time_stamps[row[2]] = [(row[5], row[1])]
    filtered_event_time_stamps = {
        k: v
        for k, v in event_time_stamps.items() if len(v) >= minl
    }
    with open(path + '/ntpp/preprocess/events.txt', 'w') as f:
        for k in filtered_event_time_stamps.keys():
            f.write(" ".join(
                [str(x[0]) for x in filtered_event_time_stamps[k]]))
            f.write("\n")

    with open(path + '/ntpp/preprocess/times.txt', 'w') as f:
        for k in filtered_event_time_stamps.keys():
            f.write(" ".join(
                [str(x[1]) for x in filtered_event_time_stamps[k]]))
            f.write("\n")


"""
Function to read the events.txt and times.txt and load then in Data struture

=============
Input : filename

Ouptut : list of list
=============

"""
def read_file(filename):
    rows = open(filename,'r').readlines()
    data = [[float(ti) for ti in line.strip().split(' ')] for line in rows]
    return np.array(data)


"""
Function to comapre the event value of host with rest of host

=============
Input : indexes of times, number of host, data

Ouptut : list of list
=============

"""
def compare_interval_count(left, right, host_count, interval_count):
    Y = []
    for interval in range(left, right):
        a = []
        for host in range(host_count - 1):
            a.extend(
                np.greater(interval_count[host,interval],
                           interval_count[:, interval])[host + 1:])
        # print("a :", len(a))
        Y.append(a)
    return Y


"""
Function to ensure of the directory exist or not

=============
Input : directory

Ouptut :
=============

"""
def ensure_dir(d, verbose=True):
    if not os.path.exists(d):
        if verbose:
            print("Directory {} do not exist; creating...".format(d))

        os.makedirs(d)

def getMinCount(filename):
    events = read_file(filename)
    min_count = min([len(x) for x in events])
    return min_count

def read_pcap(filename):
    cmd = f"""tshark -r {filename} -E separator=, -E occurrence=f -E quote=d -o 'gui.column.format:"Time","%t","Source","%s", "Length","%L"'"""
    res = subprocess.check_output(cmd,shell=True).decode('utf-8')
    res = res.strip().split("\n")
    events, times = defaultdict(list),defaultdict(list)
    for entry in res:
        print(entry)
        if len(entry)>0:
            entry = entry.strip()
            [time, source, length] = entry.split(" ")
            events[source].append(int(length))
            times[source].append(float(time))
    return (list(events.values())),(list(times.values()))
    
if __name__ =="__main__":
    filename = "augur/data/fuzz-2006-11-24-4742.pcap"
    print(read_pcap(filename))

    
