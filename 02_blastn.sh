#!/usr/bin/env bash

set -euo pipefail

# ==============================
# Usage:
# bash blastn.sh -Q <query_file> -DB <database> [-O <output_file>] [-T <task>] [-J <threads>]
# ==============================

# Print messages with timestamp
log_info() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] $1"
}

QUERY_FILE=""
DATABASE=""
OUTPUT_FILE=""
TASK="blastn"
NUM_THREADS=8
MAX_TARGET_SEQS=10

while getopts "Q:D:O:T:M:J:h" opt; do
    case $opt in
        Q) QUERY_FILE="$OPTARG" ;;
        D) DATABASE="$OPTARG" ;;
        O) OUTPUT_FILE="$OPTARG" ;;
        T) TASK="$OPTARG" ;;
        M) MAX_TARGET_SEQS="$OPTARG" ;;
        J) NUM_THREADS="$OPTARG" ;;
        h)
            echo "Usage: $0 -Q <query_file> -D <database> [-O <output_file>] [-T <task>] [-M <max_target_seqs>] [-J <threads>]"
            echo "  -Q    Query file (FASTA format, required)"
            echo "  -D    BLAST database name (required)"
            echo "  -O    Output file (default: blastn_result.tsv)"
            echo "  -T    BLAST task type (default: blastn)"
            echo "  -M    Max target sequences (default: 10)"
            echo "  -J    Number of threads (default: 8)"
            echo "  -h    Show this help message"
            exit 0
            ;;
        *)
            echo "Usage: $0 -Q <query_file> -D <database> [-O <output_file>] [-T <task>] [-M <max_target_seqs>] [-J <threads>]"
            exit 1
            ;;
    esac
done

# Parameter validation
if [[ -z "$QUERY_FILE" && -z "$DATABASE" ]]; then
    # Show help when no arguments provided
    echo "Usage: $0 -Q <query_file> -D <database> [-O <output_file>] [-T <task>] [-M <max_target_seqs>] [-J <threads>]"
    echo "  -Q    Query file (FASTA format, required)"
    echo "  -D    BLAST database name (required)"
    echo "  -O    Output file (default: blastn_result.tsv)"
    echo "  -T    BLAST task type (default: blastn)"
    echo "  -M    Max target sequences (default: 10)"
    echo "  -J    Number of threads (default: 8)"
    echo "  -h    Show this help message"
    exit 0
fi

if [[ -z "$QUERY_FILE" || -z "$DATABASE" ]]; then
    echo "Error: -Q and -D are required"
    exit 1
fi

if [[ ! -f "$QUERY_FILE" ]]; then
    echo "Error: query file not found: $QUERY_FILE"
    exit 1
fi

# Validate number of threads is a positive integer
if ! [[ "$NUM_THREADS" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: number of threads must be a positive integer: $NUM_THREADS"
    exit 1
fi

# Validate max target sequences is a positive integer
if ! [[ "$MAX_TARGET_SEQS" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: max target sequences must be a positive integer: $MAX_TARGET_SEQS"
    exit 1
fi

# ==============================
# Check if blastn is installed
# ==============================
if ! command -v blastn &> /dev/null; then
    echo "Error: blastn is not installed or not in PATH"
    echo "Please install BLAST+ tools"
    exit 1
fi

# ==============================
# Set default output file
# ==============================
if [[ -z "$OUTPUT_FILE" ]]; then
    OUTPUT_FILE="blastn_result.tsv"
fi

# ==============================
# Print parameter information
# ==============================
echo "================================================================"
echo "Query file       : $QUERY_FILE"
echo "Database         : $DATABASE"
echo "Output file      : $OUTPUT_FILE"
echo "Task             : $TASK"
echo "Max target seqs  : $MAX_TARGET_SEQS"
echo "Threads          : $NUM_THREADS"
echo "================================================================"

# ==============================
# Output directory logic
# ==============================
OUT_DIR=$(dirname "$OUTPUT_FILE")
mkdir -p "$OUT_DIR"

# ==============================
# Execute BLAST search
# ==============================
log_info "Starting BLAST search"

blastn \
    -query "$QUERY_FILE" \
    -db "$DATABASE" \
    -task "$TASK" \
    -word_size 11 \
    -evalue 1e-5 \
    -perc_identity 95 \
    -qcov_hsp_perc 85 \
    -max_target_seqs "$MAX_TARGET_SEQS" \
    -max_hsps 1 \
    -dust no \
    -soft_masking false \
    -num_threads "$NUM_THREADS" \
    -outfmt "6 qseqid sseqid sscinames pident length mismatch gapopen qstart qend sstart send qcovs evalue bitscore stitle" \
    -out "$OUTPUT_FILE" || {
        echo "Error: BLAST search failed. Check database availability and query file format."
        exit 1
    }

log_info "BLAST search completed"

# ==============================
# Print result statistics
# ==============================
log_info "Result statistics"
if [[ -f "$OUTPUT_FILE" ]]; then
    RESULT_LINES=$(wc -l < "$OUTPUT_FILE")
    echo "Number of hits    : $RESULT_LINES"
else
    echo "Warning: Output file not created"
fi

log_info "Done"