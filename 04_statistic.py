#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
import sys
from datetime import datetime

# ==============================
# Time-stamped log function
# ==============================
def log_info(message):
    """Print log message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

# ==============================
# Arguments
# ==============================
parser = argparse.ArgumentParser(
    description="BLAST taxonomy summary and pie chart"
)

parser.add_argument(
    "-i", "--input",
    required=True,
    help="Input TSV file (required)"
)

parser.add_argument(
    "-r", "--rank",
    default="Species",
    help="Taxonomic rank column for analysis (default: Species). "
         "Must be one of: Kingdom, Phylum, Class, Order, Family, Genus, Species"
)

parser.add_argument(
    "-n", "--topn",
    type=int,
    default=5,
    help="Number of top categories to display in results (default: 5). "
         "Remaining categories will be grouped as 'Others'"
)

parser.add_argument(
    "-o", "--outdir",
    default=".",
    help="Output directory (default: current directory)"
)

args = parser.parse_args()

input_file = args.input
rank_column = args.rank
top_n = args.topn
outdir = args.outdir

# ==============================
# Valid taxonomic ranks
# ==============================
VALID_RANKS = ["Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species"]

# Check if rank parameter is valid
if rank_column not in VALID_RANKS:
    print(f"Error: Invalid rank parameter: {rank_column}")
    print(f"Valid ranks are: {', '.join(VALID_RANKS)}")
    sys.exit(1)

# Check if top_n is positive
if top_n <= 0:
    print(f"Error: Top N must be a positive integer: {top_n}")
    sys.exit(1)

# Check if input file exists
if not os.path.isfile(input_file):
    print(f"Error: Input file not found: {input_file}")
    sys.exit(1)

# Create output directory
os.makedirs(outdir, exist_ok=True)

# ==============================
# Print parameter info
# ==============================
print("================================================================")
print(f"Input file       : {input_file}")
print(f"Rank column      : {rank_column}")
print(f"Top N            : {top_n}")
print(f"Output dir       : {outdir}")
print("================================================================")

# ==============================
# Load data
# ==============================
log_info("Loading data...")
try:
    df = pd.read_csv(input_file, sep="\t")
except Exception as e:
    print(f"Error: Failed to read input file: {e}")
    sys.exit(1)

# Check if rank column exists in the data
if rank_column not in df.columns:
    print(f"Error: Column '{rank_column}' not found in input file")
    print(f"Available columns: {', '.join(df.columns)}")
    sys.exit(1)

total_reads = len(df)
log_info(f"Total reads: {total_reads:,}")

# ==============================
# Count
# ==============================
log_info("Calculating abundance...")

rank_count = (
    df[rank_column]
    .fillna("unknown")
    .value_counts()
)

top_items = rank_count.head(top_n)
others_count = rank_count.iloc[top_n:].sum()

summary = top_items.reset_index()
summary.columns = [rank_column, "Count"]

if others_count > 0:
    summary.loc[len(summary)] = ["Others", others_count]

summary["Percentage"] = (
    summary["Count"] / total_reads * 100
).round(2)

# ==============================
# Output paths
# ==============================
base_name = os.path.basename(input_file).replace(".tsv", "")

output_table = os.path.join(
    outdir,
    f"{base_name}_{rank_column}_top{top_n}_summary.tsv"
)

output_png = os.path.join(
    outdir,
    f"{base_name}_{rank_column}_top{top_n}_pie.png"
)

output_pdf = os.path.join(
    outdir,
    f"{base_name}_{rank_column}_top{top_n}_pie.pdf"
)

# ==============================
# Save table
# ==============================
log_info("Writing summary table...")

try:
    summary.to_csv(
        output_table,
        sep="\t",
        index=False
    )
except Exception as e:
    print(f"Error: Failed to write table: {e}")
    sys.exit(1)

# ==============================
# Plot
# ==============================
log_info("Generating pie chart...")

try:
    plt.rcParams['font.family'] = 'Arial'

    colors = plt.colormaps["tab20"](range(len(summary)))

    # Wind rose chart style - polar bar chart
    import numpy as np
    
    # Create polar axis
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'polar': True})
    
    # Calculate angles - spread categories evenly around the circle
    num_categories = len(summary)
    angles = np.linspace(0, 2 * np.pi, num_categories, endpoint=False).tolist()
    
    # Make the plot circular by closing the angles
    angles += angles[:1]
    
    # Get values and close the circle
    counts = summary["Count"].tolist()
    counts += counts[:1]
    
    percentages = summary["Percentage"].tolist()
    percentages += percentages[:1]
    
    # Bar width
    width = 2 * np.pi / num_categories
    
    # Create wind rose bars
    bars = ax.bar(
        angles,
        counts,
        width=width,
        color=colors[:num_categories],
        edgecolor='white',
        linewidth=1.5,
        zorder=2
    )
    
    # Customize the polar plot
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    # Set category labels at angles
    category_labels = summary[rank_column].tolist()
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(
        [f"{cat}\n({pct:.1f}%)" for cat, pct in zip(category_labels, summary["Percentage"])],
        fontsize=10,
        fontweight='bold'
    )
    
    # Move labels further away from the circle
    ax.tick_params(pad=30)
    
    # Remove radial labels
    ax.set_yticklabels([])
    
    # Add concentric circles with light gray
    ax.set_facecolor('#f8f8f8')
    ax.grid(color='lightgray', linestyle='-', linewidth=0.8, zorder=2)
    
    # Add legend with count information
    legend_labels = [
        f"{row[rank_column]}  ({row.Count:,})"
        for _, row in summary.iterrows()
    ]
    
    ax.legend(
        bars,
        legend_labels,
        title=rank_column,
        loc="center left",
        bbox_to_anchor=(1.25, 0.5),
        fontsize=10,
        title_fontsize=12,
        ncol=1,
        frameon=True,
        fancybox=True,
        shadow=True
    )
    
    ax.set_title(
        f"Top {top_n} {rank_column} Composition\nTotal aligned sequences = {total_reads:,}",
        y=1.25,
        fontsize=14,
        fontweight='bold'
    )

    fig.tight_layout()

    fig.savefig(
        output_png,
        dpi=300,
        bbox_inches='tight'
    )

    fig.savefig(
        output_pdf,
        bbox_inches='tight'
    )

    plt.close()

except Exception as e:
    print(f"Error: Failed to generate plot: {e}")
    sys.exit(1)

log_info("Analysis completed")

# ==============================
# Summary output
# ==============================
log_info(f"Summary table : {output_table}")
log_info(f"Pie chart PNG : {output_png}")
log_info(f"Pie chart PDF : {output_pdf}")

log_info("Done")