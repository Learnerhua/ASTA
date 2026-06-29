# NCBI 序列分类学自动化分析流程

基于智能体的序列比对与物种鉴定自动化流程

## 流程简介

本流程是一个完整的序列分类学分析自动化工具，通过智能体驱动实现从原始序列数据到最终分析报告的全流程自动化处理。流程整合了序列采样、BLAST比对、分类学注释、统计分析及报告生成等关键步骤，适用于微生物组学、环境样本、临床样本等领域的物种鉴定与分类学分析。

### 主要功能

- **自动化流程执行**：智能体自动驱动流程各步骤，无需手动干预
- **序列采样与预处理**：支持 FASTQ/FASTA 格式，随机采样与格式转换
- **高效 BLAST 比对**：多线程并行计算，支持自定义数据库与参数
- **分类学注释**：自动获取完整的分类学层级信息（界-种）
- **可视化分析**：生成各分类层级的统计图表（风玫瑰图/饼图）
- **报告自动生成**：输出 HTML 和 PDF 格式的专业分析报告

## 流程架构

流程包含 5 个顺序执行的步骤：

| 步骤 | 脚本 | 功能 |
|------|------|------|
| 1 | `01_seqs_sample.sh` | 序列采样与格式转换 |
| 2 | `02_blastn.sh` | BLAST 序列比对 |
| 3 | `03_taxonmy.sh` | 分类学注释 |
| 4 | `04_statistic.py` | 统计分析与可视化 |
| 5 | `05_md_converter.py` | 报告生成（HTML/PDF） |

## 环境要求

### 必需软件工具

- **SeqKit** (v2.9.0+) - 序列处理工具
- **BLAST+** (v2.17.0+) - 序列比对工具
- **TaxonKit** (v0.20.0+) - 分类学信息查询工具
- **Python** (v3.12+) - 数据分析与可视化

### 必需 Python 包

```bash
pip install pandas matplotlib markdown weasyprint
```

### 必需数据库

- **BLAST 数据库**：如 `core_nt`、`nt` 等 NCBI 核酸数据库
- **TaxonKit 数据库**：taxdump 文件（自动下载到 `~/.taxonkit/`）

## 安装

### 方式一：使用 Conda（推荐）

```bash
# 创建环境并安装依赖
conda create -n ncbi_pipeline python=3.12
conda activate ncbi_pipeline
conda install -c bioconda seqkit blast taxonkit
pip install pandas matplotlib markdown weasyprint
```

### 方式二：手动安装

请参考各软件官方文档进行安装：

- SeqKit: https://github.com/shenwei356/seqkit
- BLAST+: https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/
- TaxonKit: https://github.com/shenwei356/taxonkit

## 使用方法

本流程支持两种运行方式：**智能体驱动运行（推荐）** 和 **手动分步运行**。

### 方式一：智能体驱动运行（推荐）

通过智能体（如 Trae IDE）运行流程，这是推荐的运行方式，具有以下优势：

- **自动化程度高**：智能体自动驱动流程各步骤，无需手动干预
- **参数智能配置**：智能体协助收集和验证分析参数
- **错误自动处理**：智能体可诊断并处理常见运行错误
- **报告智能生成**：智能体自动生成符合模板格式的专业报告

**运行步骤**：

1. 在智能体环境中打开流程目录
2. 向智能体发出运行指令：

```
用户指令: 开始运行当前流程
```

3. 智能体将自动执行以下操作：
   - 选择并验证运行环境
   - 收集并确认分析参数
   - 顺序执行各步骤
   - 生成最终分析报告

### 方式二：手动分步运行

如需手动执行流程，可按以下步骤操作：

#### 参数说明

运行流程时需提供以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 输入文件 | FASTQ/FASTA 格式序列文件 | 必需 |
| 输出目录 | 结果输出目录 | `result/` |
| 采样数量 | 随机采样的序列数 | `1000` |
| BLAST 数据库 | 数据库名称或路径 | `core_nt` |
| BLAST 线程数 | 并行计算的线程数 | `8` |
| Max target seqs | 每条序列最多保留的匹配数 | `10` |
| Top N | 可视化展示的 Top 分类单元数 | `5` |

#### 手动执行命令

如需手动执行各步骤，可使用以下命令：

```bash
# 1. 序列采样
bash 01_seqs_sample.sh -i input.fq -o sample.fa -n 1000

# 2. BLAST比对
bash 02_blastn.sh -Q sample.fa -D core_nt -J 48 -M 10 -O blastn_result.tsv

# 3. 分类学注释
bash 03_taxonmy.sh -i blastn_result.tsv -o taxon_info.tsv

# 4. 统计分析（各分类层级）
python3 04_statistic.py -i taxon_info.tsv -r Kingdom -n 5 -o result/
python3 04_statistic.py -i taxon_info.tsv -r Phylum -n 5 -o result/
# ... 其他分类层级

# 5. 报告生成
# Markdown 报告需由智能体根据 template.md 模板和运行结果生成
# 然后转换为 HTML 和 PDF 格式
python3 05_md_converter.py result/seqs_taxonomy_report.md -o result/report
```

**注意**：步骤 5 中的 Markdown 报告（`seqs_taxonomy_report.md`）需要由智能体根据流程运行结果和 `template.md` 模板自动生成，包含方法学描述、统计结果和结论分析。智能体会提取软件版本信息、整合各分类层级统计数据，并按照模板格式生成完整报告。

## 输出文件

流程完成后将生成以下文件：

| 文件 | 说明 |
|------|------|
| `sample<N>.fa` | 采样的 FASTA 序列文件 |
| `blastn_result.tsv` | BLAST 比对结果 |
| `taxon_info.tsv` | 分类学注释信息 |
| `taxon_info_<rank>_top<N>_summary.tsv` | 各分类层级统计表格 |
| `taxon_info_<rank>_top<N>_pie.png/pdf` | 各分类层级饼图 |
| `seqs_taxonomy_report.html` | HTML 格式分析报告 |
| `seqs_taxonomy_report.pdf` | PDF 格式分析报告 |
| `run.log` | 流程运行日志 |

## 分析报告

生成的报告包含三个主要部分：

1. **方法**：分析流程介绍、软件版本、主要参数
2. **结果**：各分类层级（界-种）的统计表格与可视化图表
3. **结论**：基于分析结果的主要发现与总结

报告格式遵循 `template.md` 定义的标准结构，确保分析结果的规范性与一致性。

## 示例

### 输入文件示例

```
输入文件: /path/to/sample.pure_unmapped_reads.fq
输出目录: result_example
采样数量: 1000
BLAST线程: 48
数据库: core_nt
```

### 运行结果示例

```
比对成功率: 40.0% (400/1000)
主要类群: 灵长目 (70.5%), 偶蹄目 (23.5%)
主要物种: Homo sapiens (21.5%), Sus scrofa (20.5%), Macaca mulatta (17.0%)
```

## 注意事项

1. **数据库配置**：确保 BLAST 数据库可访问，必要时设置 `BLASTDB` 环境变量
2. **资源需求**：BLAST 比对计算密集，建议根据可用 CPU 调整线程数
3. **中文支持**：报告包含中文内容，确保系统已安装中文字体
4. **磁盘空间**：流程可能产生较大临时文件，确保有足够磁盘空间

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

## 致谢

本流程整合了以下优秀开源工具：

- [SeqKit](https://github.com/shenwei356/seqkit) - 快速序列处理
- [BLAST+](https://blast.ncbi.nlm.nih.gov) - NCBI 序列比对
- [TaxonKit](https://github.com/shenwei356/taxonkit) - 分类学信息处理