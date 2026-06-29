# ASTA - Automated Sequence Taxonomy Agent

**ASTA** (Automated Sequence Taxonomy Agent)

Agent-driven automated pipeline for sequence alignment and species identification

## Overview

ASTA is a comprehensive automated tool for sequence taxonomy analysis, powered by intelligent agents to achieve full automation from raw sequence data to final analysis reports. The pipeline integrates key steps including sequence sampling, BLAST alignment, taxonomic annotation, statistical analysis, and report generation. It is suitable for species identification and taxonomic analysis in microbiomics, environmental samples, clinical samples, and other research fields.

### Key Features

- **Automated Pipeline Execution**: Intelligent agents automatically drive all pipeline steps without manual intervention
- **Sequence Sampling and Preprocessing**: Supports FASTQ/FASTA formats with random sampling and format conversion
- **Efficient BLAST Alignment**: Multi-threaded parallel computation with customizable databases and parameters
- **Taxonomic Annotation**: Automatically retrieves complete taxonomic hierarchy information (Kingdom to Species)
- **Visualization Analysis**: Generates statistical charts for each taxonomic level (wind rose/pie charts)
- **Automated Report Generation**: Outputs professional analysis reports in HTML and PDF formats

## Pipeline Architecture

The pipeline consists of 5 sequential steps:

| Step | Script               | Function                                |
| ---- | -------------------- | --------------------------------------- |
| 1    | `01_seqs_sample.sh`  | Sequence sampling and format conversion |
| 2    | `02_blastn.sh`       | BLAST sequence alignment                |
| 3    | `03_taxonmy.sh`      | Taxonomic annotation                    |
| 4    | `04_statistic.py`    | Statistical analysis and visualization  |
| 5    | `05_md_converter.py` | Report generation (HTML/PDF)            |

## Requirements

### Required Software Tools

- **SeqKit** (v2.9.0+) - Sequence processing tool
- **BLAST+** (v2.17.0+) - Sequence alignment tool
- **TaxonKit** (v0.20.0+) - Taxonomic information query tool
- **Python** (v3.12+) - Data analysis and visualization

### Required Python Packages

```bash
pip install pandas matplotlib markdown weasyprint
```

### Required Databases

- **BLAST Database**: NCBI nucleotide databases such as `core_nt`, `nt`, etc.
- **TaxonKit Database**: taxdump files (automatically downloaded to `~/.taxonkit/`)

## Installation

### Option 1: Using Conda (Recommended)

```bash
# Create environment and install dependencies
conda create -n asta_pipeline python=3.12
conda activate asta_pipeline
conda install -c bioconda seqkit blast taxonkit
pip install pandas matplotlib markdown weasyprint
```

### Option 2: Manual Installation

Please refer to official documentation for each software:

- SeqKit: <https://github.com/shenwei356/seqkit>
- BLAST+: <https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/>
- TaxonKit: <https://github.com/shenwei356/taxonkit>

## Usage

ASTA supports two execution modes: **Agent-driven Execution (Recommended)** and **Manual Step-by-step Execution**.

### Mode 1: Agent-driven Execution (Recommended)

Running the pipeline through an intelligent agent (such as Trae IDE) is the recommended method with the following advantages:

- **High Automation**: Agent automatically drives all pipeline steps without manual intervention
- **Intelligent Parameter Configuration**: Agent assists in collecting and validating analysis parameters
- **Automatic Error Handling**: Agent can diagnose and handle common runtime errors
- **Intelligent Report Generation**: Agent automatically generates professional reports following template format

**Execution Steps**:

1. Open the pipeline directory in an agent environment
2. Issue a run command to the agent:

```
User command: Run the current pipeline
```

1. The agent will automatically perform the following operations:
   - Select and validate the runtime environment
   - Collect and confirm analysis parameters
   - Execute steps sequentially
   - Generate final analysis report

### Mode 2: Manual Step-by-step Execution

If you need to execute the pipeline manually, follow these steps:

#### Parameter Specification

The following parameters are required when running the pipeline:

| Parameter        | Description                                     | Default Value |
| ---------------- | ----------------------------------------------- | ------------- |
| Input file       | FASTQ/FASTA sequence file                       | Required      |
| Output directory | Output directory for results                    | `result/`     |
| Sample size      | Number of sequences to randomly sample          | `1000`        |
| BLAST database   | Database name or path                           | `core_nt`     |
| BLAST threads    | Number of threads for parallel computation      | `8`           |
| Max target seqs  | Maximum matches to retain per sequence          | `10`          |
| Top N            | Number of top taxonomic units for visualization | `5`           |

#### Manual Execution Commands

If you need to execute each step manually, use the following commands:

```bash
# 1. Sequence sampling
bash 01_seqs_sample.sh -i input.fq -o sample.fa -n 1000

# 2. BLAST alignment
bash 02_blastn.sh -Q sample.fa -D core_nt -J 48 -M 10 -O blastn_result.tsv

# 3. Taxonomic annotation
bash 03_taxonmy.sh -i blastn_result.tsv -o taxon_info.tsv

# 4. Statistical analysis (each taxonomic level)
python3 04_statistic.py -i taxon_info.tsv -r Kingdom -n 5 -o result/
python3 04_statistic.py -i taxon_info.tsv -r Phylum -n 5 -o result/
# ... other taxonomic levels

# 5. Report generation
# Markdown report must be generated by agent based on template.md and execution results
# Then convert to HTML and PDF formats
python3 05_md_converter.py result/seqs_taxonomy_report.md -o result/report
```

**Note**: Step 5 requires the Markdown report (`seqs_taxonomy_report.md`) to be generated by an intelligent agent based on pipeline execution results and the `template.md` template. The agent extracts software version information, integrates taxonomic statistical data, and generates a complete report following the template format.

## Output Files

After pipeline completion, the following files are generated:

| File                                   | Description                                 |
| -------------------------------------- | ------------------------------------------- |
| `sample<N>.fa`                         | Sampled FASTA sequence file                 |
| `blastn_result.tsv`                    | BLAST alignment results                     |
| `taxon_info.tsv`                       | Taxonomic annotation information            |
| `taxon_info_<rank>_top<N>_summary.tsv` | Statistical tables for each taxonomic level |
| `taxon_info_<rank>_top<N>_pie.png/pdf` | Pie charts for each taxonomic level         |
| `seqs_taxonomy_report.html`            | HTML format analysis report                 |
| `seqs_taxonomy_report.pdf`             | PDF format analysis report                  |
| `run.log`                              | Pipeline execution log                      |

## Analysis Report

The generated report contains three main sections:

1. **Methods**: Pipeline description, software versions, main parameters
2. **Results**: Statistical tables and visualization charts for each taxonomic level (Kingdom to Species)
3. **Conclusion**: Main findings and summary based on analysis results

Report format follows the standard structure defined in `template.md`, ensuring consistency and standardization of analysis results.

## Example

### Input File Example

```
Input file: /path/to/sample.pure_unmapped_reads.fq
Output directory: result_example
Sample size: 1000
BLAST threads: 48
Database: core_nt
```

### Execution Result Example

```
Alignment success rate: 40.0% (400/1000)
Major groups: Primates (70.5%), Artiodactyla (23.5%)
Major species: Homo sapiens (21.5%), Sus scrofa (20.5%), Macaca mulatta (17.0%)
```
### Illustration Exampe
![](https://github.com/Learnerhua/ASTA/blob/main/example/taxon_info_Species_top5_pie.png)

## Notes

1. **Database Configuration**: Ensure BLAST database is accessible; set `BLASTDB` environment variable if needed
2. **Resource Requirements**: BLAST alignment is compute-intensive; adjust thread count based on available CPU
3. **Font Support**: Reports contain Chinese content; ensure Chinese fonts are installed on system
4. **Disk Space**: Pipeline may generate large temporary files; ensure sufficient disk space

## Contact

For questions or suggestions, please submit an Issue or Pull Request.

**Email**: oyjh417701@163.com

## Copyright

June 29 CST 2026

Copyright (c) 2026 OYJH

All Rights Reserved.

## License

MIT License

## Acknowledgments

This pipeline integrates the following excellent open-source tools:

- [SeqKit](https://github.com/shenwei356/seqkit) - Fast sequence processing
- [BLAST+](https://blast.ncbi.nlm.nih.gov) - NCBI sequence alignment
- [TaxonKit](https://github.com/shenwei356/taxonkit) - Taxonomic information processing

<br />

<br />

