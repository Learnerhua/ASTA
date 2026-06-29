#!/usr/bin/env bash

set -euo pipefail

# ==============================
# Usage:
# bash seqs_sample.sh -i input.fq.gz -o output.fa [-n sample_size]
# ==============================

# Print messages with timestamp
log_info() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] $1"
}

INPUT_FILE=""
OUTPUT_FA=""
SAMPLE_SIZE=1000  # Default sample size

while getopts "i:o:n:h" opt; do
    case $opt in
        i) INPUT_FILE="$OPTARG" ;;
        o) OUTPUT_FA="$OPTARG" ;;
        n) SAMPLE_SIZE="$OPTARG" ;;
        h)
            echo "Usage: $0 -i <input_file> -o <output_fasta> [-n <sample_size>]"
            echo "  -i  Input file (FASTQ or FASTA format, required)"
            echo "  -o  Output FASTA file (required)"
            echo "  -n  Number of sequences to sample (default: 1000)"
            echo "  -h  Show this help message"
            exit 0
            ;;
        *)
            echo "Usage: $0 -i <input_file> -o <output_fasta> [-n <sample_size>]"
            exit 1
            ;;
    esac
done

# Parameter validation
if [[ -z "$INPUT_FILE" && -z "$OUTPUT_FA" ]]; then
    # Show help when no arguments provided
    echo "Usage: $0 -i <input_file> -o <output_fasta> [-n <sample_size>]"
    echo "  -i  Input file (FASTQ or FASTA format, required)"
    echo "  -o  Output FASTA file (required)"
    echo "  -n  Number of sequences to sample (default: 1000)"
    echo "  -h  Show this help message"
    exit 0
fi

if [[ -z "$INPUT_FILE" || -z "$OUTPUT_FA" ]]; then
    echo "Error: -i and -o are required"
    exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: input file not found: $INPUT_FILE"
    exit 1
fi

# Validate sample size is a positive integer
if ! [[ "$SAMPLE_SIZE" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: sample size must be a positive integer: $SAMPLE_SIZE"
    exit 1
fi

# ==============================
# Check if seqkit is installed
# ==============================
if ! command -v seqkit &> /dev/null; then
    echo "Error: seqkit is not installed or not in PATH"
    echo "Please install seqkit: https://github.com/shenwei356/seqkit"
    exit 1
fi

# ==============================
# Print parameter information
# ==============================
echo "================================================================"
echo "Input file       : $INPUT_FILE"
echo "Final output     : $OUTPUT_FA"
echo "Sample size      : $SAMPLE_SIZE"
echo "================================================================"

# ==============================
# Output directory logic
# ==============================
OUT_DIR=$(dirname "$OUTPUT_FA")
mkdir -p "$OUT_DIR"

# ==============================
# Detect input file format
# ==============================
IS_FASTQ=false
if [[ "$INPUT_FILE" =~ \.(fastq|fq)(\.gz)?$ ]]; then
    IS_FASTQ=true
    log_info "Detected input format: FASTQ"
elif [[ "$INPUT_FILE" =~ \.(fasta|fa)(\.gz)?$ ]]; then
    IS_FASTQ=false
    log_info "Detected input format: FASTA"
else
    echo "Warning: Unable to determine file format from extension, assuming FASTQ"
    IS_FASTQ=true
fi

# ==============================
# Streaming processing and sampling (optimized)
# ==============================
log_info "Processing and sampling ${SAMPLE_SIZE} sequences"

if [[ "$IS_FASTQ" == true ]]; then
    # FASTQ input: convert + unwrap + sample (streaming pipeline)
    seqkit fq2fa "$INPUT_FILE" -j 24 \
        | seqkit seq -w 0 -j 8 \
        | seqkit sample -n "$SAMPLE_SIZE" --rand-seed 123 -j 8 \
        > "$OUTPUT_FA" || {
            echo "Error: Processing failed. Check seqkit installation and input file format."
            exit 1
        }
else
    # FASTA input: unwrap + sample (streaming pipeline)
    seqkit seq -w 0 "$INPUT_FILE" -j 8 \
        | seqkit sample -n "$SAMPLE_SIZE" --rand-seed 123 -j 8 \
        > "$OUTPUT_FA" || {
            echo "Error: Processing failed. Check seqkit installation and input file format."
            exit 1
        }
fi

log_info "Sampling completed"

# ==============================
# Print output statistics
# ==============================
log_info "Output FASTA stats"
seqkit stats "$OUTPUT_FA"

log_info "Done"