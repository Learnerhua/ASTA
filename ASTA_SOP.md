# ASTA - 自动化序列分类学智能体

**ASTA**（Automated Sequence Taxonomy Agent，自动化序列分类学智能体）

基于智能体驱动的序列比对与物种鉴定自动化流程

## 1 概述

ASTA 是一款全面的自动化序列分类学分析工具，通过智能体实现从原始序列数据到最终分析报告的全流程自动化。流程整合了序列采样、BLAST 比对、分类学注释、统计分析及报告生成等关键步骤，适用于微生物组学、环境样本、临床样本等领域中的物种鉴定与分类学分析。

**核心功能：**

- **自动化流程执行**：智能体自动驱动所有流程步骤，无需人工干预
- **序列采样与预处理**：支持 FASTQ/FASTA 格式，提供随机采样与格式转换功能
- **高效 BLAST 比对**：多线程并行计算，支持自定义数据库与参数配置
- **分类学注释**：自动获取完整分类层级信息（从界到种）
- **可视化分析**：为各分类层级生成统计图表（风玫瑰图/饼图）
- **自动化报告生成**：以 HTML 和 PDF 格式输出专业分析报告

## 2 流程架构

本流程包含 5 个顺序执行的步骤：

| 步骤 | 脚本                | 功能                   |
| ---- | ------------------- | ---------------------- |
| 1    | `01_seqs_sample.sh` | 序列采样与格式转换     |
| 2    | `02_blastn.sh`      | BLAST 序列比对         |
| 3    | `03_taxonmy.sh`     | 分类学注释             |
| 4    | `04_statistic.py`   | 统计分析与可视化       |
| 5    | `05_md_converter.py`| 报告生成（HTML/PDF）  |

## 3 环境要求

### 3.1 必需的软件工具

- **SeqKit**（v2.9.0+）— 序列处理工具
- **BLAST+**（v2.17.0+）— 序列比对工具
- **TaxonKit**（v0.20.0+）— 分类学信息查询工具
- **Python**（v3.12+）— 数据分析与可视化

### 3.2 必需的 Python 包

```bash
pip install pandas matplotlib markdown weasyprint
```

### 3.3 必需的数据库

- **BLAST 数据库**：NCBI 核苷酸数据库，如 `core_nt`、`nt` 等
- **TaxonKit 数据库**：taxdump 文件（自动下载至 `~/.taxonkit/` 目录）

## 4 安装

### 4.1 方式一：使用 Conda（推荐）

```bash
# 创建环境并安装依赖
conda create -n asta_pipeline python=3.12
conda activate asta_pipeline
conda install -c bioconda seqkit blast taxonkit
pip install pandas matplotlib markdown weasyprint
```

### 4.2 方式二：手动安装

各软件请参阅官方文档进行安装：

- SeqKit：<https://github.com/shenwei356/seqkit>
- BLAST+：<https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/>
- TaxonKit：<https://github.com/shenwei356/taxonkit>

## 5 使用方法

ASTA 支持两种运行模式：**智能体驱动执行（推荐）**和**手动分步执行**。

### 5.1 模式一：智能体驱动执行（推荐）

通过智能体（如 Trae IDE）运行流程是推荐的方式，具有以下优势：

- **高度自动化**：智能体自动驱动所有流程步骤，无需人工干预
- **智能参数配置**：智能体协助收集与验证分析参数
- **自动错误处理**：智能体可诊断并处理常见运行时错误
- **智能报告生成**：智能体按照模板格式自动生成专业报告

**执行步骤**：

1. 在智能体环境中打开流程目录
2. 向智能体发出运行命令：

```
用户指令：运行当前流程
```

3. 智能体将自动执行以下操作：
   - 选择并验证运行时环境
   - 收集并确认分析参数
   - 依次执行各步骤
   - 生成最终分析报告

### 5.2 模式二：手动分步执行

如需手动执行流程，请按以下步骤操作：

#### 5.2.1 参数说明

运行流程时需要指定以下参数：

| 参数          | 说明                           | 默认值       |
| ------------ | ------------------------------ | ------------ |
| 输入文件      | FASTQ/FASTA 序列文件           | 必填         |
| 输出目录      | 结果输出目录                   | `result/`   |
| 采样数量      | 随机采样的序列数量             | `1000`       |
| BLAST 数据库  | 数据库名称或路径               | `core_nt`    |
| BLAST 线程数  | 并行计算的线程数               | `8`          |
| 最大目标序列数 | 每个序列保留的最大匹配数       | `10`         |
| Top N        | 可视化展示的顶级分类单元数量   | `5`          |

#### 5.2.2 手动执行命令

如需手动执行每个步骤，请使用以下命令：

```bash
# 1. 序列采样
bash 01_seqs_sample.sh -i input.fq -o sample.fa -n 1000

# 2. BLAST 比对
bash 02_blastn.sh -Q sample.fa -D core_nt -J 48 -M 10 -O blastn_result.tsv

# 3. 分类学注释
bash 03_taxonmy.sh -i blastn_result.tsv -o taxon_info.tsv

# 4. 统计分析（各分类层级）
python3 04_statistic.py -i taxon_info.tsv -r Kingdom -n 5 -o result/
python3 04_statistic.py -i taxon_info.tsv -r Phylum -n 5 -o result/
# ... 其他分类层级

# 5. 报告生成
# Markdown 报告须由智能体根据 template.md 模板和执行结果生成
# 然后转换为 HTML 和 PDF 格式
python3 05_md_converter.py result/seqs_taxonomy_report.md -o result/report
```

**注意**：第 5 步所需的 Markdown 报告（`seqs_taxonomy_report.md`）须由智能体根据流程执行结果和 `template.md` 模板生成。智能体提取软件版本信息，整合分类学统计数据，按照模板格式生成完整报告。

## 6 输出文件

流程执行完成后，将生成以下文件：

| 文件                                      | 说明                         |
| ---------------------------------------- | ---------------------------- |
| `sample<N>.fa`                           | 采样后的 FASTA 序列文件       |
| `blastn_result.tsv`                     | BLAST 比对结果               |
| `taxon_info.tsv`                        | 分类学注释信息               |
| `taxon_info_<rank>_top<N>_summary.tsv`  | 各分类层级的统计表           |
| `taxon_info_<rank>_top<N>_pie.png/pdf`   | 各分类层级的饼图             |
| `seqs_taxonomy_report.html`             | HTML 格式分析报告             |
| `seqs_taxonomy_report.pdf`              | PDF 格式分析报告             |
| `run.log`                                | 流程执行日志                 |

## 7 分析报告

生成的报告包含三个主要部分：

1. **方法**：流程描述、软件版本、主要参数
2. **结果**：各分类层级（从界到种）的统计表与可视化图表
3. **结论**：基于分析结果的主要发现与总结

报告格式遵循 `template.md` 中定义的标准结构，确保分析结果的一致性与规范性。

## 8 示例

### 8.1 输入文件示例

```
输入文件：/path/to/sample.pure_unmapped_reads.fq
输出目录：result_example
采样数量：1000
BLAST 线程数：48
数据库：core_nt
```

### 8.2 执行结果示例

```
比对成功率：40.0%（400/1000）
主要类群：灵长目（70.5%）、偶蹄目（23.5%）
主要物种：人类（21.5%）、野猪（20.5%）、恒河猴（17.0%）
```

### 8.3 示例图示
![](D:\Work\KMHD\Analysis\NCBI_alignment\pipeline\Github_repo\example\taxon_info_Species_top5_pie.png)
