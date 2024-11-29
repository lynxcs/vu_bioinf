import numpy as np

def calc_file_quality_score_min_max(file):
    min_val = 128 # tingejau tikslaus max ieskot, bet turetu tikt
    max_val = 0
    with open(file, mode="+rt") as f:
        for idx, line in enumerate(f):
            # read every 4th line (quality)
            if idx % 4 != 3:
                continue
            for symbol in line.rstrip():
                symbol_val = ord(symbol)
                if not min_val or symbol_val < min_val:
                    min_val = symbol_val
                if not max_val or symbol_val > max_val:
                    max_val = symbol_val
    return min_val, max_val

def main():
    encoding_min_max = [
        (33, 73,  "Sanger Phred+33"),
        (59, 104, "Solexa Solexa+64"),
        (64, 104, "Illumina 1.3+ Phred+64"),
        (66, 104, "Illumina 1.5+ Phred+64"),
        (33, 74,  "Illumina 1.8+ Phred+33"),
    ]
    min, max = calc_file_quality_score_min_max("reads_for_analysis.fastq")
    print(f"value range: {min}-{max}")
    print("Possible encodings:")
    for enc in encoding_min_max:
        if min < enc[0] or max > enc[1]:
            continue
        print(f"{enc[2]}: {enc[0]}-{enc[1]}")

if __name__ == "__main__":
    main()