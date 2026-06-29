#!/usr/bin/env bash

set -euo pipefail

# ==============================
# Usage:
# bash add_species_info.sh -i input_blast.tsv -o output_file.tsv
# ==============================

# Print messages with timestamp
log_info() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] $1"
}

INPUT_FILE=""
OUTPUT_FILE=""

while getopts "i:o:h" opt; do
    case $opt in
        i) INPUT_FILE="$OPTARG" ;;
        o) OUTPUT_FILE="$OPTARG" ;;
        h)
            echo "Usage: $0 -i <input_blast.tsv> -o <output_file.tsv>"
            echo "  -i  Input BLAST result file (TSV format, required)"
            echo "  -o  Output file path (required)"
            echo "  -h  Show this help message"
            exit 0
            ;;
        *)
            echo "Usage: $0 -i <input_blast.tsv> -o <output_file.tsv>"
            exit 1
            ;;
    esac
done

# Parameter validation
if [[ -z "$INPUT_FILE" && -z "$OUTPUT_FILE" ]]; then
    # Show help when no arguments provided
    echo "Usage: $0 -i <input_blast.tsv> -o <output_file.tsv>"
    echo "  -i  Input BLAST result file (TSV format, required)"
    echo "  -o  Output file path (required)"
    echo "  -h  Show this help message"
    exit 0
fi

if [[ -z "$INPUT_FILE" || -z "$OUTPUT_FILE" ]]; then
    echo "Error: -i and -o are required"
    exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: input file not found: $INPUT_FILE"
    exit 1
fi

# ==============================
# Check if taxonkit is installed
# ==============================
if ! command -v taxonkit &> /dev/null; then
    echo "Error: taxonkit is not installed or not in PATH"
    echo "Please install taxonkit: https://github.com/shenwei356/taxonkit"
    exit 1
fi

# ==============================
# Print parameter information
# ==============================
echo "================================================================"
echo "Input file       : $INPUT_FILE"
echo "Output file      : $OUTPUT_FILE"
echo "================================================================"

# ==============================
# Output directory logic
# ==============================
OUT_DIR=$(dirname "$OUTPUT_FILE")
mkdir -p "$OUT_DIR"

# ==============================
# Temporary directory management
# ==============================
tmpdir=$(mktemp -d -p "$OUT_DIR")
trap 'rm -rf "$tmpdir"' EXIT

# ==============================
# Processing workflow
# ==============================
log_info "Starting BLAST to Taxonomic conversion"

# Step 1: Deduplicate, keep first occurrence
log_info "Deduplicating query sequences"
awk '!seen[$1]++' "$INPUT_FILE" > "$tmpdir/top1.tsv"

# Step 2: Extract qseqid and species column (species in column 3)
log_info "Extracting query ID and species names"
cut -f1,3 "$tmpdir/top1.tsv" > "$tmpdir/top1_species.tsv"

# Step 3: Keep first species (handle semicolon-separated cases)
log_info "Cleaning species names"
awk -F'\t' '{
    split($2,a,";");
    $2=a[1];
    print $1"\t"$2
}' "$tmpdir/top1_species.tsv" > "$tmpdir/top1_species_clean.tsv"

# Step 4: Convert species names to TaxIDs and retrieve taxonomy
log_info "Converting species names to TaxIDs and retrieving taxonomy"
cut -f2 "$tmpdir/top1_species_clean.tsv" \
    | taxonkit name2taxid -j 40 \
    | taxonkit reformat2 -I 2 -j 40 -f "{kingdom}\t{phylum}\t{class}\t{order}\t{family}\t{genus}\t{species}" \
    > "$tmpdir/species_info.tsv" || {
        echo "Error: Taxonkit conversion failed"
        exit 1
    }

# Step 5: Merge query IDs with taxonomy information
log_info "Merging query IDs with taxonomy information"
paste <(cut -f1 "$tmpdir/top1_species_clean.tsv") <(cut -f2- "$tmpdir/species_info.tsv") > "$tmpdir/merged.tsv"

# Step 6: Fill missing values
log_info "Filling missing values"
awk -F'\t' 'BEGIN{OFS="\t"}{
    for(i=1;i<=9;i++){
        if($i=="") $i="unknown"
    }
    print
}' "$tmpdir/merged.tsv" > "$tmpdir/merged_filled.tsv"

# Step 7: Write final output with column headers
log_info "Writing final output with column headers"
echo -e "qseqid\tTaxID\tKingdom\tPhylum\tClass\tOrder\tFamily\tGenus\tSpecies" | cat - "$tmpdir/merged_filled.tsv" > "$OUTPUT_FILE"

log_info "Conversion completed"

# ==============================
# Print result statistics
# ==============================
log_info "Output file validation"

# Check if each line has 9 columns
bad_lines=$(awk -F'\t' 'NR>1 && NF!=9 {print NR,$0}' "$OUTPUT_FILE")
if [[ -n "$bad_lines" ]]; then
    echo "Warning: Lines with wrong column count:"
    echo "$bad_lines" | head -n 5
else
    echo "All lines have correct column count"
fi

# Number of unique input lines
lines_input=$(awk '!seen[$1]++' "$INPUT_FILE" | wc -l)
# Number of output lines (excluding header)
lines_output=$(tail -n +2 "$OUTPUT_FILE" | wc -l)

echo "Unique input lines : $lines_input"
echo "Output lines       : $lines_output"

if [[ "$lines_input" -eq "$lines_output" ]]; then
    echo "Line count matches"
else
    echo "Warning: Line count mismatch"
fi

log_info "Done"