---
name: "ncbi-alignment-pipeline"
description: "Automates NCBI BLAST sequence alignment and taxonomy classification pipeline. Invokes when user wants to run sequence alignment, perform species identification, process FASTQ/FASTA files for taxonomic analysis, or mentions running the pipeline."
---

# NCBI Alignment Pipeline Automation

This skill automates the complete NCBI BLAST sequence alignment and taxonomy classification pipeline, including environment validation, parameter configuration, execution, and logging.

## When to Invoke

Invoke this skill IMMEDIATELY when:
- User asks to run the sequence alignment pipeline
- User wants to perform species identification or taxonomic analysis
- User mentions processing FASTQ/FASTA files for BLAST analysis
- User asks about the NCBI alignment workflow
- User says "run the pipeline" or similar instructions

## Pipeline Overview

The pipeline consists of 5 sequential steps:

1. **01_seqs_sample.sh** - Sequence sampling from FASTQ/FASTA files
2. **02_blastn.sh** - BLAST sequence alignment
3. **03_taxonmy.sh** - Taxonomic classification using TaxonKit
4. **04_statistic.py** - Statistical analysis and visualization
5. **05_md_converter.py** - Report generation in HTML/PDF formats

## Execution Workflow

### Step 1: Environment Selection (FIRST STEP)

**CRITICAL:** Before checking dependencies, ask user which environment to use for running the pipeline.

**Ask User:**
- "请问您想在哪个环境中运行此流程？"
- "请指定运行环境（例如：conda 环境名称或路径）"

**Environment Options:**
1. **Conda environment** - Ask for environment name (e.g., "bioinfo", "blast_env")
2. **System environment** - Use default system PATH
3. **Custom environment** - User specifies environment path or configuration

**Environment Activation:**
If user specifies a conda environment, activate it first:
```bash
conda activate <environment_name>
```

**Why This Step First:**
- User may have multiple environments with different tool versions
- Dependencies must be checked in the correct environment
- Avoids false negatives from checking wrong environment

### Step 2: Environment Validation

Check all required dependencies in the user-specified environment:

**Required Tools:**
- `seqkit` - For sequence sampling and format conversion
- `blastn` - For BLAST alignment (BLAST+ tools)
- `taxonkit` - For taxonomic classification
- `python3` - For statistics and report generation

**Required Python Packages:**
- `pandas`
- `matplotlib`
- `markdown`
- `weasyprint` or `wkhtmltopdf` (for PDF generation)

**Required Databases:**
- BLAST database (e.g., core_nt, nt) - Ask user for database path or name
- TaxonKit database (taxdump files in ~/.taxonkit/)

**Validation Commands:**
```bash
# Check seqkit
seqkit version

# Check blastn
blastn -version

# Check taxonkit
taxonkit version

# Check Python and packages
python3 -c "import pandas, matplotlib, markdown; print('OK')"

# Check weasyprint or wkhtmltopdf
python3 -c "import weasyprint" 2>/dev/null || which wkhtmltopdf
```

If any dependency is missing, provide clear installation instructions based on pipeline_tutorial.md and ask user to install before proceeding.

### Step 3: Parameter Configuration

Collect and validate pipeline parameters:

**Required Parameters:**
1. **Input file** (FASTQ/FASTA format) - Ask user for the path
2. **Output directory** - Ask user or use default (e.g., `result/`)
3. **Sample size** - Default: 1000, ask user if different needed
4. **BLAST database** - Ask user for database path or name
5. **BLAST threads** - Default: 8, ask user if different needed
6. **Max target sequences** - Default: 10
7. **Taxonomic ranks to analyze** - Default: all ranks (Kingdom through Species)
8. **Top N for visualization** - Default: 5

**Default Configuration Example:**
```
Input file: [USER_INPUT]
Output directory: result/
Sample size: 1000
BLAST database: core_nt
BLAST threads: 8
Max target seqs: 10
Ranks: Kingdom,Phylum,Class,Order,Family,Genus,Species
Top N: 5
```

Present the configuration to user and ask for confirmation. If user approves, proceed to execution.

### Step 4: Pipeline Execution

Execute each step sequentially with error handling:

**Execution Steps:**

1. **Sequence Sampling**
   ```bash
   bash 01_seqs_sample.sh -i <input_file> -o <output_dir>/sample<N>.fa -n <sample_size>
   ```

2. **BLAST Alignment**
   ```bash
   bash 02_blastn.sh -Q <output_dir>/sample<N>.fa -D <database> -J <threads> -M <max_target_seqs> -O <output_dir>/blastn_result.tsv
   ```

3. **Taxonomic Classification**
   ```bash
   bash 03_taxonmy.sh -i <output_dir>/blastn_result.tsv -o <output_dir>/taxon_info.tsv
   ```

4. **Statistical Analysis and Visualization**
   For each taxonomic rank:
   ```bash
   python 04_statistic.py -i <output_dir>/taxon_info.tsv -r <rank> -n <top_n> -o <output_dir>
   ```

5. **Report Generation** (CRITICAL STEP)

   **Template Reference:** The report MUST strictly follow the format defined in `template.md` (located in the pipeline directory) to ensure consistency across all analyses.

   **Report Generation Prompt:**
   Use this prompt to guide AI assistant in generating the report:

   ```
   你是一个生物信息学专家，请你根据流程的运行结果帮我梳理成报告，格式可以参考已有的template.md文档，报告主要有3大部分：

   1.方法部分，简要介绍流程的过程和主要的软件，需要给出主要软件（seqkit; blast; taxonkit; python）的使用版本（从当前环境中获取），内容不能完全照搬模板，需要结合实际使用的参数确定。

   2.结果部分：概括每一个分类水平的统计结果并插入相应的结果图片。

   3.结论部分，简单总结。

   最后生成markdown格式的报告，名称为seqs_taxonmy_report.md。
   ```

   **Report Generation Steps:**
   1. Read `template.md` to understand the required report structure
   2. Use the above prompt to generate `seqs_taxonomy_report.md` following template format
   3. Extract software versions from current environment:
      ```bash
      seqkit version
      blastn -version
      taxonkit version
      python3 --version
      ```
   4. Insert actual parameters used in the "方法" section
   5. Generate statistics tables and descriptions for each taxonomic rank following template format
   6. Insert pie chart images with proper relative paths (e.g., `taxon_info_Kingdom_top5_pie.png`)
   7. Ensure all formatting matches template exactly
   8. Convert final markdown to HTML/PDF:
      ```bash
      python 05_md_converter.py <output_dir>/seqs_taxonomy_report.md -o <output_dir>/report
      ```

   **Key Requirements:**
   - Report structure must match template exactly (目录, 方法, 结果, 结论 sections)
   - "方法" section: introduce process and software, include versions, no commands, customize based on actual parameters
   - "结果" section: summarize each taxonomic rank's statistics with corresponding images
   - "结论" section: brief summary in numbered list format
   - Table format must follow template specifications
   - Include Chinese translations for taxonomic terms
   - Output file name: `seqs_taxonomy_report.md`

**Error Handling:**
- If any step fails, check the error message
- Try to diagnose and fix common issues automatically:
  - Missing input files
  - Permission issues
  - Database path issues
  - Insufficient disk space
- If cannot resolve, provide clear error message and suggestions to user

### Step 5: Logging

Create and maintain a detailed `run.log` file with:

**Log Format:**
```
[YYYY-MM-DD HH:MM:SS] STEP_START: <step_name>
[YYYY-MM-DD HH:MM:SS] PARAMETERS: <parameters_used>
[YYYY-MM-DD HH:MM:SS] STATUS: <running/completed/failed>
[YYYY-MM-DD HH:MM:SS] DURATION: <time_taken>
[YYYY-MM-DD HH:MM:SS] ERROR: <error_message> (if any)
[YYYY-MM-DD HH:MM:SS] RESOLUTION: <resolution_attempted> (if any)
```

**Log Contents:**
- Start time and end time of entire pipeline
- Each step's execution details
- Parameter values used
- Runtime duration for each step
- Error messages and resolution attempts
- Output file paths
- Final summary

**Log Location:** `<output_dir>/run.log`

## Error Resolution Guide

### Common Errors and Solutions:

1. **"seqkit: command not found"**
   - Solution: Install seqkit using conda: `conda install -c bioconda seqkit`

2. **"blastn: command not found"**
   - Solution: Install BLAST+ tools from NCBI

3. **"taxonkit: command not found"**
   - Solution: Install taxonkit and download taxdump database

4. **"BLAST database error"**
   - Check if database exists: `blastdbcheck -db <database_name>`
   - Set BLASTDB environment variable if needed

5. **"No space left on device"**
   - Check disk space
   - Clean temporary files
   - Use smaller sample size

6. **Python module import errors**
   - Install missing packages: `pip install pandas matplotlib markdown weasyprint`

## Output Files

After successful execution, the pipeline generates:

1. **Sampled sequences:** `<output_dir>/sample<N>.fa`
2. **BLAST results:** `<output_dir>/blastn_result.tsv`
3. **Taxonomic info:** `<output_dir>/taxon_info.tsv`
4. **Statistics tables:** `<output_dir>/taxon_info_<rank>_top<N>_summary.tsv`
5. **Pie charts:** `<output_dir>/taxon_info_<rank>_top<N>_pie.png/pdf`
6. **Final report:** `<output_dir>/report.html` and `<output_dir>/report.pdf`
7. **Execution log:** `<output_dir>/run.log`

## Important Notes

1. **Script Location**: All pipeline scripts must be in the current working directory or in PATH
2. **Database Access**: Ensure BLAST database is accessible and properly configured
3. **Resource Requirements**: BLAST search can be resource-intensive; adjust thread count based on available CPU cores
4. **Chinese Language Support**: The pipeline supports Chinese characters in reports; ensure proper font installation
5. **User Interaction**: Always ask user for confirmation before running with default parameters
6. **Progress Updates**: Provide regular status updates during long-running operations (especially BLAST)
7. **Verification**: After each step, verify output files exist and are non-empty before proceeding
8. **Report Template Compliance** (CRITICAL): The final report MUST strictly follow the format in `template.md` to ensure consistency across all analyses. Deviation from the template format is not allowed.

## Example Usage

User: "请帮我跑一下这个流程"
Assistant: [Invokes this skill and starts pipeline automation]

User: "Run the NCBI alignment pipeline"
Assistant: [Invokes this skill immediately]

User: "I want to analyze my sequences for species identification"
Assistant: [Invokes this skill to start the pipeline]

## Skill Invocation Checklist

When invoked, follow this sequence:

- [ ] Step 1: Ask user which environment to use (conda/system/custom)
- [ ] Step 2: Activate environment if needed (e.g., conda activate)
- [ ] Step 3: Validate environment and dependencies in selected environment
- [ ] Step 4: Collect parameters from user
- [ ] Step 5: Present configuration and get approval
- [ ] Step 6: Initialize run.log
- [ ] Step 7: Execute 01_seqs_sample.sh
- [ ] Step 8: Execute 02_blastn.sh
- [ ] Step 9: Execute 03_taxonmy.sh
- [ ] Step 10: Execute 04_statistic.py for each rank
- [ ] Step 11: Generate markdown report (strictly following template.md format)
- [ ] Step 12: Execute 05_md_converter.py
- [ ] Step 13: Finalize run.log
- [ ] Step 14: Present summary to user