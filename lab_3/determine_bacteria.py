import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML

def graph_sequences(file):
    data_freq = {}
    data_values = {}
    for i in range(0, 101):
        data_freq[i] = 0
        data_values[i] = []

    with open(file, mode="+rt") as f:
        title = "UNK"
        for idx, line in enumerate(f):
            # read every 1st line (title/id)
            if idx % 4 == 0:
                title = line.rstrip()[1:].split(' ')[0]
                continue
            # read every 2nd line (sequence)
            if idx % 4 != 1:
                continue
            line = line.rstrip()
            total_symbol_count = len(line)
            gc_count = line.count('G') + line.count('C')
            percent = int((gc_count / total_symbol_count) * 100.0)
            data_freq[percent] += 1
            data_values[percent].append((title, line))
    return data_freq, data_values

def main():
    series, series_seqs = graph_sequences("reads_for_analysis.fastq")
    print(series)

    series_data = []
    for key in series:
        for i in range(series[key]):
            series_data.append(key)

    bin_width = 1
    bins = np.arange(0, 100 + bin_width, bin_width)
    hist, bin_edges = np.histogram(series_data, bins=bins)

    smoothed_hist = gaussian_filter1d(hist, sigma=2)

    peaks, _ = find_peaks(smoothed_hist, height=200, distance=7)

    peak_threshold = 7
    grouped_peaks = []
    current_group = [peaks[0]]

    for i in range(1, len(peaks)):
        if peaks[i] - peaks[i - 1] <= peak_threshold:
            current_group.append(peaks[i])
        else:
            grouped_peaks.append(current_group)
            current_group = [peaks[i]]

    grouped_peaks.append(current_group)

    top_values_per_group = []

    for group in grouped_peaks:
        start_bin = max(group[0] - peak_threshold, 0)
        end_bin = min(group[-1] + peak_threshold, len(hist) - 1)
        group_bins = np.arange(start_bin, end_bin + 1)
        
        group_frequencies = hist[group_bins]
        group_bin_centers = bin_edges[group_bins]

        sorted_indices = np.argsort(group_frequencies)[::-1][:1]
        top_values = group_bin_centers[sorted_indices]
        top_frequencies = group_frequencies[sorted_indices]

        top_values_per_group.append((top_values, top_frequencies))

    plt.bar(bin_edges[:-1], hist, width=bin_width, alpha=0.7, label='Histogram', color='Blue')
    plt.plot(bin_edges[:-1], smoothed_hist, color='orange', label='Smoothed Histogram')
    plt.scatter(bin_edges[peaks], smoothed_hist[peaks], color='red', label='Peaks')

    for i, (values, frequencies) in enumerate(top_values_per_group):
        plt.scatter(values, frequencies, label=f'Peak group vals {i}')

    for i, group in enumerate(grouped_peaks):
        for peak_index in group:
            plt.text(bin_edges[peak_index], hist[peak_index], f'Peak {i+1}', color='black', fontsize=8)

    peak_values = []
    for (val, freq) in top_values_per_group:
        values = list(set(series_seqs[val[0]]))
        peak_values.extend(values[:5])

    print(peak_values)
    with open('blastq', 'w') as f:
        f.write(
            'ID\tBacteria\tInput sequence\tMatching sequence\n')
        for peak_seq in peak_values:
            print(f"Querying: {peak_seq[1]}")
            result_handler = NCBIWWW.qblast(program="blastn", database="nt", sequence=peak_seq[1],
                expect=10, word_size=11, nucl_reward=2, hitlist_size=1, nucl_penalty=-3, gapcosts="5 2", entrez_query='Bacteria [Organism]')

            blast_records = NCBIXML.parse(result_handler)
            finish = False
            for blast_record in blast_records:
                for alignment in blast_record.alignments:
                    for hsp in alignment.hsps:
                        if not finish:
                            print(f"Bacteria: {alignment.title} (len: {alignment.length}, e val: {hsp.expect})")
                            f.write(f'{peak_seq[0]}\t{alignment.title}\t{peak_seq[1]}\t{hsp.sbjct}\n')
                            finish = True


    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()