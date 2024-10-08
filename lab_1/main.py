import sys
import os
from Bio import SeqIO
from Bio.Seq import Seq
from collections import Counter, deque
import numpy as np
from itertools import product
from scipy.spatial.distance import pdist, squareform
import codon_table as ct

START_CODONS = ['ATG']
STOP_CODONS = ['TAA', 'TAG', 'TGA']

def find_coding_sequences(seq, min_seq_len = 100):
    stack = deque()
    coding_sequences = []

    for i in range(0, len(seq) - 2, 3):
        codon = seq[i:i+3]
        if codon in START_CODONS:
            stack.append(i)
        elif codon in STOP_CODONS:
            if len(stack) != 0:
                begin_idx = stack.popleft()
                stack.clear()
                end_idx = i + 3
                if end_idx - begin_idx >= min_seq_len:
                    coding_sequences.append(seq[begin_idx:end_idx])
    
    return coding_sequences

def translate_dna_to_protein(dna_seq):
    protein_seq = ''
    for i in range(0, len(dna_seq) - 2, 3):
        codon = dna_seq[i:i+3]
        protein_seq += ct.codontab.get(codon, '')
    return protein_seq

def calculate_codon_dicodon_frequencies(protein_seqs):
    codon_counts = Counter()
    dicodon_counts = Counter()

    # write 0's where missing codons/dicodons from seq
    codon_counts.update({codon: 0 for codon in set(ct.codontab.values()) - set(codon_counts.keys())})
    i = 0
    for codon_1 in set(ct.codontab.values()):
        for codon_2 in set(ct.codontab.values()):
            dicodon_counts.update({(codon_1+codon_2): 0})
            i += 1
    
    for protein_seq in protein_seqs:
        codon_counts.update(protein_seq)
        dicodon_counts.update([protein_seq[i:i+2] for i in range(len(protein_seq) - 1)])
    
    total_codons = sum(codon_counts.values())
    total_dicodons = sum(dicodon_counts.values())
    
    codon_frequencies = {k: v / total_codons for k, v in codon_counts.items()}
    dicodon_frequencies = {k: v / total_dicodons for k, v in dicodon_counts.items()}
    
    return codon_frequencies, dicodon_frequencies

def calculate_distance_matrix(frequencies_list):
    freq_list = [list(kv.values()) for kv in frequencies_list]
    dist = pdist(freq_list, metric='euclidean')
    distance_matrix = squareform(dist)
    return distance_matrix

def save_phylip_distance_matrix(distance_matrix, labels, output_file):
    with open(output_file, 'w') as f:
        f.write(f"{len(labels)}\n")
        for i, label in enumerate(labels):
            distances = " ".join([f"{dist:.3f}" for dist in distance_matrix[i]])
            f.write(f"{label} {distances}\n")

def process_sequences(sequences):
    all_codon_frequencies = []
    all_dicodon_frequencies = []
    labels = []

    for record in sequences:
        seq = str(record.seq)
        reverse_comp_seq = str(Seq(seq).reverse_complement())
        coding_sequences = find_coding_sequences(seq) + find_coding_sequences(reverse_comp_seq)

        protein_sequences = [translate_dna_to_protein(cs) for cs in coding_sequences]
        
        codon_freqs, dicodon_freqs = calculate_codon_dicodon_frequencies(protein_sequences)
        all_codon_frequencies.append(codon_freqs)
        all_dicodon_frequencies.append(dicodon_freqs)
        labels.append(record.id)
    
    codon_distance_matrix = calculate_distance_matrix(all_codon_frequencies)
    dicodon_distance_matrix = calculate_distance_matrix(all_dicodon_frequencies)
    
    codon_dist_mtx_file = f"codons.phy"
    dicodon_dist_mtx_file = f"dicodons.phy"
    save_phylip_distance_matrix(codon_distance_matrix, labels, codon_dist_mtx_file)
    save_phylip_distance_matrix(dicodon_distance_matrix, labels, dicodon_dist_mtx_file)

def main(fasta_dir):
    sequences = []
    for fasta_file in os.listdir(fasta_dir):
        if not fasta_file.endswith(".fasta"):
            continue
        fasta_file = os.path.join(fasta_dir, fasta_file)
        sequences += SeqIO.parse(fasta_file, "fasta")

    process_sequences(sequences)
    
if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Pass directory containing fasta files as first argument")
