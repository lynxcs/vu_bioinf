import numpy as np
# import pandas as pd
import matplotlib.pyplot as plt

def graph_sequences(file):
    data_series = {}
    for i in range(0, 101):
        data_series[i] = 0

    with open(file, mode="+rt") as f:
        for idx, line in enumerate(f):
            # read every 2nd line (sequence)
            if idx % 4 != 1:
                continue
            line = line.rstrip()
            total_symbol_count = len(line)
            gc_count = line.count('G') + line.count('C')
            percent = int((gc_count / total_symbol_count) * 100.0)
            print(f"{total_symbol_count} - {gc_count} - {percent}%")
            data_series[percent] += 1
    return data_series

def main():
    series = graph_sequences("reads_for_analysis.fastq")
    plt.bar(series.keys(), series.values())
    plt.show()

if __name__ == "__main__":
    main()